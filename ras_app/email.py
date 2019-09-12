import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from ras_app.models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
from collections import defaultdict

from notifications_python_client.notifications import NotificationsAPIClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Running')
        # send_approvals_email()


# This is used to send e-mails to a test address if set in settings.
def get_test_email_addreess(email):
    # import pdb; pdb.set_trace()
    if settings.EMAIL_TEST_ADDRESS:
        emailaddr = settings.EMAIL_TEST_ADDRESS
    elif settings.EMAIL_TEST_SMOKE == 'True':
        emailaddr = settings.EMAIL_TEST_NOTIFY_ADDRESS
    else:
        emailaddr = email
    return emailaddr


def get_username(user_email):
    response = requests.get(
        'https://sso.trade.gov.uk/api/v1/user/introspect/',
        params={'email': user_email},
        headers={'Authorization': f'Bearer {settings.SSO_INTROS_TOKEN}'})

    if response.status_code == requests.codes.ok:
        user_data = response.json()
        first_name = user_data['first_name']
        last_name = user_data['last_name']
    else:
        print("User not in staff sso db.")
    person = first_name + ' ' + last_name
    return person


def get_approval_details(request_id):
    items_to_approve = RequestItem.objects.values_list(
        'services__service_name', flat=True).filter(request_id=request_id)
    items_to_approve_as_lst = []
    for x in items_to_approve:
        if x in ['google analytics', 'github', 'ukgov paas']:
            items_to_approve_as_lst.append(
                x + ' - ' + RequestItem.objects.get(
                    request_id=request_id, services__service_name=x).additional_info)
        else:
            items_to_approve_as_lst.append(x)
    request = Request.objects.get(id=request_id)
    requestor = request.requestor
    user = request.user_email
    reason = request.reason
    approver = Approver.objects.get(id=(request.approver_id)).email
    team_name = User.objects.get(email=user).team.team_name
    if Teams.objects.get(team_name=team_name).sc:
        sc = 'Access to this team required SC clearance, please ensure clearance has been granted.'
    else:
        sc = ''
    return approver, requestor, user, reason, team_name, items_to_approve_as_lst, sc


def send_approvals_email(request_id):

    print('Sending mail')
    approver, requestor, user, reason, team_name, items_to_approve, sc = get_approval_details(
        request_id)
    print(approver)
    approval_url = 'https://' + settings.DOMAIN_NAME + '/access-requests/'
    attention_for = get_username(approver)
    requestor = get_username(requestor)
    user = get_username(user)
    emailaddr = get_test_email_addreess(approver)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=emailaddr,
        template_id=settings.EMAIL_UUID,
        personalisation={
            'name': attention_for,
            'sc': sc,
            'requester': requestor,
            'user': user,
            'reason': reason,
            'team': team_name,
            'services': items_to_approve,
            'url': approval_url
        }
    )


def send_end_user_email(request_id):
    print('Sending mail')
    approver, requestor, user, reason, team_name, items_to_approve, sc = get_approval_details(
        request_id)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/request-status/'
    attention_for = get_username(user)
    requestor = get_username(requestor)
    approver = get_username(approver)
    emailaddr = get_test_email_addreess(user)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=emailaddr,
        template_id=settings.EMAIL_ENDUSER_UUID,
        personalisation={
            'name': attention_for,
            'requester': requestor,
            'approver': approver,
            'request_id': request_id,
            'ras_url': ras_url,
            'services': items_to_approve
        }
    )


def send_requestor_email(request_id):
    print('Sending mail')
    if Request.objects.get(id=request_id).rejected:
        status = 'has been rejected'
        rejection_reason = ', because: ' + Request.objects.get(
            id=request_id).rejected_reason
    else:
        status = 'is being reviewed'
        rejection_reason = '.'

    approver, requestor, user, reason, team_name, items_to_approve, sc = get_approval_details(
        request_id)
    attention_for = get_username(requestor)
    approver = get_username(approver)
    user = get_username(user)
    emailaddr = get_test_email_addreess(requestor)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=emailaddr,
        template_id=settings.EMAIL_REQUESTOR_UUID,
        personalisation={
            'name': attention_for,
            'approver': approver,
            'request_id': request_id,
            'user': user,
            'status': status,
            'services': items_to_approve,
            'rejection_reason': rejection_reason
        }
    )


def send_accounts_creator_email(request_id):
    print('Sending mail')
    request_approve = RequestItem.objects.values_list('services_id').filter(
        request_id__in=request_id)
    creators_id = AccountsCreator.objects.values_list('email', flat=True).filter(
        services__in=request_approve)
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/action-requests/'

    for creator in set(creators_id):
        print('emailing: ')
        print(creator)
        attention_for = get_username(creator)
        emailaddr = get_test_email_addreess(creator)

        notifications_client.send_email_notification(
            email_address=emailaddr,
            template_id=settings.EMAIL_ACTIVATE_UUID,
            personalisation={
                'name': attention_for,
                'ras_url': ras_url
            }
        )


def send_completed_email(completed_tasks):
    print('Sending mail')
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    out = defaultdict(list)
    for item in completed_tasks:
        service_str = item['services__service_name'] + \
            ', link to docs: ' + \
            Services.objects.get(service_name=item['services__service_name']).service_docs + \
            ', service url: ' + \
            Services.objects.get(service_name=item['services__service_name']).service_url
        out[item['request_id']].append(service_str)

    for x in out:
        confirmation_user = Request.objects.get(id=x).user_email
        confirmation_requestor = Request.objects.get(id=x).requestor

        if out[x][0].partition(',')[0] in ['google analytics', 'github', 'ukgov paas']:
            services = '[' + out[x][0] + ' - ' + RequestItem.objects.get(
                request_id=x, services__service_name=out[x][0]).additional_info + ']'
        else:
            services = out[x]

        attention_for = get_username(confirmation_user)
        emailaddr = get_test_email_addreess(confirmation_user)

        notifications_client.send_email_notification(
            email_address=emailaddr,
            template_id=settings.EMAIL_COMPLETED_UUID,
            personalisation={
                'who_got_access': 'You have',
                'name': attention_for,
                'services': services
            }
        )

        if confirmation_requestor != confirmation_user:
            attention_for = get_username(confirmation_requestor)
            emailaddr = get_test_email_addreess(confirmation_requestor)
            user_given_access = get_username(confirmation_user)

            notifications_client.send_email_notification(
                email_address=emailaddr,
                template_id=settings.EMAIL_COMPLETED_UUID,
                personalisation={
                    'who_got_access': user_given_access + ' has',
                    'name': attention_for,
                    'services': services})


def send_accounts_creator_close_email(creator, offboard, services):
    print('Sending mail to', creator)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    attention_for = get_username(creator)
    offboard = get_username(offboard)
    emailaddr = get_test_email_addreess(creator)

    notifications_client.send_email_notification(
        email_address=emailaddr,
        template_id=settings.EMAIL_OFFBOARD_UUID,
        personalisation={
            'creator': attention_for,
            'offboard': offboard,
            'services': services
        }
    )

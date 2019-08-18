from django.core.management.base import BaseCommand
from django.conf import settings
from ras_app.models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
from collections import defaultdict

from notifications_python_client.notifications import NotificationsAPIClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Running')
        # send_approvals_email()


def get_username(user_email):
    first_name = User.objects.get(email=user_email).first_name
    last_name = User.objects.get(email=user_email).last_name
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
    approver = Approver.objects.get(id=(request.approver_id)).email
    team_name = User.objects.get(email=user).team.team_name
    if Teams.objects.get(team_name=team_name).sc:
        sc = 'Access to this team required SC clearance, please ensure clearance has been granted.'
    else:
        sc = ''
    return approver, requestor, user, team_name, items_to_approve_as_lst, sc


def send_approvals_email(request_id):
    print('Sending mail')
    approver, requestor, user, team_name, items_to_approve, sc = get_approval_details(request_id)
    print(approver)
    approval_url = 'https://' + settings.DOMAIN_NAME + '/access-requests/'
    attention_for = get_username(approver)
    requestor = get_username(requestor)
    user = get_username(user)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    # ###Comment out whilst testing
    # notifications_client.send_email_notification(
    #     email_address=approver,
    #     template_id=settings.EMAIL_UUID,
    #     personalisation={
    #         'name': attention_for,
    #         'sc': sc,
    #         'requester': requestor,
    #         'user': user,
    #         'team': team_name,
    #         'services': items_to_approve,
    #         'url': approval_url
    #     }
    # )


def send_end_user_email(request_id):
    print('Sending mail')
    approver, requestor, user, team_name, items_to_approve, sc = get_approval_details(request_id)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/request-status/'
    attention_for = get_username(user)
    requestor = get_username(requestor)
    approver = get_username(approver)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    # ###Comment out whilst testing
    # notifications_client.send_email_notification(
    #     email_address=user,
    #     template_id=settings.EMAIL_ENDUSER_UUID,
    #     personalisation={
    #         'name': attention_for,
    #         'requester': requestor,
    #         'approver': approver,
    #         'request_id': request_id,
    #         'ras_url': ras_url,
    #         'services': items_to_approve
    #     }
    # )


def send_requestor_email(request_id):
    print('Sending mail')
    if Request.objects.get(id=request_id).rejected:
        status = 'rejected'
        rejection_reason = 'Your request was rejected because: ' + Request.objects.get(
            id=request_id).rejected_reason
    else:
        status = 'submitted'
        rejection_reason = ''

    approver, requestor, user, team_name, items_to_approve, sc = get_approval_details(request_id)
    attention_for = get_username(requestor)
    approver = get_username(approver)
    user = get_username(user)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    # ###Comment out whilst testing
    # notifications_client.send_email_notification(
    #     email_address=requestor,
    #     template_id=settings.EMAIL_REQUESTOR_UUID,
    #     personalisation={
    #         'name': attention_for,
    #         'approver': approver,
    #         'request_id': request_id,
    #         'user': user,
    #         'status': status,
    #         'services': items_to_approve,
    #         'rejection_reason': rejection_reason
    #     }
    # )


def send_accounts_creator_email(request_id):
    print('Sending mail')
    request_approve = RequestItem.objects.values_list('services_id').filter(
        request_id__in=request_id)
    creators_id = AccountsCreator.objects.values_list('email', flat=True).filter(
        services__in=request_approve)
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/action-requests/'

    for x in set(creators_id):
        print('emailing: ')
        print(x)

        attention_for = get_username(x)
        # ###Comment out whilst testing
        # notifications_client.send_email_notification(
        #     email_address=x,
        #     template_id=settings.EMAIL_ACTIVATE_UUID,
        #     personalisation={
        #         'name': attention_for,
        #         'ras_url': ras_url
        #     }
        # )


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
        # ###Comment out whilst testing
        # notifications_client.send_email_notification(
        #     email_address=confirmation_user,
        #     template_id=settings.EMAIL_COMPLETED_UUID,
        #     personalisation={
        #         'who_got_access': 'You have',
        #         'name': attention_for,
        #         'services': services
        #     }
        # )

        if confirmation_requestor != confirmation_user:
            attention_for = get_username(confirmation_requestor)

            # notifications_client.send_email_notification(
            #     email_address=confirmation_requestor,
            #     template_id=settings.EMAIL_COMPLETED_UUID,
            #     personalisation={
            #         'who_got_access': attention_for + ' has',
            #         'name': attention_for,
            #         'services': services})


def send_accounts_creator_close_email(creator, offboard, services):
    print('Sending mail to', creator)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    attention_for = get_username(creator)
    offboard = get_username(offboard)

    # notifications_client.send_email_notification(
    #     email_address=creator,
    #     template_id=settings.EMAIL_OFFBOARD_UUID,
    #     personalisation={
    #         'creator': attention_for,
    #         'offboard': offboard,
    #         'services': services
    #         #'end_date': end_date
    #     }
    # )

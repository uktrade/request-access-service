from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ras_app.models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
from collections import defaultdict

from notifications_python_client.notifications import NotificationsAPIClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')
        #send_approvals_email()


def get_approval_details(request_id):
    #import pdb; pdb.set_trace()
    rejected_url = ''
    services_required = []
    items_to_approve = RequestItem.objects.values_list('services__service_name', flat=True).filter(request_id=request_id)
    items_to_approve_as_lst = []
    for x in items_to_approve:
        if x in ['google analytics', 'github']:
            #import pdb; pdb.set_trace()
            items_to_approve_as_lst.append(x + ' - ' + RequestItem.objects.get(request_id=request_id,services__service_name=x).additional_info)
        else:
            items_to_approve_as_lst.append(x)

    request = Request.objects.get(id=request_id)
    requester = request.requestor
    user = request.user_email
    #import pdb; pdb.set_trace()
    team_name = User.objects.get(email=user).team.team_name
    if Teams.objects.get(team_name=team_name).sc:
        sc = 'Access to this team required SC clearance, please ensure clearance has been granted.'
    else:
        sc = ''

    return requester, user, team_name, items_to_approve_as_lst, sc


def send_approvals_email(request_id, approver):
    print ('Sending mail')
    print (approver)
    #import pdb; pdb.set_trace()
    requester, user, team_name, items_to_approve, sc = get_approval_details(request_id)
    #items_to_approve_as_lst = ', '.join(items_to_approve)
    approval_url = 'https://' + settings.DOMAIN_NAME + '/access-requests/'


    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=approver,
        template_id=settings.EMAIL_UUID,
        personalisation={
            'name': approver,
            'sc': sc,
            'requester': requester,
            'user': user,
            'team': team_name,
            'services': items_to_approve,
            'url': approval_url
        }
    )


def send_requester_email(request_id, approver, rejection_reason):
    print ('Sending mail')
    #print (request_id, requestor, rejection_reason)
    #import pdb; pdb.set_trace()
    if rejection_reason:
        status = 'rejected'
        #rejection_reason = 'Your request was rejected because: ' + rejection_reason
    else:
        status = 'submitted'

    requester, user, team_name, items_to_approve, sc = get_approval_details(request_id)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=requester,
        template_id=settings.EMAIL_REQUESTOR_UUID,
        personalisation={
            'name': requester,
            'approver': approver,
            'request_id': request_id,
            'user': user,
            'status': status,
            'services': items_to_approve,
            'rejection_reason': rejection_reason
        }
    )

def send_end_user_email(request_id, approver):
    print ('Sending mail')
    #print (request_id, requestor, rejection_reason)
    #import pdb; pdb.set_trace()

    requester, user, team_name, items_to_approve, sc = get_approval_details(request_id)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/request-status/'

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=user,
        template_id=settings.EMAIL_ENDUSER_UUID,
        personalisation={
            'name': user,
            'requester': requester,
            'approver': approver,
            'request_id': request_id,
            'ras_url': ras_url,
            'services': items_to_approve
        }
    )

def send_accounts_creator_email(request_id):
    print ('Sending mail')
    #import pdb; pdb.set_trace()
    request_approve = RequestItem.objects.values_list('services_id').filter(request_id__in=request_id)
    creators_id = AccountsCreator.objects.values_list('email', flat=True).filter(services__in=request_approve)
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    ras_url = 'https://' + settings.DOMAIN_NAME + '/action-requests/'

    for x in set(creators_id):
        print ('emailing: ')
        print (x)


        notifications_client.send_email_notification(
            email_address=x,
            template_id=settings.EMAIL_ACTIVATE_UUID,
            personalisation={
                'name': x,
                'ras_url': ras_url
            }
        )


def send_completed_email(completed_tasks):
    print ('Sending mail')
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    out = defaultdict(list)
    #import pdb; pdb.set_trace()
    for item in completed_tasks:
        out[item['request_id']].append(item['services__service_name'])

    for x in out:

        confirmation_user = Request.objects.get(id=x).user_email
        confirmation_requestor = Request.objects.get(id=x).requestor

        if out[x][0] in ['google analytics', 'github']:
            services = '[' + out[x][0] + ' - ' + RequestItem.objects.get(request_id=x, services__service_name=out[x][0]).additional_info + ']'
        else:
            services = out[x]

        notifications_client.send_email_notification(
            email_address=confirmation_user,
            template_id=settings.EMAIL_COMPLETED_UUID,
            personalisation={
                'who_got_access': 'You have',
                'name': confirmation_user,
                'services': services
            }
        )

        if confirmation_requestor != confirmation_user:
            notifications_client.send_email_notification(
            email_address=confirmation_requestor,
            template_id=settings.EMAIL_COMPLETED_UUID,
            personalisation={
                'who_got_access': confirmation_requestor + ' has',
                'name': confirmation_requestor,
                'services': services
            }
        )


def send_accounts_creator_close_email(creator, offboard, services, end_date):
    print ('Sending mail to', creator)
    #import pdb; pdb.set_trace()
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)

    notifications_client.send_email_notification(
        email_address=creator,
        template_id=settings.EMAIL_OFFBOARD_UUID,
        personalisation={
            'creator': creator,
            'offboard': offboard,
            'services': services,
            'end_date': end_date
        }
    )

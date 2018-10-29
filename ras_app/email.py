from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ras_app.models import Approver, Services, User, Request, RequestItem

from notifications_python_client.notifications import NotificationsAPIClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')
        #send_approvals_email()

def get_approval_details(token, approval_url):

    rejected_url = ''
    services_required = []
    request_to_approve = Request.objects.get(token=token)
    #import pdb; pdb.set_trace()
    services_required_id = RequestItem.objects.values_list('services', flat=True).filter(request=request_to_approve)
    for z in services_required_id:
        services_required.append(Services.objects.get(id=z).service_name)

    approval_url  += '\n' + \
        'Requestor: ' + request_to_approve.requestor + '\n' + \
        'Who needs access: ' + request_to_approve.user_email + '\n' + \
        'Access to: ' + ', '.join(services_required) + '\n' + \
        'Reason: ' + request_to_approve.reason + '\n' + \
        'Link to approve: ' + 'https://' + settings.DOMAIN_NAME + '/activate/' + token + '/' + '\n' + \
        'Link to reject: ' + 'https://' + settings.DOMAIN_NAME + '/reject/' + token + '/' + '\n'

    return approval_url


def send_approvals_email(token, approver):
    print ('Sending mail')
    print (approver)
    #import pdb; pdb.set_trace()
    approval_url = ''
    if not isinstance(token, str):
        for x in token:
            approval_url = get_approval_details(x, approval_url)

    else:
        approval_url = get_approval_details(token, '')


    print (approval_url)

    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=approver,
        template_id=settings.EMAIL_UUID,
        personalisation={
            'name': approver,
            'auth_link': approval_url
        }
    )

def send_requester_email(request_id, requestor, rejection_reason):
    print ('Sending mail')
    print (request_id, requestor, rejection_reason)
    #import pdb; pdb.set_trace()
    if rejection_reason:
        status = 'rejected'
        rejection_reason = 'Your request was rejected because: ' + rejection_reason
    else:
        status = 'submitted'
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=requestor,
        template_id=settings.EMAIL_REQUESTOR_UUID,
        personalisation={
            'name': requestor,
            'request_id': request_id,
            'status': status,
            'rejection_reason': rejection_reason
        }
    )

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from notifications_python_client.notifications import NotificationsAPIClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')
        #send_approvals_email()

def send_approvals_email(token, approver):
    print ('Sending mail')
    print (approver)
    #import pdb; pdb.set_trace()
    approval_url = ''
    rejeced_url = ''

    for x in token:
        #activation_url  += '/activate/' + x + '/'

        approval_url  += '<br>%0D%0A' + settings.DOMAIN_NAME + '/activate/' + x + '/'
        rejeced_url += '<br>%0D%0A' + settings.DOMAIN_NAME + '/reject/' + x + '/'

    print (approval_url)
    print (rejeced_url)
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address=approver,
        template_id=settings.EMAIL_UUID,
        personalisation={
            'name': approver,
            'auth_link': approval_url,
            'reject_link': rejeced_url
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

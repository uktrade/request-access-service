from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from notifications_python_client.notifications import NotificationsAPIClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')
        
        magic_link()

        #send_approvals_email()

def magic_link():
    


def send_approvals_email():
    print ('Sending mail')
    notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    notifications_client.send_email_notification(
        email_address='jayesh.patel@digital.trade.gov.uk',
        template_id=settings.EMAIL_UUID,
        personalisation={
            'name': 'Jayesh',
            'auth_link': 'google.co.uk'
        }
    )
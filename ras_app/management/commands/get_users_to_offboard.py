from django.core.management.base import BaseCommand, CommandError

import subprocess
import time, os, urllib.request, json
import datetime as dt
import requests, uuid, hmac, hashlib, base64
from ras_app.models import Approver, Services, User, Request, RequestItem, AccountsCreator
from ras_app.email import send_approvals_email, send_requester_email, send_accounts_creator_close_email
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')

        #import pdb; pdb.set_trace()

        users_expired = User.objects.filter(end_date__lt=dt.date.today())
        for x in users_expired:

            request_no = Request.objects.filter(user_email=x.email)
            service_no = RequestItem.objects.filter(request_id__in=request_no, completed=True).values_list('services__service_name',flat=True)
            creators_no = AccountsCreator.objects.filter(services__service_name__in=service_no).values_list('email',flat=True).distinct()
            for y in creators_no:
                print(y)
                print('Off board this person ' + x.email)
                print('Has access to: ')
                services = []
                for z in service_no:
                    if AccountsCreator.objects.filter(services__service_name=z, email=y):
                        print(z)
                        services.append(z)

                print('Contract end date: ',  x.end_date.strftime('%d %b %Y'))

                send_accounts_creator_close_email(y, x.email, services, x.end_date.strftime('%d %b %Y'))

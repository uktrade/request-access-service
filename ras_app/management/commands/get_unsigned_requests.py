from django.core.management.base import BaseCommand, CommandError

import subprocess
import time, os, urllib.request, json
import requests, uuid, hmac, hashlib, base64
from ras_app.models import Approver, Services, User, Request
from ras_app.email import send_approvals_email, send_requester_email
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

#from ras_app.models import

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')

        #import pdb; pdb.set_trace()
        #ordered_requests =  Request.objects.order_by().values('approver_id', 'id', 'token')#.distinct():

        # This section of code works, but not happy with the method need to work out a better way
        id_to_check = 0
        sorted_list = Request.objects.order_by('approver_id').values('approver_id', 'id', 'token').filter(signed_off=False, rejected=False)
        #import pdb; pdb.set_trace()
        append_token = []
        for index, obj in enumerate(sorted_list):
            if index == (len(sorted_list) - 1):
                append_token.append(sorted_list[index]['token'])
                #print (append_token)
                approver_email = Approver.objects.get(id=sorted_list[index]['approver_id'])
                send_approvals_email(append_token, str(approver_email))
                break

            elif index < (len(sorted_list) - 1):
                if sorted_list[index]['approver_id'] == sorted_list[index+1]['approver_id']:
                    #print ('Same')
                    append_token.append(sorted_list[index]['token'])# + ' http:')

                else:
                    # print ('Diff')
                    # if not append_token:
                    append_token.append(sorted_list[index]['token'])
                    # print (sorted_list[index]['token'])
                    #print (append_token)
                    approver_email = Approver.objects.get(id=sorted_list[index]['approver_id'])
                    send_approvals_email(append_token, str(approver_email))#, settings.DOMAIN_NAME)
                    append_token = []
        #print (approver)

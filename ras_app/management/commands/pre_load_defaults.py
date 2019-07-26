from django.core.management.base import BaseCommand, CommandError

import subprocess
import time, os, urllib.request, json
import datetime as dt
import requests, uuid, hmac, hashlib, base64
from ras_app.models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
from ras_app.email import send_approvals_email, send_requester_email, send_accounts_creator_close_email
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')

        with open('services.json') as f:
            data_services = json.load(f)
        #import pdb; pdb.set_trace()
        print ('Populating Services:')
        for value in data_services['services']:

            Services.objects.update_or_create(service_name=value[0]['service_name'],
                service_url=value[1]['service_url'],
                service_docs=value[2]['service_docs'])
            print (value[0]['service_name'] + ' Added')

        with open('teams.json') as f:
            data_teams = json.load(f)
        #import pdb; pdb.set_trace()
        print ('Populating Teams:')
        for x in data_teams['teams']:
            for team, sc in x.items():
                Teams.objects.update_or_create(team_name=team, sc=sc['sc'])
                print (team + ' Added')

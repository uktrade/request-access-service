from django.core.management.base import BaseCommand, CommandError

import subprocess
import time, os, urllib.request, json
import requests, uuid, hmac, hashlib, base64

#from ras_app.models import

BASE_URL = 'https://localhost'
API_TOKEN = ''
API_SECRET = ''

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')



    def auth_request(method, path, headers=None, data=None):
        auth_timestamp = str(int(time.time()))
        auth_nonce = uuid.uuid4().hex
        auth_string = '&'.join([API_TOKEN, auth_timestamp, auth_nonce,
            method.upper(), path])
        #import pdb; pdb.set_trace()
        auth_signature = base64.b64encode(hmac.new(
            API_SECRET.encode(), auth_string.encode(), hashlib.sha256).digest())
        auth_headers = {
            'Auth-Token': API_TOKEN,
            'Auth-Timestamp': auth_timestamp,
            'Auth-Nonce': auth_nonce,
            'Auth-Signature': auth_signature,
        }
        if headers:
            auth_headers.update(headers)
        return getattr(requests, method.lower())(
            BASE_URL + path,
            verify=False,
            headers=auth_headers,
            data=data,
        )
    #print ((auth_request('GET', '/organization')).json())
    r = (auth_request('GET', '/user/5ba0e3b139911600015ecd20')).json()

    for lst in r:
        for key, value in lst.items():
            if key == 'email':
                print (value)
    #import pdb; pdb.set_trace()

from django.core.management.base import BaseCommand, CommandError

import subprocess
import time, os, urllib.request, json
import requests, uuid, hmac, hashlib, base64

#from ras_app.models import

class Command(BaseCommand):
    def handle(self, *args, **options):
        print ('Running')



    def unsigned_request(method, path, headers=None, data=None):
        print('finding requests')
        
    #import pdb; pdb.set_trace()

import json

from django.core.management.base import BaseCommand
from ras_app.models import Services, Teams
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Running')
        data_services = json.loads(settings.SERVICES)

        print('Populating Services:')
        for value in data_services['services']:

            Services.objects.update_or_create(
                service_name=value[0]['service_name'],
                service_url=value[1]['service_url'],
                service_docs=value[2]['service_docs'])

            print(value[0]['service_name'] + ' Added')

        data_teams = json.loads(settings.TEAMS)

        print('Populating Teams:')
        for x in data_teams['teams']:
            for team, sc in x.items():
                Teams.objects.update_or_create(team_name=team, sc=sc['sc'])
                print(team + ' Added')

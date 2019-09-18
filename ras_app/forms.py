import json

from .models import Approver, Services, User, Request, AccountsCreator, RequestItem, Teams

from django import forms

from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets


ACCESS_CHOICES = [
    ('myeslf', 'Yes'),
    ('on_behalf', 'No, on the behalf of someone else.'), ]

ACTION_REQUESTS = [
    ('yes', 'Yes'),
    ('no', 'No'), ]


class StartForm(GOVUKForm):
    needs_access = forms.ChoiceField(
        label='Are you requesting access for yourself?',
        choices=ACCESS_CHOICES,
        widget=widgets.Select())


def get_teams_list():
    return Teams.objects.values_list('id', 'team_name').order_by('team_name')


class StaffLookupForm(GOVUKForm):
    searchname = forms.CharField(
        label='Name:',
        max_length=60,
        widget=widgets.TextInput())


class AddNewUserForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        self._chosen_staff = kwargs.pop('chosen_staff', None)
        super().__init__(*args, **kwargs)
        self.fields['team'].choices = get_teams_list()
        self.fields['user'].disabled = True
        if self._chosen_staff:
            self.fields['user'].initial = self._chosen_staff

    user = forms.CharField(
        label='Users fullname (person who needs access)',
        max_length=60,
        widget=widgets.TextInput())
    team = forms.ChoiceField(
        label='Which team:',
        choices=[],
        widget=widgets.Select())


class AccessApproverForm(GOVUKForm):
    approver = forms.CharField(
        label='Name:',
        widget=widgets.TextInput())


def get_service_list(user_email):
    # Check to see if a service has already been approved if so dont display
    if RequestItem.objects.values_list(
        'services_id', flat=True).filter(
        request_id__in=Request.objects.values_list(
            'id', flat=True).filter(
            user_email=user_email), completed=True):

        approved_items = RequestItem.objects.values_list('services_id', flat=True).filter(
            request_id__in=Request.objects.values_list('id', flat=True).filter(
                user_email=user_email), completed=True)
        services_list = Services.objects.exclude(id__in=approved_items).values_list(
            'id',
            'service_name')
    else:
        # Get all services.
        services_list = Services.objects.values_list('id', 'service_name')
    return services_list


class ServicesRequiredForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email')
        super().__init__(*args, **kwargs)
        self.fields['services'].choices = get_service_list(user_email)

    services = forms.MultipleChoiceField(
        label='Please select the services you needs access to be give to',
        choices=[],
        widget=widgets.CheckboxSelectMultiple)


class AdditionalInfoForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services')
        super(AdditionalInfoForm, self).__init__(*args, **kwargs)
        service_objects = json.loads(services)

        for service, value in service_objects.items():
            if value == 'False' and service == 'ga':
                self.fields['ga_info'].widget = forms.HiddenInput()
                self.fields['ga_info'].required = False

            if value == 'False' and service == 'github':
                self.fields['github_info'].widget = forms.HiddenInput()
                self.fields['github_info'].required = False

            if value == 'False' and service == 'ukgovpaas':
                self.fields['ukgovpaas_info'].widget = forms.HiddenInput()
                self.fields['ukgovpaas_info'].required = False

    ga_info = forms.CharField(
        label='Please specify the Google Analytic services that is required:',
        max_length=60,
        widget=widgets.TextInput())
    github_info = forms.CharField(
        label='Enter in GitHub Username:',
        max_length=60,
        widget=widgets.TextInput())
    ukgovpaas_info = forms.CharField(
        label='Which GovPaaS Space will be required:',
        max_length=60,
        widget=widgets.TextInput())


class ReasonForm(GOVUKForm):
    reason = forms.CharField(
        label='Short description on why you need access:',
        widget=widgets.Textarea())


def get_approve_list(email):
    approve_list = []
    request_list = []

    if Request.objects.filter(approver__email=email).exclude(
            signed_off=True).exclude(rejected=True).exists():
        request_list = Request.objects.values_list('id', 'user_email').filter(
            approver__email=email).exclude(signed_off=True).exclude(rejected=True)

    for id, email in request_list:
        services_required = RequestItem.objects.values_list(
            'services__service_name', flat=True).filter(request_id=id)
        services_required_as_str = ''
        for service in services_required:
            if service in ['google analytics', 'github']:
                services_required_as_str += '[' + service + ' - ' + \
                    RequestItem.objects.get(
                        request_id=id, services__service_name=service).additional_info + '], '
            else:
                services_required_as_str += service + ', '
        user_team = User.objects.values_list('team__team_name', flat=True).filter(email=email)
        services_per_user = 'User: [' + email + \
            '] in team: [' + user_team[0] + \
            '] has requested access to services: [' + services_required_as_str + ']'

        approve_list.append([id, services_per_user])
    return approve_list


class AccessRequestsForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        email = kwargs.pop('email')
        super().__init__(*args, **kwargs)

        self.fields['approve'].choices = get_approve_list(email)
        self.fields['approve'].required = False
        self.fields['reject'].choices = get_approve_list(email)
        self.fields['reject'].required = False

    approve = forms.MultipleChoiceField(
        label='Check which to approve',
        choices=[],
        widget=widgets.CheckboxSelectMultiple)
    reject = forms.MultipleChoiceField(
        label='Check which to reject',
        choices=[],
        widget=widgets.CheckboxSelectMultiple)


def action_rejected_form_factory(rejected_ids, post=None):
    form_list = []
    reject = rejected_ids.split(',')
    for id in reject:
        form_list.append(RejectedReasonForm(post, id=id, prefix='id_{}'.format(id)))
    return form_list


class RejectedReasonForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        self._rejected_id = kwargs.pop('id', None)
        super().__init__(*args, **kwargs)

        services_required = ', '.join(RequestItem.objects.values_list(
            'services__service_name', flat=True).filter(request_id=self._rejected_id))
        rejected_user = Request.objects.get(id=self._rejected_id).user_email
        rejected_reason = "[" + \
            rejected_user + \
            "] from team [" + \
            User.objects.get(email=rejected_user).team.team_name + \
            "] wants access to [" + \
            services_required + \
            "]; please enter the reason for rejection:"
        self.fields['rejected_reason'].label = rejected_reason
        self.fields['rejected_reason'].label_suffix = self._rejected_id

    rejected_reason = forms.CharField(label=[], max_length=60, widget=widgets.TextInput())


def get_action_list(email):
    full_action_list = []
    full_action_list_noservice = Request.objects.values_list('id', 'user_email').filter(
        signed_off=True,
        rejected=False)
    for z, user_email in full_action_list_noservice:
        for requestitem in RequestItem.objects.filter(request_id=z, completed=False):
            full_action_list.append([requestitem.id, requestitem.services_id, user_email, str(z)])

    action_list = []
    accounts_creator_services = AccountsCreator.objects.values_list('services', flat=True).filter(
        email=email)
    for v in full_action_list:
        for y in accounts_creator_services:
            if v[1] == y:
                service_item = Services.objects.get(id=v[1]).service_name
                if service_item in ['google analytics', 'github']:
                    service_item = '[' + service_item + ' - ' + RequestItem.objects.get(
                        request_id=v[3], services__service_name=service_item).additional_info + ']'

                services_str = service_item + ' - ' + \
                    'User: [' + v[2] + \
                    '] - Request ID: [' + v[3] + \
                    '] - ' + 'Team: [' + User.objects.get(email=v[2]).team.team_name + ']'
                action_list.append([v[0], services_str])
    return action_list


class ActionRequestsForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        email = kwargs.pop('email')
        super().__init__(*args, **kwargs)
        self.fields['action'].choices = get_action_list(email)

    action = forms.MultipleChoiceField(
        label='Select the tasks which are complete and press submit so the user can be notified.',
        choices=[],
        widget=widgets.CheckboxSelectMultiple)

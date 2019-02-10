import datetime as dt
import json

from django import forms

from .models import Approver, Services, User, Request, AccountsCreator, RequestItem, Teams

from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import UserCreationForm

from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets, fields
from django.utils.translation import gettext
from django.utils.timezone import now


ACCESS_CHOICES= [
    ('myeslf', 'Yes'),
    ('behalf', 'No, on the behalf of someone else'),
    ]

ACTION_REQUESTS= [
    ('yes', 'Yes'),
    ('no', 'No'),
    ]

class UserForm(GOVUKForm):
    needs_access = forms.ChoiceField(label='Are you requesting access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())


def get_teams_list():
    #import pdb; pdb.set_trace()
    return Teams.objects.values_list('id', 'team_name').order_by('team_name')

class AddSelfForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        #behalf_status = kwargs.pop('behalf')
        super().__init__(*args, **kwargs)
        self.fields['team'].choices = get_teams_list()

    end_date = fields.SplitDateField(
        label='End Date of Contract',
        min_year=dt.date.today().year,
        max_year=dt.date.today().year + 10,
    )
    team = forms.ChoiceField(label='Which team:', choices=[], widget=widgets.Select())

class UserEmailForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        #behalf_status = kwargs.pop('behalf')
        super().__init__(*args, **kwargs)
        self.fields['team'].choices = get_teams_list()

    user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())
    team = forms.ChoiceField(label='Which team:', choices=[], widget=widgets.Select())

class UserEndForm(GOVUKForm):
    #user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())
    firstname = forms.CharField(label='Users Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Users Surname', max_length=60, required=False, widget=widgets.TextInput())
    #end_date = SplitDateFieldsWTF()
    end_date = fields.SplitDateField(
        label='End Date of Contract',
        min_year=dt.date.today().year,
        max_year=dt.date.today().year + 10,
    )

    # def __init__(self, *args, **kwargs):
    #     #import pdb; pdb.set_trace()
    #     behalf = kwargs.pop('behalf')
    #     super(UserEndForm, self).__init__(*args, **kwargs)
    #     if behalf == 'False':
    #         #self.fields['user_email'].widget = forms.HiddenInput()
    #         self.fields['firstname'].widget = forms.HiddenInput()
    #         self.fields['surname'].widget = forms.HiddenInput()
    #         #self.fields['user_email'].required = False
    #         self.fields['firstname'].required = False
    #         self.fields['surname'].required = False

        #import pdb; pdb.set_trace()
    def clean_end_date(self):
        #import pdb; pdb.set_trace()
        date = self.cleaned_data['end_date']
        if date and date < dt.date.today():
            raise forms.ValidationError('The date cannot be in the past')
        return date


class AdditionalInfoForm(GOVUKForm):
    #services_list = get_service_list
    #import pdb; pdb.set_trace()
    ga_info = forms.CharField(label='List GA access', max_length=60, widget=widgets.TextInput())
    github_info = forms.CharField(label='GitHub Username', max_length=60, widget=widgets.TextInput())

    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        services = kwargs.pop('services')
        super(AdditionalInfoForm, self).__init__(*args, **kwargs)

        service_objects = json.loads(services)
        # for service, value in services.items():
        #     print (value)

        for service, value in service_objects.items():
            if value == 'False' and service == 'ga':
                self.fields['ga_info'].widget = forms.HiddenInput()
                self.fields['ga_info'].required = False

            if value == 'False' and service == 'github':
                self.fields['github_info'].widget = forms.HiddenInput()
                self.fields['github_info'].required = False


        # if service == 'google analytics':
        #     #self.fields['user_email'].widget = forms.HiddenInput()
        #     self.fields['additional_info'].widget = forms.HiddenInput()
        #     self.fields['surname'].widget = forms.HiddenInput()
        #     #self.fields['user_email'].required = False
        #     self.fields['firstname'].required = False
        #     self.fields['surname'].required = False


def get_action_list(email):

    full_action_list=[]
    full_action_list_noservice = Request.objects.values_list('id', 'user_email').filter(signed_off=True, rejected=False)
    #import pdb; pdb.set_trace()
    for z, user_email in full_action_list_noservice:

        for requestitem in RequestItem.objects.filter(request_id=z, completed=False):
            #full_action_list.append([requestitem.id, Services.objects.get(id=requestitem.services_id).service_name  + ' - ' + user_email + ' - ' + str(z)])
            full_action_list.append([requestitem.id, requestitem.services_id, user_email, str(z)])


    complete_list = []
    action_list = []

    accounts_creator_services = AccountsCreator.objects.values_list('services', flat=True).filter(email=email)
    for v in full_action_list:
        for y in accounts_creator_services:
            if v[1] == y:
                #import pdb; pdb.set_trace()
                service_item = Services.objects.get(id=v[1]).service_name
                if service_item in ['google analytics', 'github']:
                    service_item = '[' + service_item + ' - ' + RequestItem.objects.get(request_id=v[3], services__service_name=service_item).additional_info + ']'

                action_list.append([v[0],
                service_item
                + ' - ' + 'User: ['
                + v[2] + '] - Request ID: ['
                + v[3]
                + '] - ' + 'Team: [' + User.objects.get(email=v[2]).team.team_name  + ']'#Teams.objects.get(id=User.objects.get(email=v[2]).team_id).team_name
                ])
    #import pdb; pdb.set_trace()
    #
    # for y, username, request_id in action_list:
    #     complete_list.append([str(y), (Services.objects.get(id=y).service_name + ' - ' + username + ' - ' + str(request_id))])
    #import pdb; pdb.set_trace()
    return action_list

class ActionRequestsForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        email = kwargs.pop('email')
        super().__init__(*args, **kwargs)
        self.fields['action'].choices = get_action_list(email)

    #access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))
    action = forms.MultipleChoiceField(label='Check which is completed', choices=[], widget=widgets.CheckboxSelectMultiple)


def get_approver_list(email_exclude, behalf_status):
    #import pdb; pdb.set_trace()
    # if behalf_status == 'True':
    #     email_exclude = ''

    return Approver.objects.values_list('id', 'email').exclude(email = email_exclude)


class AccessReasonForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        email_exclude = kwargs.pop('user_email')
        behalf_status = kwargs.pop('behalf')
        super().__init__(*args, **kwargs)
        self.fields['approver'].choices = get_approver_list(email_exclude, behalf_status)
        #self.fields['team'].choices = get_teams_list()

    #approver_list = get_approver_list
    reason = forms.CharField(label='Short description on why you need access:', widget=widgets.Textarea())
    #team = forms.ChoiceField(label='Which team:', choices=[], widget=widgets.Select())
    approver = forms.ChoiceField(label='Person who will approve access:', choices=[], widget=widgets.Select())

# def action_request_form_factory(post=None):
#     forms = []
#     for item in ['a', 'b', 'c']:
#          forms.append(DeactivateForm(prefix=item, post=post))
#
#     return forms


def get_deactivate_list(email, user_found):
    action_list = []
    #import pdb; pdb.set_trace()
    request_items = RequestItem.objects.filter(request__user_email=user_found, completed=True)
    if email in AccountsCreator.objects.filter(services__in=request_items.values_list('services',flat=True)).values_list('email',flat=True):
        #import pdb; pdb.set_trace()
        action_list.append(request_items.values_list('id', 'services__service_name'))

    complete_list = []
    #import pdb; pdb.set_trace()
    for z in action_list:
        for y in z:
            complete_list.append(y)

    return complete_list

class DeactivateForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        self._user = kwargs.pop('user', None)
        self._creator_email = kwargs.pop('creator_email', None)
        super().__init__(*args, **kwargs)
        #super(my_form, self).__init__(*args, **kwargs)

        self.fields['deactivate'].choices = get_deactivate_list(self._creator_email,  self._user.email)
        self.fields['deactivate'].label =  self._user.email
        self.fields['deactivate'].required = False


    deactivate = forms.MultipleChoiceField(label=[], choices=[], widget=widgets.CheckboxSelectMultiple)


def action_request_form_factory(creator_email, post=None):
   form_list = []
   #import pdb; pdb.set_trace()
   for user in User.objects.filter(end_date__lt=dt.date.today(), request_id__isnull=False):
       form_list.append(DeactivateForm(post, creator_email=creator_email, user=user, prefix='user_{}'.format(user.id)))
   return form_list


def get_approve_list(email):
    #import pdb; pdb.set_trace()
    # if behalf_status == 'True':
    #     email_exclude = ''
    approve_list = []

    request_list = Request.objects.values_list('id', 'user_email').filter(approver_id=Approver.objects.get(email=email).id).exclude(signed_off=True).exclude(rejected=True)
    for id, email in request_list:
        services_required = RequestItem.objects.values_list('services__service_name', flat=True).filter(request_id=id)
        services_required_as_str = ''
        for x in services_required:
            if x in ['google analytics', 'github']:
                services_required_as_str+= '['+ x + ' - ' + RequestItem.objects.get(request_id=id, services__service_name=x).additional_info + '], '
            else:
                services_required_as_str+= x + ', '
        user_team = User.objects.values_list('team__team_name', flat=True).filter(email=email)
        services_per_user = 'User: [' + email + '] in team: [' + user_team[0] + '] has requested access to services: [' + services_required_as_str + ']'

        approve_list.append([id, services_per_user])


    return approve_list

class ApproveForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        email = kwargs.pop('email')
        super().__init__(*args, **kwargs)

        self.fields['approve'].choices = get_approve_list(email)
        self.fields['approve'].required = False
        self.fields['reject'].choices = get_approve_list(email)
        self.fields['reject'].required = False

    #access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))
    approve = forms.MultipleChoiceField(label='Check which to approve', choices=[], widget=widgets.CheckboxSelectMultiple)
    reject = forms.MultipleChoiceField(label='Check which to reject', choices=[], widget=widgets.CheckboxSelectMultiple)


def get_approver_list(email_exclude, behalf_status):
    #import pdb; pdb.set_trace()
    # if behalf_status == 'True':
    #     email_exclude = ''

    return Approver.objects.values_list('id', 'email').exclude(email = email_exclude)


def get_service_list(user_email):

    #approved_items = Request.objects.values_list('id', flat=True).filter(user_email=user_email, completed=True)
    approved_requests = Request.objects.values_list('id', flat=True).filter(user_email=user_email)
    approved_items = RequestItem.objects.values_list('services_id', flat=True).filter(request_id__in=approved_requests, completed=True)
    # Get services not already assigned.

    services_list = Services.objects.exclude(id__in=approved_items).values_list()

    return services_list


class RejectedReasonForm(GOVUKForm):
    #import pdb; pdb.set_trace()

    def __init__(self, *args, **kwargs):
        self._rejected_id = kwargs.pop('id', None)
        super().__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        #services_required_as_str = []
        services_required = ', '.join(RequestItem.objects.values_list('services__service_name', flat=True).filter(request_id=self._rejected_id))
        # for x in services_required:
        #     services_required_as_str.append(x)
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


def action_rejected_form_factory(rejected_ids, post=None):
   form_list = []
   #import pdb; pdb.set_trace()
   reject = rejected_ids.split(',')
   for id in reject:

       form_list.append(RejectedReasonForm(post, id=id, prefix='id_{}'.format(id)))
   return form_list


class UserDetailsForm(GOVUKForm):
    #services_list = get_service_list
    #import pdb; pdb.set_trace()
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=[], widget=widgets.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email')

        super().__init__(*args, **kwargs)
        self.fields['services'].choices = get_service_list(user_email)

class RejectForm(GOVUKForm):
    rejected_reason = forms.CharField(label='Short description on why you have rejected access', widget=widgets.Textarea())


# def get_status_list():
#     #import pdb; pdb.set_trace()
#     return Teams.objects.values_list('id', 'team_name').order_by('team_name')
#
# class RequestStatusForm(GOVUKForm):
#     def __init__(self, *args, **kwargs):
#         #behalf_status = kwargs.pop('behalf')
#         super().__init__(*args, **kwargs)
#         self.fields['team'].choices = get_status_list()
#
#     team = forms.ChoiceField(label='Which team:', choices=[], widget=widgets.Select())
#

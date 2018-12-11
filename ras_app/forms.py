from django import forms
from .models import Approver, Services, User, Request, AccountsCreator, RequestItem#, RequestServices

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

##Cant use GovUK field as there you cannot use specify a year greater then the current.
class YearFieldWTF(fields.YearField):
    def __init__(self, era_boundary=None, **kwargs):
        #import pdb; pdb.set_trace()
        self.current_year = now().year
        self.max_year = self.current_year + 10
        self.century = 100 * (self.max_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.max_year - self.century - 10
        self.era_boundary = era_boundary
        bounds_error = gettext('Year should be between %(current_year)s and %(max_year)s.') % {
            'current_year': self.current_year, 'max_year': self.max_year
        }
        options = {
            'min_value': 2018,
            'max_value': self.max_year,
            'error_messages': {
                'min_value': bounds_error,
                'max_value': bounds_error,
                'invalid': gettext('Enter year as a number.'),
            }
        }
        options.update(kwargs)
        #import pdb; pdb.set_trace()

        forms.IntegerField.__init__(self, **options)

class SplitDateFieldsWTF(fields.SplitDateField):
   def __init__(self, *args, **kwargs):
       day_bounds_error = gettext('Day should be between 1 and 31.')
       month_bounds_error = gettext('Month should be between 1 and 12.')

       self.fields = [
           forms.IntegerField(min_value=1, max_value=31, error_messages={
               'min_value': day_bounds_error,
               'max_value': day_bounds_error,
               'invalid': gettext('Enter day as a number.')
           }),
           forms.IntegerField(min_value=1, max_value=12, error_messages={
               'min_value': month_bounds_error,
               'max_value': month_bounds_error,
               'invalid': gettext('Enter month as a number.')
           }),
           YearFieldWTF(),
       ]
       #import pdb; pdb.set_trace()

       forms.MultiValueField.__init__(self, self.fields, *args, **kwargs)



class UserForm(GOVUKForm):
    needs_access = forms.ChoiceField(label='Are you requesting access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())


class UserEmailForm(GOVUKForm):
    user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())


class UserEndForm(GOVUKForm):
    #user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())
    firstname = forms.CharField(label='Users Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Users Surname', max_length=60, required=False, widget=widgets.TextInput())
    end_date = SplitDateFieldsWTF()#label='End Date of Contract')
    #end_date = fields.SplitDateField(label='End Date of Contract')

    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        behalf = kwargs.pop('behalf')
        super(UserEndForm, self).__init__(*args, **kwargs)
        if behalf == 'False':
            #self.fields['user_email'].widget = forms.HiddenInput()
            self.fields['firstname'].widget = forms.HiddenInput()
            self.fields['surname'].widget = forms.HiddenInput()
            #self.fields['user_email'].required = False
            self.fields['firstname'].required = False
            self.fields['surname'].required = False

        #import pdb; pdb.set_trace()

def get_action_list(uuid):

    full_action_list=[]
    full_action_list_noservice = Request.objects.values_list('id', 'user_email').filter(signed_off=True, rejected=False)
    #import pdb; pdb.set_trace()
    for z, user_email in full_action_list_noservice:

        for requestitem in RequestItem.objects.filter(request_id=z, completed=False):
            #full_action_list.append([requestitem.id, Services.objects.get(id=requestitem.services_id).service_name  + ' - ' + user_email + ' - ' + str(z)])
            full_action_list.append([requestitem.id, requestitem.services_id, user_email, str(z)])


    complete_list = []
    action_list = []

    accounts_creator_services = AccountsCreator.objects.values_list('services', flat=True).filter(uuid=uuid)
    for v in full_action_list:
        for y in accounts_creator_services:
            if v[1] == y:
                action_list.append([v[0], Services.objects.get(id=v[1]).service_name + ' - ' + v[2] + ' - ' + v[3]])
    #import pdb; pdb.set_trace()
    #
    # for y, username, request_id in action_list:
    #     complete_list.append([str(y), (Services.objects.get(id=y).service_name + ' - ' + username + ' - ' + str(request_id))])
    #import pdb; pdb.set_trace()
    return action_list

class ActionRequestsForm(GOVUKForm):
    def __init__(self, *args, **kwargs):

        uuid = kwargs.pop('uid')
        super().__init__(*args, **kwargs)
        self.fields['action'].choices = get_action_list(uuid)

    #access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))
    action = forms.MultipleChoiceField(label='Check which is completed', choices=[], widget=widgets.CheckboxSelectMultiple)


def get_approver_list(email_exclude, behalf_status):
    #import pdb; pdb.set_trace()
    # if behalf_status == 'True':
    #     email_exclude = ''

    return Approver.objects.values_list('id', 'email').exclude(email = email_exclude)

class AccessReasonForm(GOVUKForm):
    def __init__(self, *args, **kwargs):
        email_exclude = kwargs.pop('email')
        behalf_status = kwargs.pop('behalf')
        super().__init__(*args, **kwargs)
        self.fields['approver'].choices = get_approver_list(email_exclude, behalf_status)

    #approver_list = get_approver_list
    reason = forms.CharField(label='Short description on why you need access', widget=widgets.Textarea())
    approver = forms.ChoiceField(label='Person who will approve access', choices=[], widget=widgets.Select())


def get_service_list():
    return Services.objects.values_list()

class UserDetailsForm(GOVUKForm):
    services_list = get_service_list
    #import pdb; pdb.set_trace()
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=services_list, widget=widgets.CheckboxSelectMultiple)

class RejectForm(GOVUKForm):
    rejected_reason = forms.CharField(label='Short description on why you have rejected access', widget=widgets.Textarea())

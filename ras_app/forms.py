from django import forms
from .models import Approver, Services, User, Request

from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import UserCreationForm

from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets, fields


ACCESS_CHOICES= [
    ('myeslf', 'Yes'),
    ('behalf', 'No, on the behalf of someone else'),
    ]

ACTION_REQUESTS= [
    ('yes', 'Yes'),
    ('no', 'No'),
    ]


class UserForm(GOVUKForm):
    needs_access= forms.ChoiceField(label='Are you requesting access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())


class UserEndForm(GOVUKForm):
    user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())
    firstname = forms.CharField(label='Users Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Users Surname', max_length=60, required=False, widget=widgets.TextInput())
    end_date = fields.SplitDateField(label='End Date of Contract')

    def __init__(self, *args, **kwargs):
        behalf = kwargs.pop('behalf')
        super(UserEndForm, self).__init__(*args, **kwargs)
        if behalf == 'False':
            self.fields['user_email'].widget = forms.HiddenInput()
            self.fields['firstname'].widget = forms.HiddenInput()
            self.fields['surname'].widget = forms.HiddenInput()
            self.fields['user_email'].required = False
            self.fields['firstname'].required = False
            self.fields['surname'].required = False


class ActionRequestsForm(GOVUKForm):
    access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))


def get_approver_list():
    return Approver.objects.values_list('id', 'email')

class AccessReasonForm(GOVUKForm):
    approver_list = get_approver_list
    reason = forms.CharField(label='Short description on why you need access', widget=widgets.Textarea())
    approver = forms.ChoiceField(label='Person who will approve access', choices=approver_list, widget=widgets.Select())

def get_service_list():
    return Services.objects.values_list()

class UserDetailsForm(GOVUKForm):
    services_list = get_service_list
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=services_list, widget=widgets.CheckboxSelectMultiple)

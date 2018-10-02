from django import forms
from .models import Approver, Services, User, Request

from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus import DatePickerInput
from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets, fields


ACCESS_CHOICES= [
    ('myeslf', 'Yes, for myself'),
    ('behalf', 'No, on behalf of someone'),
    ]

ACTION_REQUESTS= [
    ('yes', 'Yes'),
    ('no', 'No'),
    ]

# APPROVER_LIST = [
#     ('jayeshpatel', 'Jayesh Patel'),
#     ('lyndongarvey', 'Lyndon Garvey'),
#     ('bowensun', 'Bowen Sun')
# ]

class UserForm(GOVUKForm):
    #needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))
    needs_access= forms.ChoiceField(label='Is access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())


class UserEndForm(GOVUKForm):
    user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, required=False, widget=widgets.TextInput())
    firstname = forms.CharField(label='Your Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Your Surname', max_length=60, widget=widgets.TextInput())
    email = forms.CharField(label='Your E-mail', max_length=60, widget=widgets.TextInput())
    end_date = fields.SplitDateField(label='End Date of Contract')#, widget=widgets.SplitDateWidget())

    def __init__(self, *args, **kwargs):
        behalf = kwargs.pop('behalf')
        super(UserEndForm, self).__init__(*args, **kwargs)
        if behalf == 'False':
            #import pdb; pdb.set_trace()
            self.fields['user_email'].widget = forms.HiddenInput()
        else:
            self.fields['firstname'].label = 'Users Firstname'
            self.fields['surname'].label = 'Users Surname'


class ActionRequestsForm(GOVUKForm):
    access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))


class AccessReasonForm(GOVUKForm):
    approver_list = Approver.objects.values_list('id', 'email')
    reason = forms.CharField(label='Short description on why you need access', widget=widgets.Textarea())
    approver = forms.ChoiceField(label='Person who will approve access', choices=approver_list, widget=widgets.Select())


class UserDetailsForm(GOVUKForm):
    #import pdb; pdb.set_trace()
    services_list = Services.objects.values_list()#('service_name', flat=True)
    #approver_list = Approver.objects.values_list('id', 'email')
    #reason = forms.CharField(label='Short description on why you need access', widget=widgets.Textarea())
    #approver = forms.ChoiceField(label='Person who will approve access', choices=approver_list, widget=widgets.Select())
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=services_list , widget=widgets.CheckboxSelectMultiple)

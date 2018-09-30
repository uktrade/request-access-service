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

APPROVER_LIST = [
    ('jayeshpatel', 'Jayesh Patel'),
    ('lyndongarvey', 'Lyndon Garvey'),
    ('bowensun', 'Bowen Sun')
]


class UserEndForm(GOVUKForm):
    firstname = forms.CharField(label='Your Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Your Surname', max_length=60, widget=widgets.TextInput())
    end_date = fields.SplitDateField(label='End Date of Contract')#, widget=widgets.SplitDateWidget())
    # end_date = forms.DateField(
    #     widget=DatePickerInput())

class UserForm(GOVUKForm):
    #needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))
    needs_access= forms.ChoiceField(label='Is access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())

class ActionRequestsForm(GOVUKForm):
    access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))


class UserDetailsForm(GOVUKForm):
    #import pdb; pdb.set_trace()
    services_list = Services.objects.values_list()#('service_name', flat=True)
    approver_list = Approver.objects.values_list('id', 'email')

    requestor = forms.CharField(label='Your e-mail', max_length=60, widget=widgets.TextInput())
    reason = forms.CharField(label='Short description on why you need access', widget=widgets.Textarea())
    approver = forms.ChoiceField(label='Person who will approve access', choices=approver_list, widget=widgets.Select())
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=services_list , widget=widgets.CheckboxSelectMultiple)

class UserDetailsBehalfForm(GOVUKForm):
    #import pdb; pdb.set_trace()
    services_list = Services.objects.values_list()#('service_name', flat=True)
    approver_list = Approver.objects.values_list('id', 'email')

    requestor = forms.CharField(label='Your e-mail', max_length=60, widget=widgets.TextInput())
    reason = forms.CharField(label='Short description on why they need access', widget=widgets.Textarea())
    approver = forms.ChoiceField(label='Person who will approve access', choices=approver_list, widget=widgets.Select())
    services = forms.MultipleChoiceField(label='Services you needs access to', choices=services_list , widget=widgets.CheckboxSelectMultiple)
    user_email = forms.CharField(label='E-mail address of user who needs access', max_length=60, widget=widgets.TextInput())

# class UserEndForm(forms.ModelForm):
#     class Meta:
#         model = User
#         labels = {
#             'firsname': 'Your Firstname',
#             'surname': 'Your Surnname',
#             #'email': 'Your e-mail',
#             'end_date': 'End Date of Contract(dd-mm-yyyy)'

#         }
#         fields = ['firstname', 'surname', 'end_date'] #, 'email']
#         widgets = {
#             'end_date': DatePickerInput(),#format='%Y-%m-%d'), # specify date-frmat
#         }

# class UserDetailsBehalfForm(forms.ModelForm):
#     class Meta:
#         model = Request
#         labels = {
#             'requestor': 'Your e-mail',
#             'user_email': 'E-mail address of user who needs access',
#             'approver': 'Person who will approve access',
#             'services': 'User needs access to'
#         }
#         fields = ['requestor', 'reason', 'user_email', 'approver', 'services']
#
#     def __init__(self, *args, **kwargs):
#
#         super(UserDetailsBehalfForm, self).__init__(*args, **kwargs)
#
#         self.fields["services"].widget = CheckboxSelectMultiple()
#         self.fields["services"].queryset = Services.objects.all()

# class UserDetailsForm(forms.ModelForm):
#     class Meta:
#         model = Request
#         labels = {
#             'requestor': 'Your e-mail',
#             'reason': 'Short description on why you need access',
#             'approver': 'Person who will approve access',
#             'services': 'Services you needs access to'
#         }
#         exclude = ('user_email',)
#         #UserDetailsForm(initial={'user_email': 'requestor'})
#         fields = ['requestor', 'reason', 'approver', 'services']
#
#     def __init__(self, *args, **kwargs):
#
#         super(UserDetailsForm, self).__init__(*args, **kwargs)
#
#         self.fields["services"].widget = CheckboxSelectMultiple()
#         self.fields["services"].queryset = Services.objects.all()
#         self.fields["requestor"].widget = widgets.EmailInput()
#         self.fields["reason"].widget = widgets.TextInput()

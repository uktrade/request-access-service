from django import forms
from .models import Approver, Services, User, Request

from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus import DatePickerInput

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

class UserEndForm(forms.ModelForm):
    class Meta:
        model = User
        labels = {
            'end_date': 'End Date of Contract(yyyy-mm-dd)'

        }
        fields = ['firstname', 'surname', 'email', 'end_date']
        # widgets = {
        #     'end_date': DatePickerInput(format='%Y-%m-%d'), # specify date-frmat
        # }

class UserForm(forms.Form):

    needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))

class ActionRequestsForm(forms.Form):
    access_list= forms.CharField(label='Have you created all these accounts?', widget=forms.CheckboxSelectMultiple(choices=ACTION_REQUESTS))

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = Request
        labels = {
            'requestor': 'Your e-mail',
            'approver': 'Person who will approve access',
            'services': 'User needs access to'
        }
        exclude = ('user_email',)
        #UserDetailsForm(initial={'user_email': 'requestor'})
        fields = ['requestor', 'reason', 'approver', 'services']

    def __init__(self, *args, **kwargs):

        super(UserDetailsForm, self).__init__(*args, **kwargs)

        self.fields["services"].widget = CheckboxSelectMultiple()
        self.fields["services"].queryset = Services.objects.all()

class UserDetailsBehalfForm(forms.ModelForm):
    class Meta:
        model = Request
        labels = {
            'requestor': 'Your e-mail',
            'user_email': 'E-mail address of user who needs access',
            'approver': 'Person who will approve access',
            'services': 'User needs access to'
        }
        fields = ['requestor', 'reason', 'user_email', 'approver', 'services']

    def __init__(self, *args, **kwargs):

        super(UserDetailsBehalfForm, self).__init__(*args, **kwargs)

        self.fields["services"].widget = CheckboxSelectMultiple()
        self.fields["services"].queryset = Services.objects.all()

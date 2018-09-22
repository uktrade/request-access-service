from django import forms
from .models import Approver, Services, User, Request

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ACCESS_CHOICES= [
    ('myeslf', 'Yes, for myself'),
    ('behalf', 'No, on behalf of someone'),
    ]

ACCESS_LIST= [
    ('yes', 'Yes'),
    ('no', 'No'),
    ]

APPROVER_LIST = [
    ('jayeshpatel', 'Jayesh Patel'),
    ('lyndongarvey', 'Lyndon Garvey'),
    ('bowensun', 'Bowen Sun')
]

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class UserForm(forms.Form):
    # first_name= forms.CharField(label='First name', max_length=100)
    # last_name= forms.CharField(max_length=100)
    # email= forms.EmailField()
    needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))

class AccessListForm(forms.Form):
    access_list= forms.CharField(label='Sign off access?', widget=forms.CheckboxSelectMultiple(choices=ACCESS_LIST))

class UserDetailsForm(forms.Form):
    first_name= forms.CharField(label='First name', max_length=60)
    last_name= forms.CharField(max_length=60)
    email= forms.EmailField()
    approver_list= forms.CharField(label='Please select approver?', widget=forms.Select(choices=APPROVER_LIST))
    access_list= forms.CharField(label='What access do you require?', widget=forms.CheckboxSelectMultiple(choices=ACCESS_LIST))

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# class UserDetailsFormBehalf(forms.Form):
#     requestor_firstname= forms.CharField(label='Requestor First name', max_length=60)
#     requestor_surname= forms.CharField(max_length=60)
#     requestor_email= forms.EmailField()
#     user_firstname= forms.CharField(label='User First name', max_length=60)
#     user_surname= forms.CharField(max_length=60)
#     user_email= forms.EmailField()
#     enddate= forms.DateField()
#     approver_list= forms.CharField(label='Please select approver?', widget=forms.Select(choices=APPROVER_LIST))
#     access_list= forms.CharField(label='What access do you require?', widget=forms.CheckboxSelectMultiple(choices=ACCESS_LIST))

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = Request
        labels = {
            'requestor': 'Your e-mail'
        }
        exclude = ('user_email',)
        #UserDetailsForm(initial={'user_email': 'requestor'})
        fields = ['requestor', 'reason', 'approver', 'services']

class UserDetailsFormBehalf(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['requestor', 'reason', 'user_email', 'approver', 'services']
        # requestor_firstname= forms.CharField(label='Requestor First name', max_length=60)
        # requestor_surname= forms.CharField(max_length=60)
        # requestor_email= forms.EmailField()
        # user_firstname= forms.CharField(label='User First name', max_length=60)
        # user_surname= forms.CharField(max_length=60)
        # user_email= forms.EmailField()
        # enddate= forms.DateField()
        # approver_list= forms.CharField(label='Please select approver?', widget=forms.Select(choices=APPROVER_LIST))
        # access_list= forms.CharField(label='What access do you require?', widget=forms.CheckboxSelectMultiple(choices=ACCESS_LIST))

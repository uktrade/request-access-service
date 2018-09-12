from django import forms

ACCESS_CHOICES= [
    ('myeslf', 'Yes, for myself'),
    ('behalf', 'No, on behalf of someone'),
    ]

ACCESS_LIST= [
    ('aws', 'AWS'),
    ('vault', 'Vault'),
    ('rattic', 'Rattic')
    ]

APPROVER_LIST = [
    ('jayeshpatel', 'Jayesh Patel'),
    ('lyndongarvey', 'Lyndon Garvey'),
    ('bowensun', 'Bowen Sun')
]

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class UserForm(forms.Form):
    needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))

class AccessListForm(forms.Form):
    access_list= forms.CharField(label='What access do you require?', widget=forms.CheckboxSelectMultiple(choices=ACCESS_LIST))

class UserDetailsForm(forms.Form):
    first_name= forms.CharField(label='First name', max_length=100)
    last_name= forms.CharField(max_length=100)
    email= forms.EmailField()
    approver_list= forms.CharField(label='Please select approver?', widget=forms.Select(choices=APPROVER_LIST))

class UserDetailsFormBehalf(forms.Form):
    first_name= forms.CharField(label='First name', max_length=100)
    last_name= forms.CharField(max_length=100)
    email= forms.EmailField()
    enddate= forms.DateField()
    approver_list= forms.CharField(label='Please select approver?', widget=forms.Select(choices=APPROVER_LIST))

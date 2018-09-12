from django import forms

ACCESS_CHOICES= [
    ('myeslf', 'Yes, for myself'),
    ('behalf', 'No, on behalf of someone'),
    ]

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class UserForm(forms.Form):
    first_name= forms.CharField(max_length=100)
    last_name= forms.CharField(max_length=100)
    email= forms.EmailField()
    needs_access= forms.CharField(label='Is access for yourself?', widget=forms.RadioSelect(choices=ACCESS_CHOICES))

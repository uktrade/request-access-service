from django import forms
from .models import Approver, Services, User, Request

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
class YearField(fields.YearField):
    def __init__(self, era_boundary=None, **kwargs):
        #import pdb; pdb.set_trace()
        self.current_year = now().year + 10
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        bounds_error = gettext('Year should be between 1900 and %(current_year)s.') % {
            'current_year': self.current_year
        }
        options = {
            'min_value': 1900,
            'max_value': self.current_year,
            'error_messages': {
                'min_value': bounds_error,
                'max_value': bounds_error,
                'invalid': gettext('Enter year as a number.'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

class SplitDateFields(fields.SplitDateField):
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
           YearField(),
       ]
       #import pdb; pdb.set_trace()
       super().__init__(*args, **kwargs)

class UserForm(GOVUKForm):
    needs_access= forms.ChoiceField(label='Are you requesting access for yourself?', choices=ACCESS_CHOICES, widget=widgets.Select())


class UserEndForm(GOVUKForm):
    user_email = forms.CharField(label='Users E-mail (person who needs access)', max_length=60, widget=widgets.TextInput())
    firstname = forms.CharField(label='Users Firstname', max_length=60, widget=widgets.TextInput())
    surname = forms.CharField(label='Users Surname', max_length=60, required=False, widget=widgets.TextInput())
    end_date = SplitDateFields()#label='End Date of Contract')
    #end_date = fields.SplitDateField(label='End Date of Contract')

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

class RejectForm(GOVUKForm):
    rejected_reason = forms.CharField(label='Short description on why you have rejected access', widget=widgets.Textarea())

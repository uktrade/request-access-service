#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from .forms import UserEndForm, UserForm, ActionRequestsForm, UserDetailsForm, AccessReasonForm#, UserDetailsBehalfForm
from urllib.parse import urlencode
from .models import Approver, Services, User, Request
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string, get_template
from django.template import Template
#from .tokens import account_activation_token
from .email import send_approvals_email, send_requester_email
from django.views.generic.edit import FormView

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import HttpResponse

#from formtools.wizard.views import SessionWizardView
#from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
#from django.contrib.sites.models import Site
#import datetime

# Create your views here.

class landing_page(FormView):
    template_name = 'basic-post.html'
    form_class = UserForm

    def form_valid(self, form):
        self.behalf = False
        #context = form.cleaned_data
        #import pdb; pdb.set_trace()
        if form.cleaned_data['needs_access'] == 'behalf':
            #self.success_url = reverse_lazy('user_details_behalf')
            self.behalf = True
        # else:
        #     self.success_url = reverse_lazy('user_end')#('user_details')
        self.success_url = reverse_lazy('user_end')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        #import pdb; pdb.set_trace()
        context = {'behalf': self.behalf}
        return url + '?' + urlencode(context)

class user_end(FormView):
    template_name = 'basic-post.html'
    form_class = UserEndForm
    #success_url = reverse_lazy('submitted.html')
    #behalf_status = self.kwargs['behalf']
    success_url = reverse_lazy('access_reason')#('user_details')

    def get_form_kwargs(self):
        kwargs = super(user_end, self).get_form_kwargs()
        #import pdb; pdb.set_trace()
        self. behalf_status=self.request.GET['behalf']
        kwargs.update({'behalf': self.behalf_status})
        return kwargs

    def form_valid(self, form):

        self.email = form.cleaned_data['email']

        if self.behalf_status == 'True':
            self.user_email = form.cleaned_data['user_email']
        else:
            self.user_email = self.email

        self.user = User.objects.update_or_create(
            defaults={
            'firstname': form.cleaned_data['firstname'],
            'surname': form.cleaned_data['surname'],
            'end_date': form.cleaned_data['end_date']
            },
            email=self.user_email#form.cleaned_data['email']
            )

        #import pdb; pdb.set_trace()

        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        #import pdb; pdb.set_trace()

        context = {'email': self.email, 'user_email': self.user_email, 'behalf': self.behalf_status}
        return url + '?' + urlencode(context)


def get_token():
    #import pdb; pdb.set_trace()
    token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')

    return token


class access_reason(FormView):
    template_name = 'basic-post.html'
    form_class = AccessReasonForm
    success_url = reverse_lazy('user_details')

    def form_valid(self, form):
        #import pdb; pdb.set_trace()

        #approver = Approver.objects.get(id=form.cleaned_data['approver'])
        approver = form.cleaned_data['approver']
        reason=form.cleaned_data['reason']
        #self.context = dict(self.request.GET)
        self.context = {
            'email': self.request.GET['email'],
            'user_email': self.request.GET['user_email'],
            'behalf': self.request.GET['behalf'],
            'approver': approver,
            'reason': reason
            }

        return super().form_valid(form)


    def get_success_url(self):
        url = super().get_success_url()
        #import pdb; pdb.set_trace()

        #context = {'email': self.email, 'user_email': self.user_email, 'behalf': self.behalf_status}
        return url + '?' + urlencode(self.context)


class user_details(FormView):
    #import pdb; pdb.set_trace()
    template_name = 'basic-post.html'
    #behalf_status = False
    form_class = UserDetailsForm#(behalf=behalf_stat)

    def form_valid(self, form):
        #Approver.add(*[Services.objects.get(id=id) for id in form.cleaned_data['services']])
        #approver = Approver.objects.get(id=form.cleaned_data['approver'])
        #import pdb; pdb.set_trace()
        user_email = self.request.GET['user_email']
        requestor = self.request.GET['email']
        behalf = self.request.GET['behalf']
        approver = Approver.objects.get(id=self.request.GET['approver'])
        reason = self.request.GET['reason']
        token = get_token()
        request = Request.objects.create(
                        requestor=requestor,#form.cleaned_data['requestor'],
                        reason=reason,#form.cleaned_data['reason'],
                        approver=approver,
                        token=token,
                        user_email=user_email)#form.cleaned_data['requestor'])

        request.services.set([Services.objects.get(id=id) for id in form.cleaned_data['services']])
        # self.request.requestor = form.cleaned_data['requestor']
        # self.request.request_obj_id = request.id
        #import pdb; pdb.set_trace()
        User.objects.filter(email=user_email).update(request_id=request.id)

        send_mails(token, request.approver, request.id, user_email, self.request.scheme, self.request.get_host())

        t = render_to_string("submitted.html")

        return HttpResponse(t)


def send_mails(token, approver, request_id, user_email, protocol, domain):

    uidb64 = urlsafe_base64_encode(force_bytes(request_id)).decode()
    activation_url  = '/activate/' + uidb64 + '/' + token + '/'
    activate_url = "{0}://{1}{2}".format(protocol, domain, activation_url)
    send_approvals_email(activate_url, str(approver))
    send_requester_email(str(request_id), str(user_email))


def activate(request, uidb64=None, token=None):
    #import pdb; pdb.set_trace()
    #try:
        #uid = force_text(urlsafe_base64_decode(uidb64))
        #token_in_table=Request.objects.get(id=uid).token

    if Request.objects.filter(token=token).exists() and not Request.objects.get(token=token).signed_off:

        Request.objects.filter(token=token).update(signed_off=True, signed_off_on=timezone.now())
        return HttpResponse('Thank you for your email confirmation.')
    elif Request.objects.filter(token=token).exists() and Request.objects.get(token=token).signed_off:
        return HttpResponse('Confirmation has already been done!')

    else:
        return HttpResponse('Authourization link is invalid!')

    # except token.DoesNotExist:
    #     return HttpResponse('Activation link is invalid!')

# Prob dont need to do this as this can be done from the Admin interface.
def action_requests(request):
    #import pdb; pdb.set_trace()
    requests_to_complete = Request.objects.filter(completed=False)

    context = {'requests_to_complete': requests_to_complete}

    if request.method == 'POST':
        form = AcionRequestsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            #if form.cleaned_data['access_list'] == 'yes':

            for current_user in Request.objects.filter(signed_off=True):
                print (current_user.user_email)
                User.objects.get_or_create(firstname='User', surname='B', email=current_user.user_email, end_date='2018-09-20')
                #userobj.save()


            return render(request, 'submitted.html')
    else:
        form = ActionRequestsForm()

    return render(request, 'action-requests.html', context, {'form': form})

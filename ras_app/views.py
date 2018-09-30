#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from .forms import UserEndForm, UserForm, ActionRequestsForm, UserDetailsForm, UserDetailsBehalfForm
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

#from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
#from django.contrib.sites.models import Site
#import datetime

# Create your views here.

def landing_page(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            #import pdb; pdb.set_trace()
            context = form.cleaned_data
            if form.cleaned_data['needs_access'] == 'behalf':
                return redirect('/user-details-behalf/' + '?' + urlencode(context))
            else:
                return redirect('/user-details/' + '?' + urlencode(context))

    else:
        form = UserForm()

    return render(request, 'basic-post.html', {'form': form})

class landing_page(FormView):
    template_name = 'basic-post.html'
    form_class = UserForm

    def form_valid(self, form):
        #context = form.cleaned_data
        #import pdb; pdb.set_trace()
        if form.cleaned_data['needs_access'] == 'behalf':
            self.success_url = reverse_lazy('user_details_behalf')

        else:
            self.success_url = reverse_lazy('user_details')

        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        #context = {'requests_id': self.request.request_obj_id, 'email': self.request.requestor}
        return url #+ '?' + urlencode(context)


class user_details(FormView):
    #import pdb; pdb.set_trace()
    template_name = 'basic-post.html'
    form_class = UserDetailsForm
    success_url = reverse_lazy('user_end')
    #current_site = get_current_site(request)

    def form_valid(self, form):

        #Approver.add(*[Services.objects.get(id=id) for id in form.cleaned_data['services']])
        approver = Approver.objects.get(id=form.cleaned_data['approver'])
        #current_site = get_current_site(request)
        token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')
        request = Request.objects.create(requestor=form.cleaned_data['requestor'], reason=form.cleaned_data['reason'], approver=approver, token=token, user_email=form.cleaned_data['requestor'])
        request.services.set([Services.objects.get(id=id) for id in form.cleaned_data['services']])
        self.request.requestor = form.cleaned_data['requestor']
        self.request.request_obj_id = request.id
        #self.request.request_id = form.cleaned_data['id']
        #import pdb; pdb.set_trace()
        uidb64 = urlsafe_base64_encode(force_bytes(request.id)).decode()
        activation_url  = '/activate/' + uidb64 + '/' + token + '/'
        activate_url = "{0}://{1}{2}".format(self.request.scheme, self.request.get_host(), activation_url)
        send_approvals_email(activate_url, str(request.approver))
        send_requester_email(str(request.id), str(request.user_email))

        return super().form_valid(form)

    def get_success_url(self):
        #import pdb; pdb.set_trace()
        #request_id =
        url = super().get_success_url()
        context = {'requests_id': self.request.request_obj_id, 'email': self.request.requestor}
        return url + '?' + urlencode(context)


class user_details_behalf(FormView):
    #import pdb; pdb.set_trace()
    template_name = 'basic-post.html'
    form_class = UserDetailsBehalfForm
    success_url = reverse_lazy('user_end')


    def form_valid(self, form):

        #Approver.add(*[Services.objects.get(id=id) for id in form.cleaned_data['services']])
        approver = Approver.objects.get(id=form.cleaned_data['approver'])
        #
        token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')
        request = Request.objects.create(requestor=form.cleaned_data['requestor'], reason=form.cleaned_data['reason'], approver=approver, token=token, user_email=form.cleaned_data['user_email'])
        request.services.set([Services.objects.get(id=id) for id in form.cleaned_data['services']])
        self.request.requestor = form.cleaned_data['requestor']
        self.request.request_obj_id = request.id
        #self.request.request_id = form.cleaned_data['id']

        uidb64 = urlsafe_base64_encode(force_bytes(request.id)).decode()
        activation_url  = '/activate/' + uidb64 + '/' + token + '/'
        activate_url = "{0}://{1}{2}".format(self.request.scheme, self.request.get_host(), activation_url)
        send_approvals_email(activate_url, str(request.approver))
        send_requester_email(str(request.id), str(request.user_email))

        return super().form_valid(form)

    def get_success_url(self):
        #import pdb; pdb.set_trace()
        #request_id =
        url = super().get_success_url()
        context = {'requests_id': self.request.request_obj_id, 'email': self.request.requestor}
        return url + '?' + urlencode(context)

class user_end(FormView):
    template_name = 'basic-post.html'
    form_class = UserEndForm
    #success_url = reverse_lazy('submitted.html')


    def form_valid(self, form):
        #import pdb; pdb.set_trace()
        request_id = self.request.GET['requests_id']
        email = self.request.GET['email']

        request_obj=Request.objects.get(id=request_id)
        User.objects.create(email=email,
            firstname=form.cleaned_data['firstname'],
            surname=form.cleaned_data['surname'],
            end_date=form.cleaned_data['end_date'],
            request=request_obj)

        t = render_to_string("submitted.html")

        return HttpResponse(t)


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



# def user_end(request):

#     request_id = request.GET['requests_id']
#     email = request.GET['email']
#     if request.method == 'POST':
#         form = UserEndForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             #import pdb; pdb.set_trace()
#             user = form.save(commit=False)
#             request_obj=Request.objects.get(id=request_id)
#             user.email=email
#             user.request = request_obj
#             user.save()
#             #form.save_m2m()
#             #import pdb; pdb.set_trace()
#             return render(request, 'submitted.html')

#     else:
#         form = UserEndForm()

#     return render(request, 'basic-post.html', {'form': form})

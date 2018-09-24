#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import UserEndForm, UserForm, ActionRequestsForm, UserDetailsForm, UserDetailsBehalfForm
from urllib.parse import urlencode
from .models import Approver, Services, User, Request
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .email import send_approvals_email

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
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

def user_details(request):

    #import pdb; pdb.set_trace()

    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = form.save(commit=False)

            #import pdb; pdb.set_trace()
            user.user_email = user.requestor
            current_site = get_current_site(request)
            token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')
            user.token=token
            user.save()
            form.save_m2m()
            #import pdb; pdb.set_trace()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            activation_url  = '/activate/' + uidb64 + '/' + token + '/'

            activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)
            send_approvals_email(activate_url, str(user.approver))
            #print (user.requestor, ': ', activate_url)
            context = {'requests_id': user.id}
            return redirect('/user-end/' + '?' + urlencode(context))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserDetailsForm()

    return render(request, 'basic-post.html', {'form': form, 'url': 'user-details'})

def user_details_behalf(request):

    #import pdb; pdb.set_trace()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #import pdb; pdb.set_trace()
        form = UserDetailsBehalfForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = form.save(commit=False)

            user.user_email = user.requestor
            current_site = get_current_site(request)
            token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')
            user.token=token
            user.save()
            form.save_m2m()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            activation_url  = '/activate/' + uidb64 + '/' + token + '/'
            activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)
            send_approvals_email(activate_url, str(user.approver))
            context = {'requests_id': user.id}
            #print (user.requestor, ': ', activate_url)
            return redirect('/user-end/' + '?' + urlencode(context))

    else:
        form = UserDetailsBehalfForm()

    return render(request, 'basic-post.html', {'form': form, 'url': 'user-details-behalf'})

def user_end(request):

    request_id = request.GET['requests_id']
    if request.method == 'POST':
        form = UserEndForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #import pdb; pdb.set_trace()
            user = form.save(commit=False)
            request_obj=Request.objects.get(id=request_id)
            user.request = request_obj
            user.save()
            #form.save_m2m()
            #import pdb; pdb.set_trace()
            return render(request, 'submitted.html')

    else:
        form = UserEndForm()

    return render(request, 'basic-post.html', {'form': form})

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

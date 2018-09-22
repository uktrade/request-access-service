#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import NameForm, UserForm, AccessListForm, UserDetailsForm, UserDetailsFormBehalf, SignupForm
from urllib.parse import urlencode
from .models import Approver, Services, User, Request
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
#import datetime

# Create your views here.

def test(request):
    # url_list = Urllist.objects.all()
    # context = {'url_list': url_list}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # redirect to a new URL:
            params = form.cleaned_data

            #return HttpResponseRedirect('/next-page/',) '?' + urlencode(params)
            return redirect('/next-page/' + '?' + urlencode(params))

    else:
        form = NameForm()

    return render(request, 'test.html', {'form': form})



def next_page(request):

    your_name = request.GET['your_name']
    context = {'your_name': your_name}

    return render(request, 'next-page.html', context)

def landing_page(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            #import pdb; pdb.set_trace()
            #print (form.cleaned_data['needs_access'])
            context = form.cleaned_data
            if form.cleaned_data['needs_access'] == 'behalf':
                return redirect('/user-details-behalf/' + '?' + urlencode(context))
            else:
                return redirect('/user-details/' + '?' + urlencode(context))

    else:
        form = UserForm()

    return render(request, 'post-form.html', {'form': form, 'url': 'landing-page'})

def user_details(request):

    # your_name = request.GET['first_name']
    # context = {'your_name': your_name}
    #import pdb; pdb.set_trace()

    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = form.save(commit=False)

            #import pdb; pdb.set_trace()
            user.user_email = user.requestor
            
            current_site = get_current_site(request)
            #kwargs = {
            
            token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')
            #}
            # kwargs = {
            #     "uidb64": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            #     "token": default_token_generator.make_token(user)
            # }

            #activation_url = reverse('activate', kwargs=kwargs)
            user.token=token
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            activation_url  = '/activate/' + uidb64 + '/' + token + '/'

            activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)

            # context = {
            #     'user': user,
            #     'activate_url': activate_url
            # }
            # html_content = render_to_string('activate.html', context)


            print (user.requestor, ': ', activate_url)
            return render(request, 'submitted.html')# + '?' + urlencode(context))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserDetailsForm()

    return render(request, 'post-form.html', {'form': form, 'url': 'user-details'})

def user_details_behalf(request):
    # firstname = request.GET['first_name']
    # surname = request.GET['last_name']
    # email = request.GET['email']

    #import pdb; pdb.set_trace()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #import pdb; pdb.set_trace()
        form = UserDetailsFormBehalf(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=False)

            form.save()


            return redirect('/access-list/') #+ '?' + urlencode(context))

    else:
        form = UserDetailsFormBehalf()

    return render(request, 'post-form.html', {'form': form, 'url': 'user-details-behalf'})

def access_list(request):

    if request.method == 'POST':
        form = AccessListForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #if form.cleaned_data['access_list'] == 'yes':

            for current_user in Request.objects.filter(signed_off=True):
                print (current_user.user_email)
                User.objects.get_or_create(firstname='User', surname='B', email=current_user.user_email, end_date='2018-09-20')
                #userobj.save()


            return render(request, 'submitted.html')
    else:
        form = AccessListForm()

    return render(request, 'post-form.html', {'form': form, 'url': 'access-list'})

def post_request():
    print('')



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



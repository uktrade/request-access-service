#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import NameForm, UserForm, AccessListForm, UserDetailsForm, UserDetailsFormBehalf
from urllib.parse import urlencode
from .models import Approver, Services, User, Request

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

            form.save()
            return redirect('/access-list/')# + '?' + urlencode(context))

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
            # Overwrite not working
            form.user_email = 'me@me.com'
            #import pdb; pdb.set_trace()
            #initial={'user_email': 'me@me.com'}
            #print (form.cleaned_data['access_list'])
            form.save()
            #context = {'your_name': 'Jayesh'}

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

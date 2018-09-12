#from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import NameForm, UserForm
from urllib.parse import urlencode

# Create your views here.

def landing_page(request):
    # url_list = Urllist.objects.all()
    # context = {'url_list': url_list}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            params = form.cleaned_data

            #return HttpResponseRedirect('/next-page/',) '?' + urlencode(params)
            return redirect('/next-page/' + '?' + urlencode(params))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'index.html', {'form': form})

def next_page(request):

    your_name = request.GET['your_name']
    context = {'your_name': your_name}

    return render(request, 'next-page.html', context)

def radio(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            #import pdb; pdb.set_trace()
            #print (form.cleaned_data['needs_access'])
            # redirect to a new URLself
            context = form.cleaned_data
            if form.cleaned_data['needs_access'] == 'behalf':
                return render(request, 'behalf.html', context)
            else:
                return render(request, 'myself.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()

    return render(request, 'radio.html', {'form': form})

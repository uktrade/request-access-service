from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from .forms import UserForm, ActionRequestsForm, UserDetailsForm, AccessReasonForm, UserEndForm, RejectForm
from urllib.parse import urlencode
from .models import Approver, Services, User, Request
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string, get_template
from django.template import Template
from .email import send_approvals_email, send_requester_email
from django.views.generic.edit import FormView

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings

from django.utils import timezone
from django.utils.crypto import get_random_string

from django.contrib.auth.decorators import login_required

# Create your views here.
#@login_required(login_url='/landing-page/')
class home_page(FormView):
    template_name = 'home-page.html'
    form_class = UserForm

    def form_valid(self, form):
        self.behalf = False

        if form.cleaned_data['needs_access'] == 'behalf':
            self.behalf = True

        self.success_url = reverse_lazy('user_end')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {'behalf': self.behalf}
        return url + '?' + urlencode(context)

class user_end(FormView):
    template_name = 'basic-post.html'
    form_class = UserEndForm
    success_url = reverse_lazy('access_reason')#('user_details')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('user_end') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):

        kwargs = super(user_end, self).get_form_kwargs()

        self.behalf_status=self.request.GET['behalf']
        kwargs.update({'behalf': self.behalf_status})
        return kwargs

    def form_valid(self, form):
        self.email = self.request.user.email

        if self.behalf_status == 'True':
            self.user_email = form.cleaned_data['user_email']
            firstname = form.cleaned_data['firstname']
            surname = form.cleaned_data['surname']

        else:
            self.user_email = self.email
            firstname = self.request.user.first_name
            surname = self.request.user.last_name

        self.user = User.objects.update_or_create(
            defaults={
            'firstname': firstname,
            'surname': surname,
            'end_date': form.cleaned_data['end_date']
            },
            email=self.user_email
            )

        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {'email': self.email, 'user_email': self.user_email, 'behalf': self.behalf_status}
        return url + '?' + urlencode(context)


class access_reason(FormView):
    template_name = 'basic-post.html'
    form_class = AccessReasonForm
    success_url = reverse_lazy('user_details')

    def dispatch(self, request, *args, **kwargs):

        if not reverse('user_end') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('access_reason') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        approver = form.cleaned_data['approver']
        reason=form.cleaned_data['reason']
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
        return url + '?' + urlencode(self.context)


def get_token():
    token = get_random_string(length=20,allowed_chars='abcdefgh0123456789')

    return token


def send_mails(token, approver, request_id, user_email):#, protocol, domain):

    #uidb64 = urlsafe_base64_encode(force_bytes(request_id)).decode()
    # activation_url  = '/activate/' + token + '/'
    # activate_url = "{0}://{1}{2}".format(protocol, domain, activation_url)
    send_approvals_email(token, str(approver))
    send_requester_email(str(request_id), str(user_email), '')

class user_details(FormView):
    template_name = 'basic-post.html'
    form_class = UserDetailsForm

    def dispatch(self, request, *args, **kwargs):
        #import pdb; pdb.set_trace()
        if not reverse('access_reason') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('user_details') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')

        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        user_email = self.request.GET['user_email']
        requestor = self.request.GET['email']
        behalf = self.request.GET['behalf']
        approver = Approver.objects.get(id=self.request.GET['approver'])
        reason = self.request.GET['reason']
        token = get_token()
        request = Request.objects.create(
                        requestor=requestor,
                        reason=reason,
                        approver=approver,
                        token=token,
                        user_email=user_email)

        request.services.set([Services.objects.get(id=id) for id in form.cleaned_data['services']])
        User.objects.filter(email=user_email).update(request_id=request.id)

        send_mails(token, request.approver, request.id, user_email)#, self.request.scheme, self.request.get_host())

        t = render_to_string("submitted.html")

        return HttpResponse(t)


def admin_override(request):
    """This view is to redirect the admin page to SSO for authentication."""

    if not reverse('home_page') in request.META.get('HTTP_REFERER', ''):
        if not reverse('admin_override') in request.META.get('HTTP_REFERER', ''):
            return redirect('home_page')

    return redirect('/admin/')

def activate(request, uidb64=None, token=None):
    #import pdb; pdb.set_trace()
    #try:
        #uid = force_text(urlsafe_base64_decode(uidb64))
        #token_in_table=Request.objects.get(id=uid).token

    if Request.objects.filter(token=token).exists() and not Request.objects.get(token=token).signed_off:

        Request.objects.filter(token=token).update(signed_off=True, signed_off_on=timezone.now())
        context = {'message': 'Thank you for your email confirmation.'}
        render_to_string('notify.html', context)
        return HttpResponse(t)
    elif Request.objects.filter(token=token).exists() and Request.objects.get(token=token).signed_off:
        context = {'message': 'Confirmation has already been done!'}
        render_to_string('notify.html', context)
        return HttpResponse(t)

    else:
        context = {'message': 'Authourization link is invalid!'}
        render_to_string('notify.html', context)
        return HttpResponse(t)


# def send_mail_rejected(requestor_email, rejected_reason):
#     print (requestor_email, rejected_reason)
#     send_requester_email(request_id, requestor, rejected_reason)

class reject_access(FormView):
    template_name = 'basic-post.html'
    form_class = RejectForm

    def dispatch(self, request, *args, **kwargs):
        #import pdb; pdb.set_trace()
        self.token =  kwargs['token']
        if Request.objects.filter(token=self.token).exists() and not Request.objects.get(token=self.token).signed_off:
            print ("Do nothing")

            #Request.objects.filter(token=token).update(signed_off=True, signed_off_on=timezone.now())
            #return HttpResponse('Thank you for your email confirmation.')
        elif Request.objects.filter(token=self.token).exists() and Request.objects.get(token=self.token).signed_off:
            context = {'message': 'Confirmation has already been done!'}
            t = render_to_string('notify.html', context)
            return HttpResponse(t)
        else:
            context = {'message': 'Authourization link is invalid!'}
            t = render_to_string('notify.html', context)
            return HttpResponse(t)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        Request.objects.filter(token=self.token).update(rejected=True, rejected_reason=form.cleaned_data['rejected_reason'])
        #t = render_to_string("submitted.html")
        #user_email = Request.objects.get(token=self.token).user_email
        send_requester_email(Request.objects.get(token=self.token).id ,Request.objects.get(token=self.token).requestor, form.cleaned_data['rejected_reason'])

        context = {'message': 'Thank you, request rejected.  Requester has been notified'}
        t = render_to_string('notify.html', context)#, message)
        return HttpResponse(t)# 'Thank you, request rejected.  Requester has been notified')


# Prob dont need to do this as this can be done from the Admin interface.
def action_requests(request):
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

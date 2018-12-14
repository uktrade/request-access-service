from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from .forms import UserForm, ActionRequestsForm, UserDetailsForm, AccessReasonForm, UserEndForm, UserEmailForm, RejectForm
from urllib.parse import urlencode
from .models import Approver, Services, User, Request, RequestItem, RequestorDetails#, RequestServices
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string, get_template
from django.template import Template
from .email import send_approvals_email, send_requester_email, send_accounts_creator_email, send_completed_email
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
            self.context = {'behalf': self.behalf}
        else:
            #import pdb; pdb.set_trace()
            self.context = {'email': self.request.user.email, 'user_email': self.request.user.email, 'behalf': False}
            self.success_url = reverse_lazy('access_reason')
            return super().form_valid(form)

        self.success_url = reverse_lazy('user_email')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        #context = {'behalf': self.behalf}
        return url + '?' + urlencode(self.context)


#def check_user_exists(email_address):

class user_email(FormView):
    template_name = 'basic-post.html'
    form_class = UserEmailForm
    #success_url = reverse_lazy('user_end')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('user_email') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')

        return super().dispatch(request, *args, **kwargs)

    # def get_form_kwargs(self):
    #
    #     kwargs = super(user_email, self).get_form_kwargs()
    #     import pdb; pdb.set_trace()
    #     self.behalf_status=self.request.GET['behalf']
    #     kwargs.update({'behalf': self.behalf_status})
    #     return kwargs

    def form_valid(self, form):
        #import pdb; pdb.set_trace()
        self.email = self.request.user.email
        self.user_email = form.cleaned_data['user_email']
        self.behalf_status=self.request.GET['behalf']

        if User.objects.filter(email=self.user_email).exists():
            #return redirect('access_reason')
            #context = {'email': self.email, 'user_email': self.user_email, 'behalf': self.behalf_status}
            self.success_url = reverse_lazy('access_reason')
            #return super().form_valid(form)
        else:
            self.success_url = reverse_lazy('user_end')

        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {'email': self.email, 'user_email': self.user_email, 'behalf': self.behalf_status}
        return url + '?' + urlencode(context)


class user_end(FormView):
    template_name = 'basic-post.html'
    form_class = UserEndForm
    success_url = reverse_lazy('access_reason')#('user_details')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('user_email') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('user_end') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):

        kwargs = super(user_end, self).get_form_kwargs()
        self.email = self.request.GET['email']
        self.user_email = self.request.GET['user_email']
        self.behalf_status=self.request.GET['behalf']
        # kwargs.update({'behalf': self.behalf_status})
        return kwargs

    def form_valid(self, form):
        #self.email = self.request.user.email
        #import pdb; pdb.set_trace()


        if self.behalf_status == 'True':
            #self.user_email = form.cleaned_data['user_email']
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

        RequestorDetails.objects.update_or_create(
            defaults={
            'firstname': self.request.user.first_name,
            'surname': self.request.user.last_name,
            },
            email=self.email
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
    # def __init__(self,*args,**kwargs):
    #     import pdb; pdb.set_trace()
    #     self.email = kwargs.pop('email')
    #     super(StylesForm,self).__init__(*args,**kwargs)
    #def get_form_kwargs(self):

        # kwargs = super(access_reason, self).get_form_kwargs()
        # #import pdb; pdb.set_trace()
        # self.email_status=self.request.GET['email']
        # kwargs.update({'email': self.email_status})
        # return kwargs

    def dispatch(self, request, *args, **kwargs):
        #kwargs = super(access_reason, self).get_form_kwargs()

        if not reverse('user_end') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('user_email') in self.request.META.get('HTTP_REFERER', ''):
                if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
                    if not reverse('access_reason') in self.request.META.get('HTTP_REFERER', ''):
                        return redirect('home_page')
        #import pdb; pdb.set_trace()
        #self.email_status=self.request.GET['email']
        #kwargs.update({'email': self.email_status})
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self,  **kwargs):
        kwargs = super(access_reason, self).get_form_kwargs(**kwargs)
        #import pdb; pdb.set_trace()
        kwargs['email'] = self.request.GET['email']
        kwargs['behalf'] = self.request.GET['behalf']
        return kwargs

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

    def get_form_kwargs(self,  **kwargs):
        kwargs = super(user_details, self).get_form_kwargs(**kwargs)
        #import pdb; pdb.set_trace()
        kwargs['user_email'] = self.request.GET['user_email']
        return kwargs

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
        #import pdb; pdb.set_trace()

        request.add_request_items(form.cleaned_data['services'])
        #def add_item(form.cleaned_data['services']):
        # for service_id in form.cleaned_data['services']:
        #     RequestItem.objects.create(request=request, service=Service.objects.get(id=service_id)
        #request.services.set([Services.objects.get(id=id) for id in form.cleaned_data['services']])
        # for id in form.cleaned_data['services']:
        #     RequestServices.objects.create(
        #                     request_id=request.id,
        #                     service_id=id)

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
        #import pdb; pdb.set_trace()
        send_accounts_creator_email(Request.objects.values_list('id', flat=True).filter(token=token))
        context = {'message': 'Thank you for your email confirmation.'}
        t = render_to_string('notify.html', context)
        return HttpResponse(t)
    elif Request.objects.filter(token=token).exists() and Request.objects.get(token=token).signed_off:
        context = {'message': 'Confirmation has already been done!'}
        t = render_to_string('notify.html', context)
        return HttpResponse(t)

    else:
        context = {'message': 'Authourization link is invalid!'}
        t = render_to_string('notify.html', context)
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



class action_requests(FormView):
    template_name = 'home-page.html'
    form_class = ActionRequestsForm

    def get_form_kwargs(self):
        #import pdb; pdb.set_trace()
        kwargs = super().get_form_kwargs()
        self.email = self.request.user.email
        kwargs.update({'email': self.email})
        #kwargs['uid'] = self.uuid

        return kwargs

    # def dispatch(self, *args, **kwargs):
    #     import pdb; pdb.set_trace()
    #     self.email = self.request.user.email
    #     kwargs.update({'email': self.email})
    #     #self.uuid = self.kwargs['userid']
    #     return super().dispatch(*args, kwargs)

    def form_valid(self, form):
        # print ('Do something')
        # import pdb; pdb.set_trace()

        services_completed = form.cleaned_data['action']
        #import pdb; pdb.set_trace()
        # for z in services_completed:
        #     RequestItem.objects.filter(id=z).update(completed=True)
        completed_tasks = RequestItem.objects.values('request_id','services__service_name').filter(id__in=services_completed).order_by('request_id')
        send_completed_email(completed_tasks)

        t = render_to_string("submitted.html")
        return HttpResponse(t)

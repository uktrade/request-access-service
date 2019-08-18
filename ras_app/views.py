import json
import requests

from .forms import (
    StartForm, ActionRequestsForm, AddSelfForm, ServicesRequiredForm,
    AccessApproverForm, StaffLookupForm, AddNewUserForm,
    AdditionalInfoForm, ReasonForm, AccessRequestsForm)
from .models import (
    Approver, Services, User, Request, RequestItem, RequestorDetails, Teams,
    AccountsCreator)
from .email import (
    send_approvals_email, send_requestor_email, send_accounts_creator_email,
    send_completed_email, send_end_user_email)

from urllib.parse import urlencode

from django.template.loader import render_to_string
from django.views.generic.edit import FormView
from django.views import View, generic
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


def admin_override(request):
    # This view is to redirect the admin page to SSO for authentication.
    if not reverse('home_page') in request.META.get('HTTP_REFERER', ''):
        if not reverse('admin_override') in request.META.get('HTTP_REFERER', ''):
            return redirect('home_page')

    return redirect('/admin/')


def get_email_address(staff_name):

    response = requests.get(
        'https://sso.trade.gov.uk/api/v1/user/search/',
        params={'autocomplete': staff_name},
        headers={'Authorization': f'Bearer {settings.SSO_INTROS_TOKEN}'})

    if response.status_code == requests.codes.ok:
        user_data = response.json()
        email_address = user_data['results'][0]['email']
    else:
        messages.info(self.request, 'This user is not in the staff sso database')
    return (email_address)


class home_page(FormView):
    template_name = 'home-page.html'
    form_class = StartForm

    def form_valid(self, form):
        if form.cleaned_data['needs_access'] == 'on_behalf':
            self.context = {}
        else:
            self.context = {
                'email': self.request.user.email,
                'user_email': self.request.user.email}
            # Check if user exists.
            if User.objects.filter(email=self.request.user.email).exists():
                self.success_url = reverse_lazy('access_approver')
            else:
                self.success_url = reverse_lazy('add_self')
            return super().form_valid(form)

        self.success_url = reverse_lazy('add_new_user')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        return url + '?' + urlencode(self.context)


class add_self(FormView):
    template_name = 'basic-post.html'
    form_class = AddSelfForm

    def dispatch(self, request, *args, **kwargs):
        if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('add_self') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        User.objects.update_or_create(defaults={
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'team': Teams.objects.get(id=form.cleaned_data['team'])},
            email=self.request.user.email)
        self.success_url = reverse_lazy('access_approver')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {
            'email': self.request.user.email,
            'user_email': self.request.user.email}
        return url + '?' + urlencode(context)


class add_new_user(FormView):
    template_name = 'add-new-user.html'
    form_class = AddNewUserForm

    def dispatch(self, request, *args, **kwargs):
        if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('add_new_user') in self.request.META.get('HTTP_REFERER', ''):
                if not reverse('staff_lookup') in self.request.META.get('HTTP_REFERER', ''):
                    return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(add_new_user, self).get_form_kwargs(**kwargs)
        # Dont like this, but will function for now.
        try:
            self.request.GET['chosen_staff']
        except Exception:
            print("no value set yet")
        else:
            kwargs['chosen_staff'] = self.request.GET['chosen_staff']
        return kwargs

    def form_valid(self, form):
        self.team = form.cleaned_data['team']
        user = form.cleaned_data['user']

        self.user_email = get_email_address(user)
        self.email = self.request.user.email

        if User.objects.filter(email=self.user_email).exists():
            self.success_url = reverse_lazy('access_approver')
        else:
            # Add the user to the DB
            User.objects.update_or_create(defaults={
                'first_name': user.split(None, 1)[0],
                'last_name': user.split(None, 1)[1],
                'team': Teams.objects.get(id=self.team)}, email=self.user_email)

            RequestorDetails.objects.update_or_create(defaults={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name}, email=self.email)

            self.success_url = reverse_lazy('access_approver')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {
            'email': self.email,
            'user_email': self.user_email,
            'team': self.team}
        return url + '?' + urlencode(context)


class access_approver(FormView):
    template_name = 'access-approver.html'
    form_class = AccessApproverForm
    success_url = reverse_lazy('services_required')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('add_new_user') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('home_page') in self.request.META.get('HTTP_REFERER', ''):
                if not reverse('add_self') in self.request.META.get('HTTP_REFERER', ''):
                    if not reverse('access_approver') in self.request.META.get('HTTP_REFERER', ''):
                        if not reverse('staff_lookup') in self.request.META.get(
                                'HTTP_REFERER', ''):
                            return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(access_approver, self).get_form_kwargs(**kwargs)
        # Dont like this, but will function for now.
        try:
            self.request.GET['chosen_staff']
        except Exception:
            print("no value set yet")
        else:
            kwargs['chosen_staff'] = self.request.GET['chosen_staff']
        return kwargs

    def form_valid(self, form):
        approver = form.cleaned_data['approver']
        approver_email = get_email_address(approver)

        self.context = {
            'email': self.request.GET['email'],
            'user_email': self.request.GET['user_email'],
            'approver': approver_email}
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        return url + '?' + urlencode(self.context)


class staff_lookup(FormView):
    template_name = 'staff-lookup.html'
    form_class = StaffLookupForm
    success_url = reverse_lazy('staff_lookup')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('staff_lookup') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('add_new_user') in self.request.META.get('HTTP_REFERER', ''):
                if not reverse('access_approver') in self.request.META.get('HTTP_REFERER', ''):
                    return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.request.session['_referer'] = request.META.get('HTTP_REFERER', '')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = requests.get(
            'https://sso.trade.gov.uk/api/v1/user/search/',
            params={'autocomplete': form.cleaned_data['searchname']},
            headers={'Authorization': f'Bearer {settings.SSO_INTROS_TOKEN}'})

        if response.status_code == requests.codes.ok:
            staff_list = []
            user_data = response.json()
            for staff in user_data['results']:
                # This line exclude the person raising the request from being the approveer.
                # 2 lines commented whilst testing.
                # if staff['email'] != self.request.user.email:
                #     staff_list.append(staff['first_name'] + ' ' + staff['last_name'])

                # Comment this line when done with testing.
                staff_list.append(staff['first_name'] + ' ' + staff['last_name'])

            context = self.get_context_data()
            context['staff_list'] = staff_list

            if 'add-new-user' in self.request.session['_referer']:
                context['referer_path'] = '/add-new-user/'
            else:
                context['referer_path'] = '/access-approver/'
            return self.render_to_response(context)
        else:
            messages.info(self.request, 'This user is not in the staff sso database')
            return redirect('/staff-lookup/')


def send_mails(request_id):

    send_approvals_email(str(request_id))
    send_end_user_email(str(request_id))
    if Request.objects.get(id=request_id).requestor != Request.objects.get(
            id=request_id).user_email:
        send_requestor_email(str(request_id))
    return


class services_required(FormView):
    template_name = 'basic-post.html'
    form_class = ServicesRequiredForm
    success_url = reverse_lazy('reason')

    def dispatch(self, request, *args, **kwargs):
        if not reverse('access_approver') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('services_required') in self.request.META.get('HTTP_REFERER', ''):
                return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(services_required, self).get_form_kwargs(**kwargs)
        kwargs['user_email'] = self.request.GET['user_email']
        return kwargs

    def form_valid(self, form):
        user_email = self.request.GET['user_email']
        requestor = self.request.GET['email']
        approver = Approver.objects.get(email=self.request.GET['approver'])

        request = Request.objects.create(
            requestor=requestor,
            approver=approver,
            user_email=user_email)

        request.add_request_items(form.cleaned_data['services'])
        User.objects.filter(email=user_email).update(request_id=request.id)
        ga = False
        github = False
        ukgovpaas = False
        self.service = ''
        if RequestItem.objects.filter(
                request_id=request.id, services__service_name='google analytics'):
            ga = True

        if RequestItem.objects.filter(
                request_id=request.id, services__service_name='github'):
            github = True

        if RequestItem.objects.filter(
                request_id=request.id, services__service_name='ukgov paas'):
            ukgovpaas = True

        self.request_id = request.id
        self.approver = request.approver
        self.services = '{"ga": "' + str(ga) + '", "github": "' + str(github) \
            + '", "ukgovpaas": "' + str(ukgovpaas) + '"}'

        if ga or github or ukgovpaas:
            self.success_url = reverse_lazy('additional_info')
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {
            'request_id': self.request_id,
            'approver': self.approver,
            'services': self.services}
        return url + '?' + urlencode(context)


class additional_info(FormView):
    template_name = 'basic-post.html'
    form_class = AdditionalInfoForm
    success_url = reverse_lazy('reason')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.request_id = self.request.GET['request_id']
        self.approver = self.request.GET['approver']
        self.services = self.request.GET['services']
        kwargs.update({'services': self.services})
        return kwargs

    def form_valid(self, form):
        service_objects = json.loads(self.services)
        for service, value in service_objects.items():
            if value == 'True' and service == 'ga':
                RequestItem.objects.filter(
                    request_id=self.request_id,
                    services__service_name='google analytics').update(
                        additional_info=form.cleaned_data['ga_info'])

            if value == 'True' and service == 'github':
                RequestItem.objects.filter(
                    request_id=self.request_id, services__service_name='github').update(
                        additional_info=form.cleaned_data['github_info'])

            if value == 'True' and service == 'ukgovpaas':
                RequestItem.objects.filter(
                    request_id=self.request_id, services__service_name='ukgov paas').update(
                        additional_info=form.cleaned_data['ukgovpaas_info'])
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        context = {
            'request_id': self.request_id,
            'approver': self.approver,
            'services': self.services}
        return url + '?' + urlencode(context)


class reason(FormView):
    template_name = 'basic-post.html'
    form_class = ReasonForm

    def dispatch(self, request, *args, **kwargs):
        if not reverse('services_required') in self.request.META.get('HTTP_REFERER', ''):
            if not reverse('reason') in self.request.META.get('HTTP_REFERER', ''):
                if not reverse('additional_info') in self.request.META.get('HTTP_REFERER', ''):
                    return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.request_id = self.request.GET['request_id']
        return kwargs

    def form_valid(self, form):
        Request.objects.filter(id=self.request_id).update(reason=form.cleaned_data['reason'])
        send_mails(self.request_id)
        template = render_to_string("submitted.html")
        return HttpResponse(template)


class access_requests(FormView):
    template_name = 'access-requests.html'
    form_class = AccessRequestsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.email = self.request.user.email
        kwargs.update({'email': self.email})
        return kwargs

    def dispatch(self, *args, **kwargs):
        self.email = self.request.user.email
        items_to_approve = Request.objects.filter(approver_id=Approver.objects.get(
            email=self.email).id).exclude(signed_off=True).exclude(rejected=True)
        if not items_to_approve:
            messages.info(self.request, 'You have no items to approve')
        return super().dispatch(*args, kwargs)

    def form_valid(self, form):
        requests_to_approve = form.cleaned_data['approve']
        requests_rejected = form.cleaned_data['reject']

        # Do approvals updates in DB + stop selecting approve and reject check box
        if requests_to_approve in [requests_rejected]:
            messages.info(self.request, 'You can not approve and disapprove same item')
            return redirect('access-requests')

        Request.objects.filter(id__in=requests_to_approve).update(
            signed_off=True, signed_off_on=timezone.now())

        for request_id in requests_to_approve:
            send_accounts_creator_email(request_id)

        if requests_rejected:
            self.rejected_ids = requests_rejected
            self.success_url = reverse_lazy('rejected_reason')
            return super().form_valid(form)

        template = render_to_string("submitted.html")
        return HttpResponse(template)

    def get_success_url(self):
        url = super().get_success_url()
        rejected_ids = ','.join(self.rejected_ids)
        context = {'rejected_ids': rejected_ids}
        return url + '?' + urlencode(context)


class rejected_reason(View):
    template_name = 'rejected-reason.html'
    template_name_success = 'submitted.html'

    def get(self, request, *args, **kwargs):
        form_list = action_rejected_form_factory(request.GET['rejected_ids'])
        return render(request, self.template_name, {'form_list': form_list})

    def post(self, request, *args, **kwargs):
        form_list = action_rejected_form_factory(request.GET['rejected_ids'], request.POST)
        if not all(form.is_valid() for form in form_list):
            return render(request, self.template_name, {'form_list': form_list})
        else:
            for idx, val in enumerate(form_list):
                requestid = form_list[idx].fields['rejected_reason'].label_suffix
                rejected_reason = form_list[idx].cleaned_data['rejected_reason']
                Request.objects.filter(id=requestid).update(
                    rejected=True, rejected_reason=rejected_reason)
                send_requestor_email(requestid)
            return render(request, self.template_name_success)


class action_requests(FormView):
    template_name = 'home-page.html'
    form_class = ActionRequestsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.email = self.request.user.email
        kwargs.update({'email': self.email})
        return kwargs

    def form_valid(self, form):
        services_completed = form.cleaned_data['action']
        for service_id in services_completed:
            RequestItem.objects.filter(id=service_id).update(completed=True)
        completed_tasks = RequestItem.objects.values(
            'request_id', 'services__service_name').filter(
                id__in=services_completed).order_by('request_id')
        send_completed_email(completed_tasks)

        template = render_to_string("submitted.html")
        return HttpResponse(template)


class request_status(generic.ListView):
    template_name = 'request-status.html'

    def get(self, request, *args, **kwargs):
        self.request.user.email
        formatted_reqs_not_appr = []
        reqs_not_appr = Request.objects.values_list(
            'id',
            'approver__email',
            'requestitem__services__service_name').filter(
                user_email=self.request.user.email,
                signed_off=False)
        for req_id, approver, service in reqs_not_appr:
            if service in ['google analytics', 'github', 'ukgov paas']:
                request_str = 'Request id: ' + str(req_id) + \
                    ', Approver: ' + approver + \
                    ', Service: ' + service + ' - ' + \
                    RequestItem.objects.get(
                        request_id=req_id, services__service_name=service).additional_info
                formatted_reqs_not_appr.append(request_str)
            else:
                request_str = 'Request id: ' + str(req_id) + \
                    ', Approver: ' + approver + \
                    ', Service: ' + service
                formatted_reqs_not_appr.append(request_str)

        requests_not_activated = Request.objects.values_list('id').filter(
            user_email=self.request.user.email,
            signed_off=True)
        service_not_activated = []
        for request_id in requests_not_activated:
            service_not_activated = (RequestItem.objects.values(
                'request_id', 'services_id').filter(request_id__in=request_id))
        service_not_activated_lst = []
        svc_admins = []
        for idx, item in enumerate(service_not_activated):
            for x in AccountsCreator.objects.values_list('email', flat=True).filter(
                    services__id=item['services_id']):
                svc_admins.append(x)
            if Services.objects.get(id=item['services_id']).service_name in [
                    'google analytics',
                    'github',
                    'ukgov paas']:
                service = Services.objects.get(
                    id=item['services_id']).service_name + ' - ' + RequestItem.objects.get(
                    request_id=item['request_id'], services_id=item['services_id']).additional_info
            else:
                service = Services.objects.get(id=item['services_id']).service_name

            service_str = 'Request id: ' + str(item['request_id']) + \
                ', Service Admins: ' + str(set(svc_admins)) + \
                ', Service: ' + service
            service_not_activated_lst.append(service_str)
        return render(request, self.template_name, {
            'formatted_reqs_not_appr': formatted_reqs_not_appr,
            'service_not_activated_lst': service_not_activated_lst})

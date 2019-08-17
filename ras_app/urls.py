from django.conf.urls import url

from . import views
from .views import (
    services_required, home_page, add_new_user, add_self, access_approver, staff_lookup, reject_access,
    action_requests, reason, additional_info, approve, rejected_reason, request_status)

from django.urls import path, include, re_path
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='home_page')),
    path('home/', login_required(home_page.as_view()), name='home_page'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('add-self/', add_self.as_view(), name='add_self'),
    path('add-new-user/', add_new_user.as_view(), name='add_new_user'),
    path('access-approver/', access_approver.as_view(), name='access_approver'),
    path('staff-lookup/', staff_lookup.as_view(), name='staff_lookup'),
    path('services-required/', services_required.as_view(), name='services_required'),
    path('additional-info/', additional_info.as_view(), name='additional_info'),
    path('reason/', reason.as_view(), name='reason'),

    path('action-requests/', login_required(action_requests.as_view()), name='action_requests'),
    url(r'^activate/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    re_path(r'^reject/(?P<token>[0-9A-Za-z]{1,20})/$',
        reject_access.as_view(), name='reject_access'),
    path('access-requests/', login_required(approve.as_view()), name='approve'),
    path('rejected-reason/', rejected_reason.as_view(), name='rejected_reason'),
    path('request-status/', login_required(request_status.as_view()), name='request_status'),
]

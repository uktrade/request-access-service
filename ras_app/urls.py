from django.conf.urls import url

from .views import (
    services_required, home_page, add_new_user, access_approver, staff_lookup,
    action_requests, reason, additional_info, access_requests, rejected_reason,
    request_status, release)

from django.urls import path, include

from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='home_page')),
    path('home/', home_page.as_view(), name='home_page'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('add-new-user/', add_new_user.as_view(), name='add_new_user'),
    path('access-approver/', access_approver.as_view(), name='access_approver'),
    path('staff-lookup/', staff_lookup.as_view(), name='staff_lookup'),
    path('services-required/', services_required.as_view(), name='services_required'),
    path('additional-info/', additional_info.as_view(), name='additional_info'),
    path('reason/', reason.as_view(), name='reason'),
    path('access-requests/', access_requests.as_view(), name='access_requests'),
    path('rejected-reason/', rejected_reason.as_view(), name='rejected_reason'),
    path('action-requests/', action_requests.as_view(), name='action_requests'),
    path('request-status/', request_status.as_view(), name='request_status'),
    path('release/', release.as_view(), name='release'),
]

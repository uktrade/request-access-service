from django.conf.urls import url
from . import views
from django.urls import path, include, re_path
from .views import user_details, home_page, user_end, access_reason, reject_access##, admin_override
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='home_page')),
    path('home/', login_required(home_page.as_view()), name='home_page'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('user-end/', user_end.as_view(), name='user_end'),
    url(r'^action-requests/', views.action_requests, name='action_requests'),

    #path('', landing_page.as_view(), name='landing_page'),
    url(r'^activate/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    re_path(r'^reject/(?P<token>[0-9A-Za-z]{1,20})/$',
        reject_access.as_view(), name='reject_access'),
    #url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,20})/$',
        #views.activate, name='activate'),
    path('user-details/', user_details.as_view(), name='user_details'),
    path('access-reason/', access_reason.as_view(), name='access_reason'),

]

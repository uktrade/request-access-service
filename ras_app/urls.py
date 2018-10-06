from django.conf.urls import url
from . import views
from django.urls import path, include
from .views import user_details, landing_page, user_end, access_reason##, admin_override
from django.contrib.auth.decorators import login_required
from django.conf import settings

urlpatterns = [
    path('landing-page/', login_required(landing_page.as_view()), name='landing_page'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('user-end/', user_end.as_view(), name='user_end'),
    url(r'^action-requests/', views.action_requests, name='action_requests'),

    #path('', landing_page.as_view(), name='landing_page'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('user-details/', user_details.as_view(), name='user_details'),
    path('access-reason/', access_reason.as_view(), name='access_reason'),

]

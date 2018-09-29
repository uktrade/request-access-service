from django.conf.urls import url
from . import views
from django.urls import path, include
from .views import user_details, user_details_behalf, landing_page, user_end

urlpatterns = [
    #url(r'^landing-page/', views.landing_page, name='landing_page'),
    path('landing-page/', landing_page.as_view(), name='landing_page'),
    #url(r'^user-end/', views.user_end, name='user_end'),
    path('user-end/', user_end.as_view(), name='user_end'),
    url(r'^action-requests/', views.action_requests, name='action_requests'),
    #url(r'^user-details/', views.user_details, name='user_details'),
    #url(r'^user-details-behalf/', views.user_details_behalf, name='user_details_behalf'),
    #url(r'^$', views.landing_page, name='landing_page'),
    path('', landing_page.as_view(), name='landing_page'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('user-details/', user_details.as_view(), name='user_details'),
    path('user-details-behalf/', user_details_behalf.as_view(), name='user_details_behalf'),
    #url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        #views.activate, name='activate'),
    #url(r'logs', views.logs, name='logs'),
    #url(r'scan', views.scan, name='scan'),
]

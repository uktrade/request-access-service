from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^landing-page/', views.landing_page, name='landing_page'),
    url(r'^next-page/', views.next_page, name='next_page'),
    url(r'^test/', views.test, name='test'),
    url(r'^access-list/', views.access_list, name='access_list'),
    url(r'^user-details/', views.user_details, name='user_details'),
    url(r'^user-details-behalf/', views.user_details_behalf, name='user_details_behalf'),
    url(r'^$', views.landing_page, name='landing_page'),
    
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    #url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        #views.activate, name='activate'),
    #url(r'logs', views.logs, name='logs'),
    #url(r'scan', views.scan, name='scan'),
]


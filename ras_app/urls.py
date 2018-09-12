from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^your-name/', views.landing_page, name='landing_page'),
    url(r'^next-page/', views.next_page, name='next_page'),
    url(r'^radio/', views.radio, name='radio'),
    url(r'^$', views.landing_page, name='landing_page'),

    #url(r'logs', views.logs, name='logs'),
    #url(r'scan', views.scan, name='scan'),
]

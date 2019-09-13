from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from ras_app.views import admin_override

from core.views import login_redirect_view


urlpatterns = [
    path('admin/login/', admin_override, name='admin_override'),
    path('admin/', admin.site.urls),
    url(r'^', include('ras_app.urls')),
    path('login/redirect/', login_redirect_view, name='login-redirect'),
]

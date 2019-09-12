from django.shortcuts import redirect
from django.urls import resolve
from django.utils.http import is_safe_url
from django.conf import settings


SESSION_LOGIN_REDIRECT_KEY = '_next'


class ProtectAllViewsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if resolve(request.path).app_name != 'authbroker_client' and not request.user.is_authenticated:
            url = request.get_full_path()
            next_url = url if is_safe_url(request.get_full_path(), settings.ALLOWED_HOSTS,
                                          request.is_secure()) else None
            request.session[SESSION_LOGIN_REDIRECT_KEY] = next_url

            return redirect('authbroker_client:login')

        response = self.get_response(request)

        return response

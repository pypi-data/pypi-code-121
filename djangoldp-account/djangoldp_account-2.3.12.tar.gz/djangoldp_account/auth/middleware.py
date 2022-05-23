from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status


class JWTUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the JWTUserMiddleware class.")
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            return

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        try:
            user = auth.authenticate(request)
        except AuthenticationFailed as e:
            return HttpResponse(str(e), status=status.HTTP_401_UNAUTHORIZED)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)

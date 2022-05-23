import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

import jwt
from jwt import DecodeError

from pfx.pfxcore.exceptions import APIError, AuthenticationError
from pfx.pfxcore.models import CacheableMixin

logger = logging.getLogger(__name__)


class JWTTokenDecodeMixin:

    @classmethod
    def get_cached_user(cls, pk):
        UserModel = get_user_model()
        has_cache = issubclass(UserModel, CacheableMixin)
        if (has_cache):
            user = UserModel.cache_get(pk)
            if user:
                return user
        user = UserModel._default_manager.get(pk=pk)
        if (has_cache):
            user.cache()
        return user

    @classmethod
    def decode_jwt(cls, token):
        try:
            opts = ({"require": ["exp"]} if settings.PFX_TOKEN_VALIDITY
                    else {})
            decoded = jwt.decode(
                token, settings.PFX_SECRET_KEY,
                options=opts,
                algorithms="HS256")
            return cls.get_cached_user(decoded['pfx_user_pk'])
        except get_user_model().DoesNotExist:
            raise AuthenticationError(
                message=_('Authentication error'), delete_cookie=True)
        except DecodeError as e:
            logger.exception(e)
            raise AuthenticationError(message=_('Authentication error'))
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(message=_('Token has expired'))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise AuthenticationError(message=_('Authentication error'),
                                      status=500)


class AuthenticationMiddleware(JWTTokenDecodeMixin, MiddlewareMixin):

    def process_request(self, request):
        authorization = request.headers.get('Authorization')
        if authorization:
            try:
                _, key = authorization.split("Bearer ")
            except ValueError:
                key = None
            try:
                request.user = self.decode_jwt(key)
            except APIError as e:
                return e.response
        else:
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()

    def process_response(self, request, response):
        return response


class CookieAuthenticationMiddleware(JWTTokenDecodeMixin, MiddlewareMixin):

    def process_request(self, request):
        key = request.COOKIES.get('token')
        if key:
            try:
                request.user = self.decode_jwt(key)
            except APIError as e:
                return e.response
        else:
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()

    def process_response(self, request, response):
        return response

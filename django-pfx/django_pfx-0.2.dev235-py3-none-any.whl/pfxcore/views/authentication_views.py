import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    password_validation,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

import jwt

from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.exceptions import AuthenticationError
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.models import CacheableMixin
from pfx.pfxcore.shortcuts import delete_token_cookie

from .rest_views import BaseRestView, BodyMixin, CreateRestViewMixin

logger = logging.getLogger(__name__)

UserModel = get_user_model()


@rest_view("/auth")
class AuthenticationView(BodyMixin, BaseRestView):
    token_generator = default_token_generator

    def login_error_response(self):
        raise AuthenticationError()

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/login", public=True, method="post")
    def login(self, *args, **kwargs):
        data = self.deserialize_body()
        user = authenticate(self.request, username=data.get('username'),
                            password=data.get('password'))
        if isinstance(user, CacheableMixin):
            user.cache_delete()
        if user is not None:
            mode = self.request.GET.get('mode', 'jwt')
            return self._login_success(user, mode)
        return self.login_error_response()

    def _login_success(self, user, mode):
        token = self._prepare_token(user)
        if mode == 'cookie':
            if settings.PFX_TOKEN_VALIDITY:
                expires = datetime.utcnow() + timedelta(
                    **settings.PFX_TOKEN_VALIDITY)
            else:
                expires = None

            res = JsonResponse({
                'user': self.get_user_information(user)
            })
            res.set_cookie(
                'token', token, secure=True, expires=expires,
                domain=settings.PFX_COOKIE_DOMAIN, httponly=True,
                samesite='None')
            return res
        else:
            return JsonResponse({
                'token': token,
                'user': self.get_user_information(user)
            })

    @method_decorator(never_cache)
    @rest_api("/logout", public=True, method="get")
    def logout(self, *args, **kwargs):
        return delete_token_cookie(JsonResponse(dict(message="Goodbye")))

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/change-password", method="post")
    def change_password(self, *args, **kwargs):
        data = self.deserialize_body()
        user = authenticate(self.request,
                            username=self.request.user.get_username(),
                            password=data.get('old_password'))
        errors = dict()
        try:
            if user is not None and data.get('new_password'):
                password_validation.validate_password(data['new_password'],
                                                      user)
                user.set_password(data.get('new_password'))
                user.save()
                return JsonResponse({
                    'message': _('password updated successfully')
                })
        except ValidationError as e:
            errors['new_password'] = e.error_list
        if not user:
            errors['old_password'] = [_("Incorrect password")]
        if not data.get('new_password'):
            errors.setdefault('new_password', []).append(
                _("Empty password is not allowed"))
        return JsonResponse(
            ValidationError(errors), status=422)

    def _prepare_token(self, user):
        payload = {
            'pfx_user_pk': user.pk,
        }
        if settings.PFX_TOKEN_VALIDITY:
            exp = datetime.utcnow() + timedelta(**settings.PFX_TOKEN_VALIDITY)
            payload.update(exp=exp)
        payload.update(self.get_extra_payload(user))
        return jwt.encode(
            payload, settings.PFX_SECRET_KEY, algorithm="HS256")

    def get_extra_payload(self, user):
        return {}

    def get_user_information(self, user):
        return {
            'username': user.get_username(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email}

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/set-password", public=True, method="post")
    def set_password(self, *args, **kwargs):
        data = self.deserialize_body()
        assert 'uidb64' in data and 'token' in data

        user = self.get_user(data['uidb64'])

        try:
            if (user is not None and data.get('password') and
                    self.token_generator.check_token(user, data['token'])):
                password_validation.validate_password(data['password'], user)
                user.set_password(data['password'])
                user.is_active = True
                user.save()
                if 'autologin' in data and data['autologin'] in (
                        'jwt', 'cookie'):
                    return self._login_success(user, data['autologin'])

                return JsonResponse({
                    'message': _('password updated successfully')
                })
        except ValidationError as e:
            return JsonResponse(
                ValidationError(dict(password=e.error_list)), status=422)

        if not data.get('password'):
            return JsonResponse(
                ValidationError(dict(
                    password=_("Empty password is not allowed"))), status=422)
        raise AuthenticationError()

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist,
                ValidationError):
            user = None
        return user


class SendMessageTokenMixin:
    email_template_name = None
    subject_template_name = None
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    email_field = 'email'
    language_field = 'language'

    def send_token_message(self, user):
        from django.utils import translation
        lang = str(getattr(user, self.language_field, settings.LANGUAGE_CODE))

        token = self.token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        data = {
            'target_user': user,
            'token': token,
            'uid': uid,
            'reset_url': self.reset_url(token, uid),
            'site_name': settings.PFX_SITE_NAME,
            'user': user,
            **(self.extra_email_context or {})
        }
        with translation.override(lang):
            subject = loader.render_to_string(self.subject_template_name, data)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            body = loader.render_to_string(self.email_template_name, data)
            email_message = EmailMultiAlternatives(
                subject, body, self.from_email,
                [getattr(user, self.email_field)])
            if self.html_email_template_name is not None:
                html_email = loader.render_to_string(
                    self.html_email_template_name, data)
                email_message.attach_alternative(html_email, 'text/html')
            email_message.send()

    def reset_url(self, token, uid):
        return settings.PFX_RESET_PASSWORD_URL.format(
            token=token,
            uid=uid,
        )


@rest_view("/auth/signup")
class SignupView(SendMessageTokenMixin, CreateRestViewMixin, BaseRestView):
    email_template_name = 'registration/welcome_email.txt'
    subject_template_name = 'registration/welcome_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    default_public = True
    model = UserModel
    fields = ['first_name', 'last_name', 'username', 'email']

    def validate(self, obj, **kwargs):
        obj.set_unusable_password()
        super().validate(obj, **kwargs)

    def is_valid(self, obj, created=True):
        r = super().is_valid(obj, created)
        self.send_token_message(obj)
        return r


@rest_view("/auth")
class ForgottenPasswordView(SendMessageTokenMixin, BodyMixin, BaseRestView):
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/forgotten-password", public=True, method="post")
    def forgotten_password(self, *args, **kwargs):
        data = self.deserialize_body()
        if data.get('email'):
            try:
                user = UserModel._default_manager.get(email=data.get('email'))
            except UserModel.DoesNotExist:
                user = None
            if user is not None:
                self.send_token_message(user)
        return JsonResponse({
            'message': _('If the email address you entered is correct, '
                         'you will receive an email from us with '
                         'instructions to reset your password.')
        })

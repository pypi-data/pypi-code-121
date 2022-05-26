import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
import phonenumbers
from twilio.base.exceptions import TwilioRestException
from .forms import *
from .utils import *
from .dispatch import *


__all__ = [
    "Twilio2FAIndexView", "Twilio2FARegisterView", "Twilio2FAChangeView", "Twilio2FAStartView", "Twilio2FAVerifyView",
    "Twilio2FASuccessView", "Twilio2FAFailedView",
]


logger = logging.getLogger("django_twilio_2fa")


class Twilio2FAMixin(object):
    # Session values that should be cleared
    SESSION_VALUES = [
        SESSION_SID, SESSION_TIMESTAMP, SESSION_METHOD,
        SESSION_CAN_RETRY, SESSION_ATTEMPTS,
    ]

    AVAILABLE_METHODS = {
        "sms": {
            "value": "sms",
            "label": "Text Message",
            "icon": "fas fa-sms",
        },
        "voice": {
            "value": "call",
            "label": "Phone Call",
            "icon": "fas fa-phone"
        },
        # "email": {
        #     "value": "email",
        #     "label": "E-mail",
        #     "icon": "fas fa-envelope",
        # },
        "whatsapp": {
            "value": "whatsapp",
            "label": "WhatsApp",
            "icon": "fab fa-whatsapp"
        }
    }

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        allowed_methods = get_setting(
            "ALLOWED_METHODS",
            callback_kwargs={
                "user": request.user
            }
        )

        if allowed_methods is None:
            self.allowed_methods = list(self.AVAILABLE_METHODS.keys())
        elif len(allowed_methods):
            self.allowed_methods = []
            for method in allowed_methods:
                if method not in self.AVAILABLE_METHODS:
                    raise KeyError(
                        f"2FA methods '{method}' is invalid. Must be one of {', '.join(self.AVAILABLE_METHODS.keys())}"
                    )

                method_customization = get_setting(
                    "METHOD_DISPLAY_CB",
                    callback_kwargs={
                        "method": method
                    }
                )

                if method_customization and isinstance(method_customization, dict):
                    if "label" in method_customization:
                        self.AVAILABLE_METHODS[method]["label"] = method_customization["label"]

                    if "icon" in method_customization:
                        self.AVAILABLE_METHODS[method]["icon"] = method_customization["icon"]

                self.allowed_methods.append(method)
        else:
            self.allowed_methods = []

        if request.GET.get("next"):
            self.set_session_value(
                SESSION_NEXT_URL,
                request.GET.get("next")
            )

    def dispatch(self, request, *args, **kwargs):
        view_name = request.resolver_match.view_name.replace(URL_PREFIX + ":", "")

        if view_name in ["failed"]:
            # Always allow these views to be dispatched properly
            pass
        elif not len(self.allowed_methods):
            messages.error(
                request,
                "No verification method is available."
            )
            return self.get_error_redirect(
                can_retry=False
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["is_debug"] = settings.DEBUG
        ctx["is_verification"] = False

        return ctx

    def get_redirect(self, view_name, *args, **kwargs):
        logger.debug(f"Redirecting to: {view_name}")
        return HttpResponseRedirect(
            reverse(f"{URL_PREFIX}:{view_name}", args=args, kwargs=kwargs)
        )

    def get_error_redirect(self, can_retry=False):
        self.set_session_value(SESSION_CAN_RETRY, can_retry)
        return self.get_redirect("failed")

    def handle_twilio_exception(self, exc):
        if exc.code == 20404:
            # Verification not found
            messages.error(
                self.request,
                "The verification has expired. Please try again."
            )
            return self.get_redirect("start")

        raise

    def get_session_value(self, key, default=None):
        key = f"{SESSION_PREFIX}_{key}"
        return self.request.session.get(key, default)

    def set_session_value(self, key, value):
        key = f"{SESSION_PREFIX}_{key}"
        self.request.session[key] = value
        return value

    def clear_session(self):
        for key in self.SESSION_VALUES:
            key_ = f"{SESSION_PREFIX}_{key}"
            if key not in self.request.session:
                continue

            del self.request.session[key_]


class Twilio2FAVerificationMixin(Twilio2FAMixin):
    """
    This mixin should be used once a verification is started or
    in progress.
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.phone_number = get_setting(
            "PHONE_NUMBER_CB",
            callback_kwargs={
                "user": self.request.user
            }
        )

        try:
            self.phone_number = parse_phone_number(self.phone_number)
        except ValidationError:
            self.phone_number = None

    def dispatch(self, request, *args, **kwargs):
        timeout_value = self.get_session_value(SESSION_TIMEOUT)

        if timeout_value:
            timeout_value = datetime.strptime(timeout_value, DATEFMT)

            if timeout_value > datetime.now(tz=timeout_value.tzinfo):
                messages.error(
                    request,
                    "You cannot make another 2FA verification attempt at this time."
                )
                return self.get_error_redirect(can_retry=False)
            else:
                self.clear_session()

        if not self.phone_number:
            messages.warning(
                request,
                "You must add a phone number to your account before proceeding."
            )
            return self.get_redirect("register")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["is_verification"] = True
        ctx["phone_number"] = self.e164_phone_number()
        ctx["formatted_phone_number"] = self.formatted_phone_number()
        ctx["obfuscated_phone_number"] = self.obfuscate_phone_number()

        return ctx

    def e164_phone_number(self):
        if not self.phone_number:
            return None

        return phonenumbers.format_number(
            self.phone_number,
            phonenumbers.PhoneNumberFormat.E164
        )

    def formatted_phone_number(self):
        if not self.phone_number:
            return None

        return phonenumbers.format_number(
            self.phone_number,
            phonenumbers.PhoneNumberFormat.NATIONAL
        )

    def obfuscate_phone_number(self):
        if not self.phone_number:
            return None

        obfuscate_number = get_setting(
            "OBFUSCATE",
            default=True
        )

        if not obfuscate_number:
            return self.formatted_phone_number()

        n = ""

        phone_number = phonenumbers.format_number(
            self.phone_number,
            phonenumbers.PhoneNumberFormat.NATIONAL
        )

        for c in phone_number:
            if c.isdigit():
                n += "X"
            else:
                n += c

        return n[:-4] + self.e164_phone_number()[-4:]

    def update_verification_status(self, status):
        twilio_sid = self.get_session_value(SESSION_SID)

        if not twilio_sid:
            return True

        twilio_2fa_verification_status_changed.send(
            None,
            user=self.request.user,
            phone_number=self.e164_phone_number(),
            method=self.get_session_value(SESSION_METHOD),
            twilio_sid=twilio_sid,
            status=status
        )

        try:
            (get_twilio_client().verify
                .services(get_setting("SERVICE_ID"))
                .verifications(twilio_sid)
                .update(status=status)
             )
        except TwilioRestException as e:
            return self.handle_twilio_exception(e)

        return True

    def approve_verification(self):
        return self.update_verification_status("approved")

    def cancel_verification(self):
        return self.update_verification_status("canceled")


class Twilio2FAIndexView(Twilio2FAMixin, TemplateView):
    template_name = "twilio_2fa/_base.html"

    def get(self, request, *args, **kwargs):
        return self.get_redirect("start")

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class Twilio2FARegistrationFormView(Twilio2FAMixin, FormView):
    form_class = Twilio2FARegistrationForm
    success_url = reverse_lazy("twilio_2fa:start")
    template_name = "twilio_2fa/register.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["is_optional"] = get_setting(
            "REGISTER_OPTIONAL",
            default=False
        )
        ctx["skip_href"] = get_setting(
            "REGISTER_OPTIONAL_URL",
            default="javascript:history.back()"
        )

        return ctx

    def form_valid(self, form):
        phone_number = form.cleaned_data.get("phone_number")

        # This callback should return True or an error message
        updated = get_setting(
            "REGISTER_CB",
            callback_kwargs={
                "user": self.request.user,
                "phone_number": phone_number
            }
        )

        if updated is not True:
            messages.error(
                self.request,
                updated
            )
            return self.get_error_redirect(
                can_retry=False
            )

        return super().form_valid(form)


class Twilio2FARegisterView(Twilio2FARegistrationFormView):
    template_name = "twilio_2fa/register.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["is_optional"] = get_setting(
            "REGISTER_OPTIONAL",
            default=False
        )
        ctx["skip_href"] = get_setting(
            "REGISTER_OPTIONAL_URL",
            default="javascript:history.back()"
        )

        return ctx


class Twilio2FAChangeView(Twilio2FARegistrationFormView):
    template_name = "twilio_2fa/change.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["is_optional"] = False
        ctx["skip_href"] = None

        ctx["can_change"] = get_setting(
            "ALLOW_CHANGE",
            default=True
        )

        if not ctx["can_change"]:
            messages.error(
                self.request,
                "You are not allowed to make changes to your phone number."
            )

        return ctx


class Twilio2FAStartView(Twilio2FAVerificationMixin, TemplateView):
    success_url = reverse_lazy("twilio_2fa:verify")
    template_name = "twilio_2fa/start.html"

    def dispatch(self, request, *args, **kwargs):
        action = request.GET.get("action")

        if not self.phone_number:
            return self.get_redirect("register")

        elif action and action == "retry":
            r = self.retry_action(request, *args, **kwargs)

            if r is not None:
                return r

        if request.method == "GET":
            self.clear_session()

        if request.method == "GET" and len(self.allowed_methods) == 1:
            # If only one option exists, we start the verification and send the user on
            self.send_verification(
                self.allowed_methods[0]
            )

            return HttpResponseRedirect(
                self.success_url
            )

        logger.debug("Start dispatch")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["methods"] = [self.AVAILABLE_METHODS[method] for method in self.allowed_methods]

        return ctx

    def retry_action(self, request, *args, **kwargs):
        elapsed = datetime.now() - datetime.strptime(self.get_session_value(SESSION_TIMESTAMP), DATEFMT)

        min_retry_wait = get_setting(
            "RETRY_TIME",
            default=60 * 3
        )

        if elapsed.total_seconds() < min_retry_wait:
            messages.warning(
                request,
                "Please allow up to 3 minutes before retrying."
            )
            return self.get_redirect("verify")

        method = self.get_session_value(SESSION_METHOD)

        self.cancel_verification()

        if not method:
            return None

        self.send_verification(
            method
        )

        messages.success(
            request,
            "Verification has been re-sent."
        )

        return self.get_redirect("verify")

    def post(self, request, *args, **kwargs):
        method = request.POST.get("method")

        if method not in self.allowed_methods:
            messages.error(
                request,
                "The form has been tampered with. Please don't do that."
            )
            return self.get(request, *args, **kwargs)

        verification_sid = self.send_verification(
            method
        )

        if isinstance(verification_sid, HttpResponseRedirect):
            return verification_sid
        elif verification_sid:
            return HttpResponseRedirect(
                self.success_url
            )

        return self.get(request, *args, **kwargs)

    def send_verification(self, method):
        try:
            verification = (get_twilio_client().verify
                .services(get_setting("SERVICE_ID"))
                .verifications
                .create(
                    to=self.e164_phone_number(),
                    channel=method,
                    custom_friendly_name=get_setting(
                        "SERVICE_NAME",
                        callback_kwargs={
                            "user": self.request.user,
                            "request": self.request,
                            "method": method,
                            "phone_number": self.phone_number
                        }
                    )
                )
            )

            self.set_session_value(SESSION_SID, verification.sid)
            self.set_session_value(SESSION_METHOD, method)
            self.set_session_value(SESSION_TIMESTAMP, datetime.now().strftime(DATEFMT))

            twilio_2fa_verification_sent.send(
                sender=None,
                twilio_sid=self.get_session_value(SESSION_SID),
                user=self.request.user,
                phone_number=self.phone_number,
                method=self.get_session_value(SESSION_METHOD),
                timestamp=self.get_session_value(SESSION_TIMESTAMP)
            )

            return verification.sid
        except TwilioRestException as e:
            if e.code == 60223:
                messages.error(
                    self.request,
                    f"Unable to verify using {self.AVAILABLE_METHODS[method]['label']} at this time. "
                    f"Please try a different method."
                )
                return self.get_redirect("start")

            return self.handle_twilio_exception(e)


class Twilio2FAVerifyView(Twilio2FAVerificationMixin, FormView):
    form_class = Twilio2FAVerifyForm
    success_url = reverse_lazy("twilio_2fa:success")
    template_name = "twilio_2fa/verify.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["method"] = self.get_session_value(SESSION_METHOD)

        return ctx

    def handle_too_many_attempts(self):
        self.cancel_verification()

        timeout = get_setting(
            "MAX_ATTEMPTS_TIMEOUT",
            default=600
        )

        if timeout:
            self.set_session_value(
                SESSION_TIMEOUT,
                datetime.strftime(datetime.now() + timedelta(seconds=int(timeout)), DATEFMT)
            )

        messages.error(
            self.request,
            "You have made too many attempts to verify."
        )

        return self.get_error_redirect(
            can_retry=True if not timeout else False
        )

    def form_valid(self, form):
        try:
            verify = (get_twilio_client().verify
                .services(get_setting("SERVICE_ID"))
                .verification_checks
                .create(
                    to=self.e164_phone_number(),
                    code=form.cleaned_data.get("token")
                )
            )
        except TwilioRestException as e:
            if e.code == 60202:
                # Max tries
                return self.handle_too_many_attempts()

            return self.handle_twilio_exception(e)

        max_attempts = int(get_setting(
            "MAX_ATTEMPTS",
            default=5,
            callback_kwargs={
                "user": self.request.user
            }
        ))

        current_attempts = self.set_session_value(
            SESSION_ATTEMPTS,
            self.get_session_value(SESSION_ATTEMPTS, 0) + 1
        )

        if current_attempts >= max_attempts:
            return self.handle_too_many_attempts()

        if verify.status == "approved":
            # Send this signal manually
            twilio_2fa_verification_status_changed.send(
                None,
                user=self.request.user,
                phone_number=self.e164_phone_number(),
                method=self.get_session_value(SESSION_METHOD),
                twilio_sid=self.get_session_value(SESSION_SID),
                status=verify.status
            )

            twilio_2fa_verification_success.send(
                None,
                user=self.request.user,
                phone_number=self.e164_phone_number(),
                method=self.get_session_value(SESSION_METHOD)
            )

            return super().form_valid(form)

        messages.error(
            self.request,
            "Verification code was invalid"
        )

        return super().form_invalid(form)


class Twilio2FASuccessView(Twilio2FAMixin, TemplateView):
    template_name = "twilio_2fa/success.html"

    def dispatch(self, request, *args, **kwargs):
        next_url = self.get_session_value(
            SESSION_NEXT_URL
        )

        if next_url:
            return HttpResponseRedirect(
                next_url
            )

        verify_success_url = get_setting(
            "VERIFY_SUCCESS_URL"
        )

        if verify_success_url:
            return HttpResponseRedirect(
                verify_success_url
            )

        return super().dispatch(request, *args, **kwargs)


class Twilio2FAFailedView(Twilio2FAMixin, TemplateView):
    template_name = "twilio_2fa/failed.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["can_retry"] = self.get_session_value(SESSION_CAN_RETRY, False)

        if settings.DEBUG and "retry" in self.request.GET:
            ctx["can_retry"] = bool(int(self.request.GET.get("retry", 0)))

        return ctx


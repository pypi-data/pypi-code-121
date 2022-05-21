import logging
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.utils.timezone import now
from j2fa.helpers import j2fa_make_code, j2fa_send_sms

logger = logging.getLogger(__name__)


class TwoFactorSessionManager(models.Manager):
    def archive_old_sessions(self, user: User, current):
        self.filter(user=user).exclude(id=current.id).update(archived=True, active=False)
        current.active = True
        current.archived = False
        current.save()


class TwoFactorSession(models.Model):
    objects = TwoFactorSessionManager()
    created = models.DateTimeField(default=now, db_index=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    user_agent = models.CharField(max_length=512)
    ip = models.GenericIPAddressField(db_index=True)
    phone = models.CharField(max_length=32, db_index=True)
    code = models.CharField(max_length=8, default=j2fa_make_code, blank=True)
    active = models.BooleanField(default=False, db_index=True, blank=True)
    archived = models.BooleanField(default=False, db_index=True, blank=True)

    def __str__(self):
        return "[{}]".format(self.id)

    def is_valid(self, user: User, ip: str, user_agent: str) -> bool:
        return self.user == user and self.ip == ip and self.user_agent == user_agent

    def send_code(self):
        logger.info("2FA: %s -> '%s' (%s)", self.code, self.phone, self.user)
        send_by_email = (
            hasattr(
                settings,
                "J2FA_SEND_TO_EMAIL",
            )
            and settings.J2FA_SEND_TO_EMAIL
        )
        if settings.SMS_TOKEN and self.phone:
            res = j2fa_send_sms(self.phone, self.code)
            if res.status_code >= 300 and hasattr(settings, "EMAIL_HOST") and settings.EMAIL_HOST:
                logger.warning("SMS sending failed to %s (%s), trying to send code by email", self.phone, self.user)
                send_by_email = settings.J2FA_FALLBACK_TO_EMAIL if hasattr(settings, "J2FA_FALLBACK_TO_EMAIL") else True
        if send_by_email and self.user.email:
            logger.info("2FA (email): %s -> %s (%s)", self.code, self.user.email, self.user)
            subject = settings.SMS_SENDER_NAME + ": " + _("One time login code")
            body = _("j2fa.code.email.body").format(code=self.code)
            sender = settings.DEFAULT_FROM_EMAIL
            recipient = self.user.email
            send_mail(subject, body, sender, [recipient], fail_silently=False)

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


# Create your models here.

class UserCompany(models.Model):
    uuid = models.UUIDField("Hub Company UUID", null=True, blank=True)
    name = models.CharField("Hub Company Name", null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = _("User Company")
        verbose_name_plural = _("User Companys")
        db_table = "hub_companies"

    def __str__(self):
        return self.name


class BaseHubUser(models.Model):
    hub_uuid = models.UUIDField("Hub User UUID", null=True, blank=True)
    avatar = models.TextField("Avatar", blank=True, null=True)
    company = models.ForeignKey(
        UserCompany, on_delete=models.CASCADE, related_name="users", null=True
    )

    class Meta:
        abstract = True


class HubOauthToken(models.Model):
    uuid = models.UUIDField(_("User UUID"), editable=False, default=uuid.uuid4)

    access_token = models.TextField(
        "Access Token", blank=True, null=True
    )
    refresh_token = models.TextField(
        "Refresh Token", blank=True, null=True
    )
    expires_in = models.CharField("Expires In", blank=True, null=True, max_length=255)
    expires_in_dt = models.DateTimeField(
        "Expires In DT", blank=True, null=True, max_length=255
    )

    def is_expired(self):
        diff_dates = timezone.now() - self.expires_in_dt
        if abs(diff_dates.days) <= 1:
            return True
        return False

    def __str__(self):
        return "{} {}".format(self.uuid, self.expires_in_dt)

    class Meta:
        verbose_name = _("Hub Oauth Token")
        verbose_name_plural = _("Hub Oauth Tokens")
        db_table = "hub_oauth_token"


class HubUser(models.Model):
    token = models.ForeignKey(
        HubOauthToken,
        verbose_name=_("Tokens"),
        on_delete=models.CASCADE,
        related_name="user",
        null=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Users"), on_delete=models.CASCADE, related_name="tokens", null=True
    )

    class Meta:
        verbose_name = _("Hub User")
        verbose_name_plural = _("Hub Users")
        db_table = "hub_users"

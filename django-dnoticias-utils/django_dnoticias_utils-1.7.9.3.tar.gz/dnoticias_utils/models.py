import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class TrackingCreateUpdateChangesModel(models.Model):
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(_("Modificado em"), auto_now=True, blank=True)

    class Meta:
        abstract = True


class TrackingHistoricalModel(models.Model):
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'),
        null=True,
        blank=True
    )

    user_agent = models.CharField(
        verbose_name=_("User agent"),
        null=True,
        blank=True,
        max_length=256
    )

    class Meta:
        abstract = True


class UUIDTrackingCreateUpdateChangesModel(TrackingCreateUpdateChangesModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

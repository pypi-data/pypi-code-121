from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class SharingConfigsConfig(SingletonModel):
    """
    Config for sharing
    """

    api_endpoint = models.URLField(
        _("api_endpoint"),
        max_length=250,
        help_text=_("Path to API point"),
    )
    api_key = models.CharField(
        _("api_key"),
        max_length=128,
        help_text=_("API key for authorization"),
    )
    label = models.CharField(
        _("label"),
        max_length=50,
        help_text=_("Label"),
    )
    default_organisation = models.CharField(
        _("default organisation"),
        max_length=100,
        blank=True,
        help_text=_("Default organisation"),
    )

    class Meta:
        verbose_name = _("Sharing configuration config")

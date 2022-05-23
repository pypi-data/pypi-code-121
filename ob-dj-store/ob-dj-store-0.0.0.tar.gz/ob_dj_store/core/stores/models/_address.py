from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from ob_dj_store.core.stores.utils import get_data_dict


class BaseAddress(models.Model):
    """
    Base class for all address models.
    """

    address_line = models.CharField(
        max_length=250,
    )
    postal_code = models.CharField(
        max_length=64, help_text=_("The address postal/zip code.")
    )
    city = models.CharField(max_length=120, help_text=_("The address city."))
    region = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=_("The address region, province, or state."),
    )
    country = CountryField(help_text=_("The address country."))
    location = models.PointField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def to_immutable(self):
        """
        Get or create an ImmutableAddress.
        """
        data = get_data_dict(self)
        return ImmutableAddress.from_data_dict(data)


class Address(BaseAddress):
    """
    Reusable addresses model
    """

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")


class ImmutableAddress(BaseAddress):
    """
    Immutable addresses model
    """

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    @classmethod
    def from_data_dict(cls, data):
        """
        Get or create an immutable address with given data dictionary.
        """
        return cls.objects.get_or_create(**data)[0]

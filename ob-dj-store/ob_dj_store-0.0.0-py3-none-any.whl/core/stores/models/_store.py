import typing

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import (
    PaymentMethodManager,
    ShippingMethodManager,
    StoreManager,
)
from ob_dj_store.utils.model import DjangoModelCleanMixin


class ShippingMethod(models.Model):
    """
    Decides how orders should be delivered to the customer.
    """

    class ShippingFeeOptions(models.IntegerChoices):
        """
        Decides how the shipping fees should be calculated.
        """

        FIXED = 1, _("Fixed")
        PER_DISTANCE = 2, _("per distance")
        PER_WEIGHT = 3, _("per weight")

    shipping_fee_option = models.IntegerField(
        choices=ShippingFeeOptions.choices, default=1
    )
    name = models.CharField(max_length=200, help_text=_("Name"))
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    shipping_fee = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ShippingMethodManager()

    class Meta:
        verbose_name_plural = _("Shipping Methods")
        verbose_name = _("Shipping Method")

    def __str__(self):
        return f"Shipping Method {self.name} (PK={self.pk})"


class PaymentMethod(models.Model):
    """
    Payment methods are provided to the customer to select the kind of how
    products are paid.
    """

    payment_provider = models.PositiveSmallIntegerField(
        choices=settings.PAYMENT_PROVIDER_CHOICES,
        default=1,
    )
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=200, help_text=_("Name"))
    description = models.TextField(null=True, blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PaymentMethodManager()

    class Meta:
        verbose_name_plural = _("Payment Methods")
        verbose_name = _("Payment Method")

    def __str__(self):
        return f"Payment Method {self.name} (PK={self.pk})"


class Store(DjangoModelCleanMixin, models.Model):
    name = models.CharField(max_length=100)
    address = models.ForeignKey(
        "stores.address", on_delete=models.PROTECT, related_name="stores"
    )
    location = models.PointField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    poly = models.PolygonField(null=True, blank=True)
    currency = models.CharField(max_length=20)
    shipping_methods = models.ManyToManyField(
        ShippingMethod,
        related_name="shipping_methods",
        blank=True,
        help_text=_("Shipping methods within the store"),
    )
    pickup_addresses = models.ManyToManyField(
        "stores.address",
        related_name="pickup_stores",
        blank=True,
    )
    payment_methods = models.ManyToManyField(
        PaymentMethod,
        related_name="payment_methods",
        blank=True,
        help_text=_("Payment methods within the store"),
    )
    minimum_order_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=10,
        help_text=_("Minimum order amount allowed"),
    )
    delivery_charges = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        help_text=_("This is the shipping cost for the store"),
    )
    min_free_delivery_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        help_text=_("This is the min price to get a free delivery"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreManager()

    class Meta:
        verbose_name_plural = _("Stores")
        verbose_name = _("Store")

    def __str__(self) -> typing.Text:
        return f"Store {self.name} (PK={self.pk})"


class OpeningHours(DjangoModelCleanMixin, models.Model):
    """
    OpeningsHours model linked to Store model
    every store has many opening_hours
    """

    class Weekdays(models.IntegerChoices):
        MONDAY = 1, _("Monday")
        TUESDAY = 2, _("Tuesday")
        WEDNESDAY = 3, _("Wednesday")
        THURSDAY = 4, _("Thursday")
        FRIDAY = 5, _("Friday")
        SATURDAY = 6, _("Saturday")
        SUNDAY = 7, _("Sunday")

    weekday = models.IntegerField(choices=Weekdays.choices)
    from_hour = models.TimeField(help_text=_("Opening hours: From hour "))
    to_hour = models.TimeField(help_text=_("Opening hours: To hour "))
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="opening_hours"
    )

    class Meta:
        ordering = ("weekday", "from_hour")
        unique_together = (
            "weekday",
            "store",
        )

    def __str__(self) -> str:
        return f"Opening hours for store{self.store}"

    def clean(self) -> None:
        super().clean()
        if self.from_hour and self.to_hour and (self.from_hour > self.to_hour):
            raise ValidationError(
                _("From hour should be lower than To hour"), code="invalid"
            )

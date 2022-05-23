from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import OrderManager, OrderPaymentManager
from ob_dj_store.utils.model import DjangoModelCleanMixin


class AbstractPayment(models.Model):
    gateway_id = models.CharField(max_length=32, verbose_name=_("gateway ID"))
    payment_identifier = models.CharField(
        max_length=96, unique=True, verbose_name=_("identifier")
    )

    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        help_text=_("Example 10.800 KWD - Support for 3 decimal"),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class OrderPayment(AbstractPayment):

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderPaymentManager()

    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")

    def __str__(self):
        return f"Payment (PK={self.pk}) for Order {self.order.pk}"


class Order(DjangoModelCleanMixin, models.Model):
    """
    - Represent the order requested by a user
    - it contains order-items
    """

    class OrderStatus(models.TextChoices):
        ACCEPTED = "ACCEPTED", _("accepted")
        CANCELLED = "CANCELLED", _("cancelled")
        PENDING = "PENDING", _("pending")
        PREPARING = "PREPARING", _("preparing")
        READY = "READY", _("ready for pickup")
        DELIVERED = "DELIVERED", _("delivered")
        PAID = "PAID", _("paid")
        OPENED = "OPENED", _("opened")

    # Case of delivery
    customer = models.ForeignKey(
        get_user_model(), related_name="orders", on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        "stores.Store", related_name="orders", on_delete=models.CASCADE
    )
    shipping_method = models.ForeignKey(
        "stores.ShippingMethod", related_name="orders", on_delete=models.CASCADE
    )
    payment_method = models.ForeignKey(
        "stores.PaymentMethod", related_name="orders", on_delete=models.CASCADE
    )
    payment = models.ForeignKey(
        settings.ORDER_PAYMENT_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  # Payment for this order
    shipping_address = models.ForeignKey(
        "stores.address", on_delete=models.PROTECT, related_name="orders"
    )
    immutable_shipping_address = models.ForeignKey(
        "stores.ImmutableAddress", on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=32,
        default=OrderStatus.PENDING,
        choices=OrderStatus.choices,
    )
    # TODO: add pick_up_time maybe ?
    # audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order {self.pk} with total amount {self.total_amount}"

    @property
    def total_amount(self):

        return Decimal(
            sum(map(lambda item: Decimal(item.total_amount) or 0, self.items.all()))
        )

    @property
    def preparation_time(self):
        # sum of durations of all items in minutes
        return sum(map(lambda item: item.preparation_time, self.items.all()))

    def save(self, **kwargs):
        if not self.pk:
            self.immutable_shipping_address = self.shipping_address.to_immutable()
        return super().save(**kwargs)


class OrderItem(DjangoModelCleanMixin, models.Model):
    """OrderItem is detailed items of a given order, an order
    can contain one or more items purchased in the same transaction
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "stores.ProductVariant",
        null=True,
        on_delete=models.SET_NULL,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1,
                message="Can you please provide a valid quantity !",
            )
        ],
        help_text=_("quantity of the variant"),
    )

    def __str__(self):
        return f"OrderItem - {self.quantity} {self.variant.name}"

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    @property
    def total_amount(self):
        return self.variant.price * self.quantity

    @property
    def preparation_time(self):
        return (self.variant.preparation_time.total_seconds() * self.quantity) / 60

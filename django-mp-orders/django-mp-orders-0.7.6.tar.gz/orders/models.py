
from django.apps import apps
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from exchange.models import format_printable_price, MultiCurrencyPrice
from delivery.models import DeliveryMethodField

from orders.constants import (
    PAYMENT_METHODS,
    ORDER_STATUSES,
    ORDER_STATUS_NEW,
    PAYMENT_METHOD_PRIVAT24
)


def _generate_hash():
    return get_random_string(length=10)


class Order(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders',
        verbose_name=_('Owner'), null=True, blank=True,
        on_delete=models.SET_NULL)

    status = models.CharField(
        _('Status'),
        max_length=100,
        choices=ORDER_STATUSES,
        default=ORDER_STATUS_NEW)

    payment_method = models.CharField(
        _('Payment method'),
        max_length=100,
        choices=PAYMENT_METHODS)

    delivery = DeliveryMethodField()

    first_name = models.CharField(_('First name'), max_length=255)

    last_name = models.CharField(_('Last name'), max_length=255)

    middle_name = models.CharField(
        _('Middle name'), max_length=255, blank=True)

    address = models.CharField(_('Address'), max_length=255, blank=True)

    mobile = models.CharField(_('Mobile number'), max_length=255)

    created = models.DateTimeField(
        _('Date created'), auto_now_add=True, editable=False)

    comment = models.TextField(_('Comment'), max_length=1000, blank=True)

    hash = models.CharField(
        max_length=10,
        default=_generate_hash,
        unique=True)

    def __str__(self):
        return self.printable_name

    @property
    def printable_name(self):
        return '{} #{}'.format(_('Order'), self.id)

    @property
    def full_name(self):
        return '{} {} {}'.format(
            self.last_name, self.first_name, self.middle_name)

    @property
    def total(self):
        return sum([i.subtotal for i in self.items.all()])

    @property
    def printable_total(self):
        return format_printable_price(self.total)

    @property
    def delivery_method(self):
        return self.delivery.name

    def is_liqpay_payment(self):
        return self.is_paynow_form_visible() and apps.is_installed('liqpay')

    def is_paynow_form_visible(self):
        return self.payment_method == PAYMENT_METHOD_PRIVAT24

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class OrderedProduct(MultiCurrencyPrice):

    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        related_name='items',
        on_delete=models.CASCADE)

    product = models.ForeignKey(
        'products.Product',
        verbose_name=_('Product'),
        related_name='order_items',
        on_delete=models.CASCADE)

    qty = models.PositiveIntegerField(_('Quantity'), default=1)

    def __str__(self):
        return str(self.product)

    @property
    def subtotal(self):
        return self.price * self.qty

    def printable_subtotal(self):
        return format_printable_price(self.subtotal)

    class Meta:
        verbose_name = _('Ordered product')
        verbose_name_plural = _('Ordered products')

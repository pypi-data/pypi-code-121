
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ordered_model.models import OrderedModel
from ckeditor.fields import RichTextField

from exchange.models import CurrencyField


class Supplier(models.Model):

    name = models.CharField(_('Supplier name'), max_length=255)

    short_name = models.CharField(_('Short name'), max_length=255)

    code = models.CharField(_('Code'), max_length=255, unique=True)

    country = models.CharField(_('Country'), max_length=255, blank=True)

    currency = CurrencyField()

    delivery_info = RichTextField(_('Delivery info'), blank=True)

    email = models.EmailField(_('Email'), max_length=255, blank=True)

    discount = models.IntegerField(_('Discount, %'), blank=True, null=True)

    markup = models.IntegerField(_('Mark-up, %'), blank=True, null=True)

    price_updated = models.DateTimeField(
        _('Price updated date'), blank=True, editable=False, null=True)

    is_visible_for_unregistered_users = models.BooleanField(
        _('Is visible for unregistered users'), default=True)

    @property
    def warehouse_count(self):
        return self.warehouses.count()

    warehouse_count.fget.short_description = _('Warehouse count')

    def __str__(self):
        return self.name

    def clean_products(self):
        return self.products.all().delete()

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')


class SupplierWarehouse(OrderedModel):

    supplier = models.ForeignKey(
        Supplier,
        verbose_name=_('Supplier'),
        related_name='warehouses',
        on_delete=models.CASCADE)

    name = models.CharField(_('Warehouse name'), max_length=255)

    short_name = models.CharField(_('Short name'), max_length=255)

    price_updated = models.DateTimeField(
        _('Price updated date'), blank=True, editable=False, null=True)

    order_with_respect_to = 'supplier'

    def __str__(self):
        return '{} - {}'.format(str(self.supplier), self.name)

    class Meta(OrderedModel.Meta):
        verbose_name = _('Supplier warehouse')
        verbose_name_plural = _('Supplier warehouses')


class SupplierField(models.ForeignKey):

    def __init__(
            self,
            to=Supplier,
            verbose_name=_('Supplier'),
            blank=True,
            null=True,
            on_delete=models.PROTECT,
            **kwargs):

        super().__init__(
            to=to,
            verbose_name=verbose_name,
            blank=blank,
            null=null,
            on_delete=on_delete,
            **kwargs)

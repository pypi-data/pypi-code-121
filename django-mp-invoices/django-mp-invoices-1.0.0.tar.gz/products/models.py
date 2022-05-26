
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from categories.models import CategoryField
from manufacturers.models import ManufacturerField
from stock.models import Stock, UnitType
from product_barcode.models import BarCodeField, BarCode

from tecdoc.models import AdditionalCodesField
from tecdoc.utils import clean_code

from exchange.models import MultiCurrencyPrice, subscribe_on_exchange_rates
from exchange.constants import CURRENCY_UAH

from products.managers import ProductManager


@subscribe_on_exchange_rates
class Product(MultiCurrencyPrice, Stock, UnitType):

    is_active = models.BooleanField(_('Is active'), default=True)

    manufacturer = ManufacturerField(related_name='products')

    category = CategoryField(related_name='products')

    name = models.CharField(
        _('Product name'), max_length=255, blank=True, db_index=True)

    code = models.CharField(_('Code'), max_length=255, blank=True)

    clean_code = models.CharField(max_length=255, db_index=True)

    bar_code = BarCodeField()

    additional_codes = AdditionalCodesField()

    warehouse = models.CharField(_('Warehouse location'), max_length=255, blank=True)

    created = models.DateTimeField(
        _('Creation date'), auto_now_add=True, null=True, editable=False)

    objects = ProductManager()

    search_fields = ['name', 'clean_code', 'bar_code', 'additional_codes']

    def get_absolute_url(self):
        return reverse_lazy('admin:products_product_change', args=[self.pk])

    def save(self, **kwargs):
        self.clean_code = clean_code(self.code)

        if not self.bar_code:
            self.bar_code = BarCode.get_solo().get_next_code()

        return super().save(**kwargs)

    def __str__(self):
        return self.name

    @property
    def price(self):
        price = super().price

        if self.currency == CURRENCY_UAH:
            return round(price)

        return price

    @property
    def subtotal(self):
        return self.price * self.stock

    def serialize(self):
        return {
            'id': self.pk,
            'stock': self.stock
        }

    class Meta:
        ordering = ['-id']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

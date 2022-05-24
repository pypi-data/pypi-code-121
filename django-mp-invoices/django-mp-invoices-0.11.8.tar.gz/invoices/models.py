
from django.utils.functional import cached_property
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from invoices.conf import IS_ROUNDING_ENABLED
from customers.models import CustomerField, Customer
from suppliers.models import SupplierField, Supplier
from managers.models import ManagerField, Manager

from exchange.utils import get_price_factory
from exchange.constants import CURRENCY_UAH
from exchange.models import MultiCurrencyPrice


class InvoiceField(models.ForeignKey):

    def __init__(
            self,
            to,
            verbose_name=_('Invoice'),
            on_delete=models.CASCADE,
            related_name='items',
            *args, **kwargs):

        super().__init__(
            to=to,
            verbose_name=verbose_name,
            on_delete=on_delete,
            related_name=related_name,
            *args, **kwargs)


class InvoiceTypeField(models.PositiveIntegerField):

    def __init__(
            self,
            choices,
            verbose_name=_('Type'),
            *args, **kwargs):

        super().__init__(
            choices=choices,
            verbose_name=verbose_name,
            *args, **kwargs
        )


class Invoice(models.Model):

    type = NotImplemented
    customer = NotImplemented
    manager = NotImplemented

    creator = models.ForeignKey(
        get_user_model(),
        verbose_name=_('Creator'),
        on_delete=models.PROTECT)

    created = models.DateTimeField(_('Creation date'), auto_now_add=True)

    discount = models.PositiveIntegerField(
        verbose_name=_('Discount, %'),
        default=0)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._old_type = self.type

    @transaction.atomic
    def update(self, data):

        if 'manager' in data:
            if data['manager']:
                self.manager = Manager.objects.get(pk=data['manager'])
            else:
                self.manager = None

        if 'customer' in data:
            if data['customer']:
                self.customer = Customer.objects.get(pk=data['customer'])
            else:
                self.customer = None
            self.discount = self.customer_discount

        if 'discount' in data:
            self.discount = int(data['discount'])

        self.save()

    def save(self, **kwargs):
        if self.type != self._old_type:
            self.created = timezone.now()
        super().save(**kwargs)

    def __str__(self):
        return str(self.created)

    @classmethod
    def create(cls, type):
        return cls.objects.create(type=type)

    @property
    def customer_name(self):
        if self.customer:
            return self.customer.name
        return ''

    @property
    def manager_name(self):
        if self.manager:
            return self.manager.name
        return ''

    @property
    def invoice_type(self):
        return self.__class__.__name__.lower()

    @property
    def manage_url(self):
        return self._get_url('manage')

    @property
    def print_url(self):
        return self._get_url('print')

    @property
    def update_url(self):
        return self._get_url('update')

    @property
    def add_item_url(self):
        return self._get_url('add-item')

    def _get_url(self, name):
        return reverse_lazy('invoices:' + name, args=[
            self.invoice_type,
            self.pk
        ])

    @property
    def model_name(self):
        return self._meta.verbose_name

    @transaction.atomic
    def add_item(self, product, qty=1, update_product=True):
        try:
            item = self.items.get(product=product)
            item.qty += qty
            item.save()

        except ObjectDoesNotExist:
            item = self.items.create(
                product=product,
                qty=qty,
                **product.price_values
            )

        self._handle_add_item(product, qty, update_product=update_product)

        return item

    def _handle_add_item(self, product, qty, update_product):
        pass

    @transaction.atomic
    def remove_item(self, item_id):

        item = self.get_item(item_id)

        self._handle_remove_item(item)

        product = item.product

        item.delete()

        return product

    def _handle_remove_item(self, item):
        pass

    @property
    def total(self):
        return sum([i.subtotal for i in self.items.all()])

    @property
    def discounted_total(self):
        return self.calculate_discount(self.total)

    @property
    def total_with_discount(self):
        return self.total - self.discounted_total

    @property
    def total_qty(self):
        return sum([i.qty for i in self.items.all()])

    @property
    def customer_discount(self):

        if self.customer:
            return self.customer.discount

        return 0

    def calculate_discount(self, number):

        if not self.discount:
            return 0

        return (self.discount * number) / 100.0

    def serialize_totals(self):
        return {
            'grand_total': self.total,
            'discount_percentage': self.discount,
            'discounted_total': self.discounted_total,
            'total_with_discount': self.total_with_discount
        }

    def get_item(self, item_id):
        return self.items.select_related('product').get(pk=item_id)

    def get_items(self):
        return self.items.all().order_by('-id')

    def get_services(self):
        return self.services.all().order_by('-id')

    class Meta:
        abstract = True


class InvoiceItem(MultiCurrencyPrice):

    invoice = NotImplemented

    product = models.ForeignKey(
        'products.Product',
        verbose_name=_('Product'),
        on_delete=models.CASCADE)

    qty = models.FloatField(_('Quantity'))

    @transaction.atomic
    def update(self, data):

        if 'qty' in data:
            self._set_qty(float(data['qty']))

        if 'price' in data:
            self._set_price(float(data['price']))

        self.save()

    def _set_qty(self, value):
        self.qty = value

    def _set_price(self, value):
        self.initial_currency = CURRENCY_UAH
        self.price_retail = value

    def get_qty_input_value(self):
        return str(self.qty).replace(',', '')

    def set_rates(self, rates):
        self.rates = rates

    @cached_property
    def customer_name(self):
        return self.invoice.customer_name

    @cached_property
    def product_name(self):
        return self.product.name

    @property
    def bar_code(self):
        return self.product.bar_code

    @property
    def api_url(self):
        return reverse_lazy('invoices:item', args=[
            self.invoice.invoice_type,
            self.invoice.pk,
            self.pk
        ])

    def calculate_discount(self, number):
        return self.invoice.calculate_discount(number)

    @property
    def price(self):
        price = super().price

        if IS_ROUNDING_ENABLED and self.currency == CURRENCY_UAH:
            return round(price)

        return price

    @property
    def price_with_discount(self):
        return self.price - self.calculate_discount(self.price)

    @property
    def subtotal(self):
        return self.price * self.qty

    @property
    def discounted_subtotal(self):
        return self.calculate_discount(self.subtotal)

    @property
    def subtotal_with_discount(self):
        return self.price_with_discount * self.qty

    @property
    def price_wholesale_uah(self):
        return get_price_factory(
            self.rates,
            self.initial_currency,
            CURRENCY_UAH
        )(self.price_wholesale)

    @property
    def wholesale_subtotal_uah(self):
        return self.price_wholesale_uah * self.qty

    @property
    def profit_uah(self):
        return self.price_with_discount - self.price_wholesale_uah

    @property
    def profit_subtotal_uah(self):
        return self.subtotal_with_discount - self.wholesale_subtotal_uah

    @property
    def printable_qty(self):
        if hasattr(self.product, 'format_qty'):
            return self.product.format_qty(self.qty)

        return self.qty

    def render(self):
        return render_to_string('invoices/item.html', {'object': self})

    def serialize_product(self):
        return self.product.serialize()

    class Meta:
        abstract = True


class Arrival(Invoice):

    TYPE_INCOME = 1
    TYPE_RETURN = 2
    TYPE_CUSTOM = 3

    TYPES = (
        (TYPE_INCOME, _('Income')),
        (TYPE_RETURN, _('Return')),
        (TYPE_CUSTOM, _('Custom')),
    )

    type = InvoiceTypeField(TYPES)

    customer = CustomerField(related_name='arrivals')

    supplier = SupplierField(related_name='arrivals')

    manager = ManagerField(related_name='arrivals')

    def update(self, data):

        if 'supplier' in data:
            if data['supplier']:
                self.supplier = Supplier.objects.get(pk=data['supplier'])
            else:
                self.supplier = None

        super().update(data)

    def _handle_add_item(self, product, qty, update_product):

        if update_product:
            product.add_stock(value=qty)

    def _handle_remove_item(self, item):

        if item.qty > 0:
            item.product.subtract_stock(item.qty)

    class Meta:
        verbose_name = _('Arrival invoice')
        verbose_name_plural = _('Arrival invoices')


class ArrivalItem(InvoiceItem):

    invoice = InvoiceField(Arrival)

    def _set_qty(self, value):

        if self.qty > value:
            self.product.subtract_stock(self.qty - value)

        if self.qty < value:
            self.product.add_stock(value - self.qty)

        super()._set_qty(value)

    def _set_price(self, value):
        super()._set_price(value)
        if hasattr(self.product, 'handle_arrival_item_price_change'):
            self.product.handle_arrival_item_price_change(value)


class Sale(Invoice):

    TYPE_CASH_REGISTER = 1
    TYPE_WRITE_OFF = 2
    TYPE_ONLINE = 3
    TYPE_CUSTOM = 4
    TYPE_DEBT = 5
    TYPE_IN_PROCESS = 6

    TYPES = (
        (TYPE_CASH_REGISTER, _('Cash register')),
        (TYPE_WRITE_OFF, _('Write off')),
        (TYPE_DEBT, _('Debt')),
        (TYPE_IN_PROCESS, _('In process')),
        (TYPE_CUSTOM, _('Custom')),
        (TYPE_ONLINE, _('Online')),
    )

    type = InvoiceTypeField(TYPES)

    customer = CustomerField(related_name='sales')

    manager = ManagerField(related_name='sales')

    def _handle_add_item(self, product, qty, update_product):

        if update_product:
            product.subtract_stock(value=qty)

    def _handle_remove_item(self, item):

        if item.qty > 0:
            item.product.add_stock(item.qty)

    @property
    def service_total(self):
        return sum([s.subtotal for s in self.services.all()])

    def update(self, data):

        super().update(data)

        if 'customer' in data:
            self.services.all().update(customer=data['customer'])

    def serialize_totals(self):
        totals = super().serialize_totals()
        totals['service_total'] = self.service_total
        return totals

    class Meta:
        verbose_name = _('Sales invoice')
        verbose_name_plural = _('Sales invoices')


class SaleItem(InvoiceItem):

    invoice = InvoiceField(Sale)

    def _set_qty(self, value):

        if value > self.qty:
            self.product.subtract_stock(value - self.qty)

        if value < self.qty:
            self.product.add_stock(self.qty - value)

        super()._set_qty(value)

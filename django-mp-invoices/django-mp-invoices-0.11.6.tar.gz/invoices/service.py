
from datetime import datetime, time

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from exchange.models import ExchangeRates
from invoices.models import Arrival, Sale


class InvoicesService(object):

    def __init__(self, user):
        self._user = user
        self._check_access()

    def create_invoice(self, invoice_type, inner_type):
        model = self._get_invoice_model(invoice_type)
        return model.objects.create(type=inner_type, creator=self._user)

    def get_invoice(self, invoice_type, invoice_id):

        model = self._get_invoice_model(invoice_type)

        try:
            return model.objects.get(pk=invoice_id)
        except ObjectDoesNotExist:
            raise Exception(_('Invoice not found'))

    def get_sale(self, sale_id):
        return self.get_invoice('sale', sale_id)

    def get_invoice_items(
            self,
            invoice_type,
            date_from,
            date_to,
            category=None,
            exclude_categories=None,
            manager=None):

        model = self._get_invoice_model(invoice_type)

        invoices = model.objects.filter(
            created__date__range=[date_from, date_to]
        ).prefetch_related(
            'items',
            'items__product'
        )

        if category is not None:
            invoices = invoices.filter(type=category)

        if manager is not None:
            invoices = invoices.filter(manager=manager)

        if exclude_categories is not None:
            invoices = invoices.exclude(type__in=exclude_categories)

        invoices = invoices.order_by('created')

        result = []
        rates = ExchangeRates.objects.get()

        for invoice in invoices:
            for item in invoice.items.all().select_related('invoice'):
                item.set_rates(rates)
                result.append(item)

        return result

    def get_invoice_totals(self, items):
        return {
            'qty': sum([i.qty for i in items]),
            'wholesale_total': sum([i.wholesale_subtotal_uah for i in items]),
            'retail_total': sum([i.subtotal_with_discount for i in items]),
            'discounted_retail_total': sum(
                [i.discounted_subtotal for i in items]),
            'profit_total': sum([i.profit_subtotal_uah for i in items])
        }

    def handle_product_change(self, product):
        self._handle_product_stock_change(product)

    def _handle_product_stock_change(self, product):

        difference = product.stock - product.initial_stock

        if not difference:
            return

        if difference > 0:
            self._create_arrival_for_product(product, difference)
        else:
            self._create_write_off_for_product(product, abs(difference))

    def _create_arrival_for_product(self, product, qty):

        arrival = self._get_todays_invoice(Arrival, Arrival.TYPE_INCOME)

        arrival.add_item(product, qty=qty, update_product=False)

    def _create_write_off_for_product(self, product, qty):

        sale = self._get_todays_invoice(Sale, Sale.TYPE_WRITE_OFF)

        sale.add_item(product, qty=qty, update_product=False)

    def _get_todays_invoice(self, model, invoice_type):

        today = timezone.now().date()
        today_min = timezone.make_aware(datetime.combine(today, time.min))
        today_max = timezone.make_aware(datetime.combine(today, time.max))

        params = {
            'creator': self._user,
            'type': invoice_type
        }

        try:
            return model.objects.filter(
                created__range=(today_min, today_max), **params)[0]
        except IndexError:
            return model.objects.create(**params)

    def _get_invoice_model(self, invoice_type):

        models = {
            'sale': Sale,
            'arrival': Arrival
        }

        try:
            return models[invoice_type]
        except KeyError:
            raise Exception('Unknown invoice type: {}'.format(invoice_type))

    def _check_access(self):
        if not self._user.is_staff:
            raise Exception(_('Access denied'))

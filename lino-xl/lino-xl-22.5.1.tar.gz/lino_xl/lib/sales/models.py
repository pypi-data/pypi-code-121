# -*- coding: UTF-8 -*-
# Copyright 2008-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models

from lino.api import dd, rt, _
from etgen.html import E
from lino.utils.mldbc.mixins import BabelNamed
# from lino.mixins.periods import DateRange

from lino_xl.lib.ledger.mixins import Matching, SequencedVoucherItem
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.choicelists import TradeTypes
from lino_xl.lib.invoicing.mixins import InvoiceGenerator
from .mixins import SalesDocument, ProductDocItem

TradeTypes.sales.update(
    price_field_name='sales_price',
    price_field_label=_("Sales price"),
    base_account_field_name='sales_account',
    base_account_field_label=_("Sales account"))


class PaperType(BabelNamed):

    templates_group = 'sales/VatProductInvoice'

    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'PaperType')
        verbose_name = _("Paper type")
        verbose_name_plural = _("Paper types")

    template = models.CharField(_("Template"), max_length=200, blank=True)

    @dd.chooser(simple_values=True)
    def template_choices(cls):
        bm = rt.models.printing.BuildMethods.get_system_default()
        return rt.find_template_config_files(
            bm.template_ext, cls.templates_group)


class VatProductInvoice(SalesDocument, Matching):
    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'VatProductInvoice')
        verbose_name = _("Sales invoice")
        verbose_name_plural = _("Sales invoices")

    quick_search_fields = "partner__name subject"

    # show_items = dd.ShowSlaveTable('sales.ItemsByInvoice')

    # make_copy = MakeCopy()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(VatProductInvoice, cls).get_registrable_fields(site):
            yield f
        yield 'due_date'
        # yield 'order'
        yield 'voucher_date'
        yield 'entry_date'
        yield 'user'
        # yield 'item_vat'

    def get_print_items(self, ar):
        dv = rt.models.resolve(dd.plugins.sales.print_items_table)
        return dv.request(self)

    @dd.virtualfield(dd.PriceField(_("Balance to pay")))
    def balance_to_pay(self, ar):
        Movement = rt.models.ledger.Movement
        qs = Movement.objects.filter(
            partner=self.get_partner(),
            cleared=False,
            match=self.get_match())
        return Movement.get_balance(self.journal.dc.opposite(), qs)

    @dd.virtualfield(dd.PriceField(_("Balance before")))
    def balance_before(self, ar):
        Movement = rt.models.ledger.Movement
        qs = Movement.objects.filter(
            partner=self.get_partner(),
            cleared=False,
            value_date__lte=self.entry_date)
        qs = qs.exclude(voucher=self)
        return Movement.get_balance(self.journal.dc.opposite(), qs)



class InvoiceItem(ProductDocItem, SequencedVoucherItem, InvoiceGenerator):
    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'InvoiceItem')
        verbose_name = _("Sales invoice item")
        verbose_name_plural = _("Sales invoice items")

    voucher = dd.ForeignKey(
        'sales.VatProductInvoice', related_name='items')
    title = models.CharField(_("Heading"), max_length=200, blank=True)
    # ship_ref = models.CharField(
    #     _("Shipment reference"), max_length=200, blank=True)
    # ship_date = models.DateField(_("Shipment date"), blank=True, null=True)

    @classmethod
    def get_generators_for_plan(cls, plan, partner=None):
        jnls = [o.source_journal
            for o in rt.models.invoicing.FollowUpRule.objects.filter(
                target_journal=plan.area.journal)]
        if len(jnls):
            qs = cls.objects.filter(voucher__journal__in=jnls)
            if partner is not None:
                qs = qs.filter(voucher__partner=partner)
            return qs
        return []
        # trs = rt.models.invoicing.FollowUpRule.objects.filter(
        #     target_journal=plan.area.journal)
        # if trs.exist():
        # jnls = []
        # for tr in trs:
        #     trs = trs.filter(from_state=)
        #     tr.from_state
        #     qs = cls.objects.filter(voucher__journal__in=jnls)
        #     yield qs

    def get_invoiceable_product(self, max_date=None):
        return self.product

    def get_invoiceable_qty(self):
        return self.qty

    def get_invoiceable_title(self, number=None):
        return self.title

    def get_invoiceable_end_date(self):
        return None

    # def get_invoiceable_start_date(self, max_date):
    #     # don't look at events before this date.
    #     return None
    #
    def get_invoiceable_events(self, start_date, max_date):
        return []

    def get_invoiceable_free_events(self):
        return 0

    def get_invoiceable_partner(self):
        return self.voucher.partner

    def get_invoiceable_payment_term(self):
        return None

    def get_invoiceable_paper_type(self):
        return None

    def setup_invoice_from_suggestion(self, invoice, plan, info):
        if info.invoicing_max_date is not None:
            invoice.invoicing_min_date = info.invoicing_min_date
            invoice.invoicing_max_date = info.invoicing_max_date
        else:
            invoice.invoicing_min_date = plan.min_date
            invoice.invoicing_max_date = plan.get_max_date()

    def setup_invoice_item(self, item):
        pass


from .ui import *

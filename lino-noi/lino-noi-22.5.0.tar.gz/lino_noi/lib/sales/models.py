# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_xl.lib.sales.models import *
from lino.api import _


class InvoiceDetail(InvoiceDetail):
    panel1 = dd.Panel("""
    entry_date
    #order subject
    payment_term
    due_date:20
    invoicing_min_date invoicing_max_date
    """)


class InvoiceItemDetail(InvoiceItemDetail):

    main = """
    seqno product discount
    unit_price qty total_base total_vat total_incl
    title
    invoiceable_type:15 invoiceable_id:15 invoiceable:50
    description
    """


# VatProductInvoice.print_items_table = ItemsByInvoicePrintNoQtyColumn

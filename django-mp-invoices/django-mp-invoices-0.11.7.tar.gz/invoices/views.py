
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from cap.decorators import admin_render_view

from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response

from invoices import forms
from invoices.conf import IS_PRODUCT_SELECT_COLLAPSED
from invoices.models import Sale, Arrival

from apps.products.models import Product


@staff_member_required
def create_invoice(request, invoice_type):

    invoice = request.invoices.create_invoice(
        invoice_type, request.POST['type'])

    return redirect(invoice.manage_url)


@admin_render_view('invoices/manage.html')
def manage_invoice(request, invoice_type, invoice_id):

    invoice = request.invoices.get_invoice(invoice_type, invoice_id)

    expire_date = datetime.now().date() - timedelta(days=1)

    if not request.user.is_superuser and invoice.created.date() < expire_date:
        return HttpResponseForbidden(_('You can manage today`s invoices only'))

    return {
        'invoice': invoice,
        'invoice_type': invoice_type,
        'form': forms.ManageInvoiceForm(invoice),
        'is_product_select_collapsed': IS_PRODUCT_SELECT_COLLAPSED
    }


@api_view(['POST'])
def update_invoice(request, invoice_type, invoice_id):

    invoice = request.invoices.get_invoice(invoice_type, invoice_id)
    invoice.update(request.data)

    return Response({
        'message': _('Invoice updated'),
        'total': invoice.serialize_totals()
    })


@api_view(['POST'])
def add_item(request, invoice_type, invoice_id):

    try:
        invoice = request.invoices.get_invoice(invoice_type, invoice_id)
        product = Product.objects.get(pk=request.data['product'])
        item = invoice.add_item(product)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    return Response({
        'status': 'OK',
        'html': item.render(),
        'item_id': item.id,
        'product': item.serialize_product(),
        'total': invoice.serialize_totals()
    })


class ItemAPI(APIView):

    def post(self, request, invoice_type, invoice_id, item_id):

        invoice = request.invoices.get_invoice(invoice_type, invoice_id)

        item = invoice.get_item(item_id)

        try:
            item.update(request.data)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        return Response({
            'message': _('Item updated'),
            'product': item.serialize_product(),
            'total': invoice.serialize_totals()
        })

    def delete(self, request, invoice_type, invoice_id, item_id):

        if not request.user.is_superuser:
            return HttpResponseForbidden(_('You can`t delete sale items'))

        invoice = request.invoices.get_invoice(invoice_type, invoice_id)

        product = invoice.remove_item(item_id)

        return Response({
            'message': _('Item removed'),
            'product': product.serialize(),
            'total': invoice.serialize_totals()
        })


@admin_render_view(template_name='invoices/print.html')
def print_invoice(request, invoice_type, invoice_id):
    return {
        'invoice': request.invoices.get_invoice(invoice_type, invoice_id),
        'invoice_type': invoice_type
    }


def get_report(request, invoice_type):

    handlers = {
        'sale': get_sale_report,
        'arrival': get_arrival_report
    }

    try:
        handler = handlers[invoice_type]
    except KeyError:
        raise Exception('Unknown invoice type: {}'.format(invoice_type))

    return handler(request)


@admin_render_view(template_name='invoices/report/sale-report.html')
def get_sale_report(request):

    form = forms.ReportForm(request.GET)

    date_from = form.cleaned_data['date_from']
    date_to = form.cleaned_data['date_to']

    invoices = request.invoices

    items = invoices.get_invoice_items(
        'sale',
        date_from,
        date_to,
        exclude_categories=[
            Sale.TYPE_CUSTOM,
            Sale.TYPE_DEBT,
            Sale.TYPE_WRITE_OFF
        ])

    totals = invoices.get_invoice_totals(items)

    return_items = invoices.get_invoice_items(
        'arrival',
        date_from,
        date_to,
        category=Arrival.TYPE_RETURN)

    return_totals = invoices.get_invoice_totals(return_items)

    write_off_items = invoices.get_invoice_items(
        'sale',
        date_from,
        date_to,
        category=Sale.TYPE_WRITE_OFF)

    write_off_totals = invoices.get_invoice_totals(write_off_items)

    return {
        'form': form,
        'items': items,
        'totals': totals,
        'return_items': return_items,
        'return_totals': return_totals,
        'write_off_items': write_off_items,
        'write_off_totals': write_off_totals,
        'grand_totals': {
            'qty': totals['qty'] - return_totals['qty'],
            'wholesale_total': (
                totals['wholesale_total'] -
                return_totals['wholesale_total']),
            'retail_total': (
                totals['retail_total'] - return_totals['retail_total']),
            'profit_total': (
                totals['profit_total'] - return_totals['profit_total'])
        },
        **form.cleaned_data
    }


@admin_render_view(template_name='invoices/report/arrival-report.html')
def get_arrival_report(request):

    form = forms.ReportForm(request.GET)

    items = request.invoices.get_invoice_items(
        'arrival',
        form.cleaned_data['date_from'],
        form.cleaned_data['date_to'],
        exclude_categories=[Arrival.TYPE_CUSTOM])

    return {
        'form': form,
        'items': items,
        'totals': request.invoices.get_invoice_totals(items),
        **form.cleaned_data
    }

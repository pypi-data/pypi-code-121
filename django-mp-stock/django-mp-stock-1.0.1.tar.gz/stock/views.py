
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from cap.decorators import admin_render_view
from stock.forms import StockReportForm
from products.models import Product


def get_stock_report(request):
    return _get_report(
        request,
        Product.objects.active(),
        _('Products in stock')
    )


def get_min_stock_report(request):
    return _get_report(
        request,
        Product.objects.active().filter(stock__lte=F('min_stock')),
        _('Min stock report')
    )


@admin_render_view('stock/report.html')
def _get_report(request, queryset, report_name):

    form = StockReportForm(request.GET or None)

    ids = None
    categories = None

    if form.is_valid():
        ids = form.cleaned_data['ids']
        categories = form.cleaned_data['categories']

    if categories:
        queryset = queryset.filter(category__in=categories)

    if ids:
        queryset = queryset.filter(id__in=ids.split(','))

    return {
        'report_name': report_name,
        'products': queryset,
        'form': form,
        'totals': {
            'qty': sum([p.stock for p in queryset]),
            'grand_total': sum([p.subtotal for p in queryset])
        }
    }

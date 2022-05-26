
from django.contrib import admin
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from history.admin import LogHistoryAdmin
from product_barcode.filters import BarCodeFilter
from cap.actions import related_field_change_action
from cap.decorators import short_description, template_list_item
from tecdoc.filters import ProductCodeFilter
from exchange.actions import update_prices
from categories.models import Category

from products.forms import ProductForm
from products.models import Product


@short_description(_('Stock report'))
def get_stock_report_action(modeladmin, request, queryset):
    url = reverse('stock:stock-report') + '?ids=' + ','.join(
        map(str, queryset.values_list('id', flat=True)))
    return redirect(url)


@admin.register(Product)
class ProductAdmin(LogHistoryAdmin):

    change_form_template = 'invoice_products/admin/changeform.html'

    history_group = 'products'

    form = ProductForm

    list_per_page = 250

    list_display = [
        'id', 'get_name_tag', 'warehouse', 'manufacturer', 'category',
        'printable_price', 'code', 'stock', 'is_active', 'get_item_actions'
    ]

    actions = [
        get_stock_report_action,
        update_prices,
        related_field_change_action(
            Category,
            'category',
            _('Change category')
        )
    ]

    list_display_links = ['get_name_tag']

    list_filter = [BarCodeFilter, ProductCodeFilter, 'category']

    ordering = ['-id']

    search_fields = Product.search_fields

    fields = (
        ('category', 'manufacturer', ),
        ('is_active', 'name', ),
        ('code', 'bar_code', ),
        ('warehouse', 'unit_type', ),
        ('stock', 'min_stock', ),
        ('price_wholesale', 'price_retail', 'initial_currency', ),
        'additional_codes',
    )

    @short_description(_('Price, UAH'))
    def printable_price(self, item):
        return item.price

    @template_list_item(
        'invoice_products/admin/list_item_actions.html', _('Actions'))
    def get_item_actions(self, item):
        return {'object': item}

    @template_list_item('invoice_products/admin/product_name.html', _('Name'))
    def get_name_tag(self, obj):
        return {'object': obj}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        request.invoices.handle_product_change(obj)

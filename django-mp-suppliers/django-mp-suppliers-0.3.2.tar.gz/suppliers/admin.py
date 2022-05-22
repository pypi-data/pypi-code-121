
from django.contrib import admin

from suppliers.models import Supplier
from suppliers.actions import clean_products
from suppliers.forms import SupplierWarehouseInline


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = [
        'id', 'name', 'short_name', 'code', 'currency', 'discount',
        'markup', 'is_visible_for_unregistered_users', 'country',
        'warehouse_count', 'price_updated'
    ]

    list_display_links = ['id', 'name']

    list_editable = ['is_visible_for_unregistered_users']

    actions = [clean_products]

    inlines = [SupplierWarehouseInline]

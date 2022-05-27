
from cap.decorators import template_list_item
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from customers.models import Customer
from invoices.models import Arrival


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    search_fields = ['name', 'phone', 'vin']
    list_display = [
        'id', 'name', 'phone', 'vin', 'get_sale_count', 'get_actions_tag']
    list_display_links = ['id', 'name']

    @template_list_item('customers/sale_count_cell.html', _('Summary'))
    def get_sale_count(self, obj):
        return {
            'object': obj,
            'sale_count': obj.sales.count(),
            'service_count': obj.services.count(),
            'return_count': (
                obj.arrivals.filter(type=Arrival.TYPE_RETURN).count())
        }

    @template_list_item('customers/actions_cell.html', _('Actions'))
    def get_actions_tag(self, obj):
        return {
            'object': obj,
        }

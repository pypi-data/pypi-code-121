
from django.apps import apps
from django.contrib import admin
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from cap.decorators import template_list_item

from orders.constants import DAYS_OF_WEEK
from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ['order_tag', 'details_tag', 'products_tag']

    list_filter = ['status']

    search_fields = [
        'first_name', 'last_name', 'middle_name', 'address', 'mobile',
        'comment'
    ]

    def has_add_permission(self, request):
        return False

    @template_list_item('orders/admin/details.html', _('Details'))
    def details_tag(self, obj):
        return {
            'object': obj
        }

    @template_list_item('orders/admin/products.html', _('Products'))
    def products_tag(self, obj):
        return {
            'object': obj,
            'is_clothes_app_enabled': apps.is_installed('clothes')
        }

    @template_list_item('orders/admin/order.html', _('Order'))
    def order_tag(self, obj):

        created = localtime(obj.created)

        return {
            'object': obj,
            'day': DAYS_OF_WEEK[created.weekday()],
            'created': created.strftime('%d.%m.%Y %H:%M')
        }

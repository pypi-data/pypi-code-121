
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


def clean_products(modeladmin, request, queryset):

    for supplier in queryset:
        supplier.clean_products()

    messages.success(request, _('Prices cleaned'))


clean_products.short_description = _('Clean prices')

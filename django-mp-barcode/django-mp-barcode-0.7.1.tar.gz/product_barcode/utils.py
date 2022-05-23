
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.products.models import Product


def validate_barcode(bar_code, exclude_id=None):

    queryset = Product.objects.active().filter(bar_code=bar_code)

    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)

    if queryset.exists():
        raise forms.ValidationError(
            _('Product with this bar code already exists'))

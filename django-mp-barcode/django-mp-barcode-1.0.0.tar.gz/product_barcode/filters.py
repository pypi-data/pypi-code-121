
from django.utils.translation import ugettext_lazy as _

from cap.filters import InputFilter


class BarCodeFilter(InputFilter):

    parameter_name = 'bar_code'
    title = _('Bar code')

    def queryset(self, request, queryset):

        value = self.value()

        if not value:
            return

        # Fix for old barcodes
        if value.startswith('000') and len(value) == 12:
            value = value[:-1]

        return queryset.filter(bar_code__icontains=value)

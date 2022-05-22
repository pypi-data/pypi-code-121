
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _

from cap.filters import InputFilter

from tecdoc.utils import clean_code


class ProductCodeFilter(InputFilter):

    parameter_name = 'product_code'
    title = _('Product code')

    def queryset(self, request, queryset):

        code = self.value()

        if not code:
            return

        cleaned_code = clean_code(code)

        return queryset.filter(
            Q(clean_code=cleaned_code) |
            Q(additional_codes__icontains=cleaned_code)
        )

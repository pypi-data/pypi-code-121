
from django.conf import settings


invoice_settings = getattr(settings, 'INVOICES', {})

IS_ROUNDING_ENABLED = invoice_settings.get('IS_ROUNDING_ENABLED', True)

IS_PRODUCT_SELECT_COLLAPSED = invoice_settings.get('IS_PRODUCT_SELECT_COLLAPSED', True)

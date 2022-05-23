import logging

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


class PFXJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ValidationError):
            if hasattr(obj, 'error_dict'):
                return dict(obj)
            return {NON_FIELD_ERRORS: list(obj)}
        return super().default(obj)

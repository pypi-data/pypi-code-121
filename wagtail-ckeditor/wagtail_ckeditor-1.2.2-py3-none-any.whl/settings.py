import json

from django.conf import settings
from django.utils.safestring import mark_safe

WAGTAIL_CKEDITOR_CONFIG = getattr(
    settings,
    "WAGTAIL_CKEDITOR_CONFIG",
    {
        "language": "ru",
    },
)

config = mark_safe(json.dumps(WAGTAIL_CKEDITOR_CONFIG))

from django.template import Library
from django.utils import timezone
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def current_timestamp():
    now = timezone.now()
    return int(datetime.timestamp(now))

from django.template import Library, Node
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def add_time(date, **kwargs):
    return date + timedelta(**kwargs)

@register.simple_tag
def subtract_time(date, **kwargs):
    return date - timedelta(**kwargs)

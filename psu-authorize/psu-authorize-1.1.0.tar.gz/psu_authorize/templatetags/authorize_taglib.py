from django import template
from ast import literal_eval
from psu_base.classes.Log import Log
from psu_base.templatetags.tag_processing import supporting_functions as support
from psu_base.services import utility_service
from django.utils.html import format_html
from django.template import TemplateSyntaxError

register = template.Library()
log = Log()


@register.simple_tag(takes_context=True)
def authorize(context, code, alt):
    """
    Do something...
    """
    log.trace()
    pass

from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag
def under_score_tag(obj, attribute):
    obj = dict(obj)
    return obj.get(attribute)


@register.simple_tag
def clean_url_encode(data, remove):
    attrs = data.copy()
    if remove in data:
        attrs.pop(remove)
    return urlencode(attrs)

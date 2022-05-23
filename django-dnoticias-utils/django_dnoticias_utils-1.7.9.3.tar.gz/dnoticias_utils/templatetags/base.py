from django.template import Library, Node
from django.urls import resolve
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from django.core import serializers
from django.urls.exceptions import Resolver404
from urllib.parse import urlencode, urlparse
from ..utilities import render_to_string_or_empty
from datetime import datetime, date
import json
import logging
import requests

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def get_content_type(instance):
    return ContentType.objects.get_for_model(instance)

@register.simple_tag
def get_attr(instance, attr):
    return getattr(instance, attr, "")

@register.simple_tag
def set_attr(instance, attr, value):
    return getattr(instance, attr, value)


@register.simple_tag
def update_dict(context={}, **kwargs):
    context.update(kwargs)
    return context


@register.simple_tag
def parse_into_urlencode(**kwargs):
    return urlencode(kwargs, True)


@register.simple_tag
def add_string(prefix, *args):
    total = prefix
    for element in args:
        total += str(element)
    return total


@register.simple_tag
def is_string(val):
    return isinstance(val, str)

@register.simple_tag
def json_loads(val):
    try:
        return json.loads(val)
    except:
        return {}

@register.simple_tag
def json_dumps(val):
    try:
        return json.dumps(val)
    except:
        return '\{\}'


@register.simple_tag
def apply_func(instance, func_name, *args, **kwargs):
    func = getattr(instance, func_name, None)
    if func is None:
        return ""
    return func(*args, **kwargs)

@register.simple_tag
def get_index(array, index):
    if isinstance(array, dict):
        return array.get(index, None)
    else:
        try:
            return array[index]
        except:
            return None

@register.simple_tag
def get_last_index(array, value):
    pass

@register.simple_tag
def to_camel_case(value):
    return ''.join(x for x in value.title().replace("_", "") if not x.isspace())


@register.simple_tag
def is_on(request, url_name):
    try:
        current_url_name = resolve(request.path_info).url_name
        return current_url_name == url_name
    except Resolver404 as e:
        return False


@register.simple_tag
def get_settings_value(name):
    logger.debug("get_settings_value -> variable -> {} -> {}".format(name, getattr(settings, name, None)))
    return getattr(settings, name, None)


@register.simple_tag
def get_selected_option_value(optgroups):
    for group_name, group_choices, group_index in optgroups:
        if group_choices[0]["selected"]:
            return group_choices[0]["value"]
    return ""


@register.simple_tag
def get_bound_field_context(bound_field):
    widget = bound_field.field.widget

    if bound_field.field.localize:
        widget.is_localized = True

    attrs = {}
    attrs = bound_field.build_widget_attrs(attrs, widget)

    if bound_field.auto_id and 'id' not in widget.attrs:
        attrs.setdefault('id', bound_field.auto_id)

    return widget.get_context(bound_field.html_name, bound_field.value(), attrs)


@register.simple_tag
def get_dict(**kwargs):
    return kwargs


@register.simple_tag
def get_fragments(array, length, fragment_size):
    fragments = []
    actual_length = 0
    while actual_length < length:
        fragments.append(array[actual_length:actual_length+fragment_size])
        actual_length += fragment_size
    return fragments


@register.simple_tag
def assign_variable(variable):
    return variable


@register.simple_tag
def render_to_string(template, **kwargs):
    return render_to_string_or_empty(template, kwargs)


@register.simple_tag
def to_int(val):
    return int(val)


@register.simple_tag
def to_float(val):
    return float(val)

@register.simple_tag
def to_bool(val):
    return bool(val)


@register.simple_tag
def to_list(val):
    return list(val)


@register.simple_tag
def has_key(dict, key):
    return key in dict


@register.simple_tag
def today():
    return timezone.now()


@register.simple_tag
def is_same_date(a, b):
    if (isinstance(a, datetime) or isinstance(a, date)) and (isinstance(b, datetime) or isinstance(b, date)):
        return a.date() == b.date()
    else:
        return False

@register.simple_tag
def get_timedelta(datetime_reference):
    if isinstance(datetime_reference, datetime) or isinstance(datetime_reference, date):
        timedelta = (timezone.now() - datetime_reference)
        timedelta_context = dict()

        days = timedelta.days
        if timedelta.days:
            timedelta_context["days"] = timedelta.days

        minutes = (timedelta.seconds//60)%60
        if minutes:
            timedelta_context["minutes"] = minutes

        hours = timedelta.seconds//3600
        if hours:
            timedelta_context["hours"] = hours

        if timedelta_context.keys() == 0:
            timedelta_context["seconds"] = timedelta.seconds

        return timedelta_context
    else:
        return None

@register.simple_tag
def is_same_year(a, b):
    if isinstance(a, datetime) and isinstance(b, datetime):
        return a.year == b.year
    else:
        return False

@register.simple_tag
def get_class_name(instance):
    return instance.__class__.__name__

@register.simple_tag
def get_domain(url : str):
    return urlparse(url).netloc

@register.simple_tag
def request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
    except:
        logger.exception("Error in the response")
        return {
            "status" : 500,
            "json" : {},
            "content" : ""
        }

    response_content_json = {}
    try:
        response_content_json = response.json()
    except:
        logger.exception("The response isn't a json")

    return {
        "status" : response.status_code,
        "json" : response_content_json,
        "content" : response.content
    }

@register.simple_tag
def build_list(*args):
    return args

@register.simple_tag
def extend_list(elements, *args):
    elements = list(elements) + list(args)
    return elements

@register.simple_tag
def get_index_of_value(array, value, start=0):
    try:
        return array[start:].index(value) + start
    except:
        return None

@register.simple_tag
def get_last_index_of_value(array, value, start=0):
    try:
        return len(array) - 1 - array[start:][::-1].index(value)
    except:
        return None

@register.simple_tag
def subset(array, end, start=0):
    return array[start:end]

@register.simple_tag
def serialize(format, queryset, multi=True, **kwargs):
    try:
        json_list_string = serializers.serialize(format, queryset, **kwargs)
        if multi:
            return json.loads(json_list_string)
        else:
            context = json.loads(json_list_string)
            return context[0]
    except Exception as e:
        if multi:
            return []
        else:
            return {}

@register.simple_tag
def range_diff(index, limit):
    return range(index, limit)
import importlib
import re
import logging
import traceback
from itertools import chain
from urllib.parse import urlparse, parse_qs, urlencode, urlsplit, urlunsplit

from django import forms
from django.contrib import messages
from django.shortcuts import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager, ManyToManyField
from django.template.loader import get_template, TemplateDoesNotExist, render_to_string

logger = logging.getLogger(__name__)


def normalize_domain(domain):
    return re.sub('[^\w\-_ ]', '', domain)


def get_model_attr(instance, field, default=[]):
    try:
        value = getattr(instance, field, None)
    except Exception as e:
        logger.exception(e)
        value = None
    is_manager = isinstance(value, Manager)
    if is_manager:
        value = value.all()
    return value


def get_attr_by_string(class_path):
    path_fragments = class_path.split(".")
    module_path = ".".join(path_fragments[:-1])
    class_name = path_fragments[-1]
    module = importlib.import_module(module_path)
    _class = getattr(module, class_name, None)
    if _class:
        return _class
    else:
        raise Exception(
            "Couldn't find the class with the path {}".format(class_path))


def exists_template(template_name):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist as e:
        return False


def render_to_string_or_empty(template_name, context, request=None, using=None):
    logger.debug("TEMPLATE NAME -> {}".format(template_name))
    try:
        content = render_to_string(
            template_name, context=context, request=request, using=using
        )
    except Exception as e:
        logger.exception("Error in rendering the template -> {}".format(template_name))
        is_preview = context.get("is_preview")
        if is_preview:
            content = traceback.format_exc()
        else:
            content = ""
    return content


def instance_to_dot_path(instance):
    if isinstance(instance, type):
        return ".".join([instance.__module__, instance.__name__])
    else:
        return ".".join([instance.__class__.__module__, instance.__class__.__name__])


def errors_serialize(form):
    errors_context = dict()
    for key in form.errors:
        if key in form:
            errors_context[key] = {
                "id": form[key].auto_id,
                "name": form[key].html_name,
                "errors": form.errors[key]
            }
    return errors_context


def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_facebook_graph_url():
    facebook_graph_base_url = settings.FACEBOOK_GRAPH_URL
    if facebook_graph_base_url.endswith('/'):
        facebook_graph_base_url += "/"
    return facebook_graph_base_url


def is_absolute(url):
    return bool(urlparse(url).netloc)


def get_field_form_from_model(instance, field_name):
    instance_class = instance.__class__

    class CustomModelForm(forms.ModelForm):
        class Meta:
            model = instance_class
            fields = (field_name,)
    form = CustomModelForm(instance=instance)
    return form.fields[field_name]


def to_valid_variable_name(value):
    # Remove invalid characters
    value = re.sub('[^0-9a-zA-Z_]', '_', value)

    # Remove leading characters until we find a letter or underscore
    value = re.sub('^[^a-zA-Z_]+', '', value)

    return value


def replace_keys_with_valid_variable_name(context):
    new_context = dict()
    keys = context.keys()
    for key in keys:
        new_context[to_valid_variable_name(key)] = context.get(key)
    return new_context


def get_content_type_preview_url(printable_object):
    if printable_object:
        return reverse("preview-content-type", kwargs={
            "content_type_pk" : ContentType.objects.get_for_model(printable_object).pk,
            "pk" : printable_object.pk
        })
    else:
        return None


def send_message(request, msg_level, msg, **kwargs):
    fail_silently = kwargs.pop("fail_silently", False)

    if fail_silently:
        try:
            messages.add_message(request, msg_level, msg, **kwargs)
        except Exception as e:
            logger.exception("Failed to add message to the request -> {}, probably request is None".format(request))
    else:
        messages.add_message(request, msg_level, msg, **kwargs)


def set_query_parameters(url, **extra_query_params):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    for param in extra_query_params:
        query_params[param] = extra_query_params[param]

    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def has_cached_prefetch_field(model_instance, attr_name):
    attr_value = getattr(model_instance, attr_name, None)
    if attr_value and isinstance(attr_value, list):
        return True

    return bool(
        getattr(model_instance, "_prefetched_objects_cache", {}).get(attr_name)
    )


def has_cached_related_field(model_instance, model_field=None, attr_name=None):
    if model_field is None and attr_name is None:
        return False

    field_name = model_field.field.name if model_field else attr_name

    return bool(
        getattr(model_instance._state, "fields_cache", {}).get(field_name)
    )


def get_select_related_choices_by_model(model_class):
    opts = model_class._meta

    direct_choices = (f.name for f in opts.fields if f.is_relation)

    reverse_choices = (
        f.field.related_query_name()
        for f in opts.related_objects if f.field.unique
    )

    return list(
        chain(direct_choices, reverse_choices)
    )


def get_prefetch_related_choices_by_model(model_class):
    opts = model_class._meta

    reverse_choices = (
        f.field.related_query_name()
        for f in opts.related_objects if not f.field.unique
    )

    direct_choices = (f.name for f in opts.get_fields() if isinstance(f, ManyToManyField))

    return list(
        chain(
            reverse_choices,
            direct_choices
        )
    )

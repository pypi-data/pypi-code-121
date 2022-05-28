from django.forms import BaseForm
from django.utils.translation import get_language
from rest_framework.serializers import Serializer

try:
    from urlparse import parse_qs, urlparse
except ImportError:  # For Python 3
    from urllib.parse import parse_qs, urlparse


def django_files_to_requests_files(files):
    return {k: (f.name, f.read(), f.content_type) for k, f in files.items()} if files is not None else None


def to_error_list(serializer_or_form):
    """
    Converts from django error format to a list of error strings. The fields must have `label` attribute.

    :param serializer_or_form: django serializer or form with failed validation,
     i.e. serializer_or_form.is_valid() is False.
    :return: A list of error strings
    """
    assert isinstance(serializer_or_form, Serializer) or isinstance(serializer_or_form, BaseForm), (
        'Input parameter must be a rest_framework serializer or a django form.'
    )

    return [
        '{field_name}: {error_message}'.format(
            field_name=serializer_or_form.fields[field_key].label,
            error_message=field_errors[0],
        )
        for field_key, field_errors in serializer_or_form.errors.items()
    ]


def append_lang_param(url, param_name):
    query = urlparse(url).query
    if param_name not in parse_qs(query):
        if url[-1] not in ['?', '&']:
            url += '&' if query else '?'
        url += '{}={}'.format(param_name, get_language())
    return url

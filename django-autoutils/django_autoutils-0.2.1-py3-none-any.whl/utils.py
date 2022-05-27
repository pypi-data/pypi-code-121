"""
    Some utils for working with django
"""
import inspect

from django.contrib.messages.storage.base import BaseStorage
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from rest_framework import exceptions, serializers


def get_client_ip(request):
    """
        Get Client IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_request_obj():
    """
        Find request obj
    """
    for frame_record in inspect.stack():
        if frame_record[3] == "get_response":
            return frame_record[0].f_locals["request"]
    return None


def get_empty_request(server_name: str = "localhost", server_port: int = 80):
    """
        Get Empty request
    """
    request = HttpRequest()
    request._messages = BaseStorage(request=request)
    request.META["SERVER_NAME"] = server_name
    request.META["SERVER_PORT"] = server_port
    request.user = None
    return request


def handle_validation_error(e: "ValidationError", none_field=None):
    """
        Handle validation error
    """
    if hasattr(e, 'error_dict'):
        raise exceptions.ValidationError(e.message_dict)
    if none_field is not None:
        raise exceptions.ValidationError({none_field: e.messages})


def get_model_serializer(model, fields, read_only_fields=None, base_serializer=serializers.ModelSerializer,
                         extra_fields: dict = None, meta_extra_fields: dict = None):
    """
        Get Model serializer
    """
    if extra_fields is None:
        extra_fields = {}
    if meta_extra_fields is None:
        meta_extra_fields = {}
    if not read_only_fields:
        read_only_fields = []
    meta_class = type('Meta', (), {
        "model": model,
        "fields": fields,
        "read_only_fields": read_only_fields,
        **meta_extra_fields
    })
    return type('Serializer', (base_serializer,), {
        "Meta": meta_class,
        **extra_fields
    })

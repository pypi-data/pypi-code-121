# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
try:
    from django.http.response import HttpResponseBase

    django_response_types = (HttpResponseBase,)
except ImportError:  # pragma: no cover
    django_response_types = ()

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

string_types = (str, bytes, bytearray)

list_iterator = type(iter(list()))
dict_iterator = type(iter(dict()))


def is_iterable(value):
    """
    :param value: any type
    :return: True if iterable type like list, dict but NOT string
             False if string or any other type like database collection types
                   (pymongo Collection implements iter but is not an iterable
    """

    try:
        it = iter(value)
        if not hasattr(it, "__next__"):
            return False
    except TypeError:
        return False

    return not isinstance(value, string_types)


def len_or_zero(value):
    try:
        return len(value)
    except Exception:
        return 0


def safe_iterator(it):
    if isinstance(it, (list_iterator, dict_iterator)):
        logger.debug(
            "WARNING: skipping iteration of non-seekable iterator: %s", type(it)
        )
        return

    if isinstance(it, (str, list, dict, tuple)) or (
        isinstance(it, django_response_types)
        and not safe_getattr(it, "streaming", True)
    ):
        for x in it:
            yield x
        return

    if not (hasattr(it, "tell") and hasattr(it, "seek")):
        logger.debug("WARNING: skipping iteration of non-seekable object: %s", type(it))
        return

    try:
        orig_pos = it.tell()
    except Exception:
        logger.debug(
            "WARNING: skipping iteration of non-tell()-able object: %s", type(it)
        )
        return

    try:
        for x in it:
            yield x
    except Exception:
        logger.debug("safe_iterator failed to iterate over %s", type(it))
    finally:
        it.seek(orig_pos)


def safe_getattr(obj, attr, default=None):
    """
    A getattr implementation that returns a default even if an exception is raised

    Some classes may override __getattribute__ to raise exceptions when certain
    attributes are accessed. When we are dealing with objects from the outside world,
    we want to be careful in our attribute access to avoid such exceptions and provide
    a safe default.
    """
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default

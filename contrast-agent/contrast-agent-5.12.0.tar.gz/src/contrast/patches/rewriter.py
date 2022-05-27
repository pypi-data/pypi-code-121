# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent import scope
from contrast.agent.assess.utils import is_tracked
from contrast.agent.assess.policy import string_propagation
from contrast.utils.decorators import fail_loudly


def contrast__add(left, right):
    """
    This function replaces addition in the AST. We use double underscore to lower the
    probability of a name conflict.

    It is basically a pure-python translation of <type>_concat_new from str_concat.c.
    In the future, we should consider implementing as much of this in C as possible.
    """
    with scope.propagation_scope():
        result = left + right

    _propagate_add(left, right, result)

    return result


def contrast__append(target, value):
    orig_target = target
    with scope.propagation_scope():
        target += value

    _propagate_add(orig_target, value, target)

    return target


@fail_loudly("failed to propagate through addition in contrast__add")
def _propagate_add(left, right, result):
    propagation_func = None
    if isinstance(result, str):
        propagation_func = string_propagation.propagate_unicode_concat
    elif isinstance(result, bytes):
        propagation_func = string_propagation.propagate_bytes_concat
    elif isinstance(result, bytearray):
        propagation_func = string_propagation.propagate_bytearray_concat
    if propagation_func is None:
        return

    if len(result) < 2:
        return

    if scope.in_scope() or scope.in_trigger_scope():
        return

    if not (is_tracked(left) or is_tracked(right)):
        return

    with scope.contrast_scope(), scope.propagation_scope():
        propagation_func(result, left, result, (right,), {})

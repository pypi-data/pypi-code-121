# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
This module contains workarounds for the fact that some builtin methods appear
to be unpatchable using funchook for one reason or another.
"""
import contrast
from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy.propagation_policy import (
    PROPAGATOR_ACTIONS,
    track_copy_without_new_event,
)
from contrast.agent.assess.policy.propagators import FormatPropagator, JoinPropagator
from contrast.agent.assess.policy.preshift import Preshift
from contrast.assess_extensions import cs_str, smart_setattr


from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def build_bytearray_join_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]

    def bytearray_join_patch(__cs_self, *args, **kwargs):
        # Since we need to make reference to the input multiple times, convert the
        # first argument to a list and use that instead. This prevents any iterators
        # from being exhausted before we can make use of them in propagation.
        # For bytearray.join, args == (list_or_iterator_of_things_to_join,...)
        # Note that this is different from the C hooks for other join methods. In
        # those cases, the PyObject *args argument corresponds to just the list or
        # iterator itself, in contrast to a tuple that contains that list or
        # iterator. (Got that straight?)
        if cs_str.in_contrast_or_propagation_scope():
            return orig_method(__cs_self, *args, **kwargs)

        args_list = [list(args[0])] + list(args[1:])
        result = orig_method(__cs_self, *args_list, **kwargs)

        scope.enter_contrast_scope()

        try:
            preshift = Preshift(__cs_self, args_list, kwargs)
            propagator = JoinPropagator(node, preshift, result)
            if propagator.needs_propagation:
                propagator.track_and_propagate(result)
        except Exception as ex:
            logger.debug("failed to propagate bytearray.join", exc_info=ex)

        scope.exit_contrast_scope()

        return result

    bytearray_join_patch.__name__ = orig_method.__name__
    return bytearray_join_patch


def build_strtype_join_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]

    def strtype_join_patch(__cs_self, *args, **kwargs):
        if cs_str.in_contrast_or_propagation_scope():
            return orig_method(__cs_self, *args, **kwargs)

        args_list = list(args[0])

        with scope.propagation_scope():
            result = orig_method(__cs_self, args_list, **kwargs)

        scope.enter_contrast_scope()

        try:
            preshift = Preshift(__cs_self, (args_list,), kwargs)
            propagator = JoinPropagator(node, preshift, result)
            if propagator.needs_propagation:
                propagator.track_and_propagate(result)
        except Exception as ex:
            logger.debug("failed to propagate join", exc_info=ex)

        scope.exit_contrast_scope()

        return result

    strtype_join_patch.__name__ = orig_method.__name__
    return strtype_join_patch


def build_str_format_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]

    def str_format_patch(__cs_self, *args, **kwargs):
        """
        Propagation hook for str.format

        This hook is a special case because we need to enable some propagation to occur
        while we evaluate whether to propagate this particular event. With the current
        general hook infrastructure, this is not possible, so we need to account for it
        here. Eventually it may be possible to fit this back into the more general
        infrastructure if we overhaul the way that scope works.
        """
        result = orig_method(__cs_self, *args, **kwargs)

        if cs_str.in_contrast_or_propagation_scope():
            return result

        try:
            with scope.contrast_scope():
                preshift = Preshift(__cs_self, args, kwargs)
                propagator = FormatPropagator(node, preshift, result)

            # This evaluation must not occur in scope. This is what enables us
            # to perform any conversions from object to __str__ or __repr__,
            # while allowing propagation to occur through those methods if
            # necessary.
            if propagator.needs_propagation:
                with scope.contrast_scope():
                    propagator.track_and_propagate(result)
        except Exception as ex:
            with scope.propagation_scope():
                logger.debug("failed to propagate str.format", exc_info=ex)

        return result

    str_format_patch.__name__ = orig_method.__name__
    return str_format_patch


def build_str_formatmap_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]

    def str_formatmap_patch(__cs_self, *args, **kwargs):
        """
        Propagation hook for str.format_map

        This hook is a special case because we need to enable some propagation to occur
        while we evaluate whether to propagate this particular event. With the current
        general hook infrastructure, this is not possible, so we need to account for it
        here. Eventually it may be possible to fit this back into the more general
        infrastructure if we overhaul the way that scope works.
        """
        result = orig_method(__cs_self, *args, **kwargs)

        if cs_str.in_contrast_or_propagation_scope() or not args:
            return result

        try:
            with scope.contrast_scope():
                preshift = Preshift(__cs_self, (), args[0])
                propagator = FormatPropagator(node, preshift, result)

            # This evaluation must not occur in scope. This is what enables us
            # to perform any conversions from object to __str__ or __repr__,
            # while allowing propagation to occur through those methods if
            # necessary.
            if propagator.needs_propagation:
                with scope.contrast_scope():
                    propagator.track_and_propagate(result)
        except Exception as ex:
            with scope.propagation_scope():
                logger.debug("failed to propagate str.format", exc_info=ex)

        return result

    str_formatmap_patch.__name__ = orig_method.__name__
    return str_formatmap_patch


def build_generic_strtype_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]
    propagator_class = PROPAGATOR_ACTIONS.get(node.action)

    def str_patch(__cs_self, *args, **kwargs):
        result = orig_method(__cs_self, *args, **kwargs)

        # This special case does not apply to bytearrays
        if result is __cs_self:
            return result

        if cs_str.in_contrast_or_propagation_scope():
            return result

        scope.enter_contrast_scope()

        try:
            preshift = Preshift(__cs_self, args, kwargs)
            propagator = propagator_class(node, preshift, result)

            if propagator.needs_propagation:
                propagator.track_and_propagate(result)
        except Exception as ex:
            name = orig_method.__class__.__name__
            logger.debug(
                "failed to propagate %s.%s", name, orig_method.__name__, exc_info=ex
            )

        scope.exit_contrast_scope()

        return result

    str_patch.__name__ = orig_method.__name__
    return str_patch


def build_track_without_new_event_patch(orig_method, patch_policy):
    node = patch_policy.propagator_nodes[0]
    propagator_class = PROPAGATOR_ACTIONS.get(node.action)

    def str_patch(__cs_self, *args, **kwargs):
        result = orig_method(__cs_self, *args, **kwargs)

        if cs_str.in_contrast_or_propagation_scope():
            return result

        # This special case applies to all bytearray methods and all .translate methods
        if result == __cs_self:
            track_copy_without_new_event(result, __cs_self)
            return result

        scope.enter_contrast_scope()

        try:
            preshift = Preshift(__cs_self, args, kwargs)
            propagator = propagator_class(node, preshift, result)

            if propagator.needs_propagation:
                propagator.track_and_propagate(result)
        except Exception as ex:
            name = orig_method.__class__.__name__
            logger.debug(
                "failed to propagate %s.%s", name, orig_method.__name__, exc_info=ex
            )

        scope.exit_contrast_scope()

        return result

    str_patch.__name__ = orig_method.__name__
    return str_patch


def build_and_apply_patch(owner, method_name, patch_builder):
    orig_method = getattr(owner, method_name)

    policy_method_name = (
        "formatmap" if orig_method.__name__ == "format_map" else orig_method.__name__
    )

    patch_policy = Policy().policy_by_name.get("BUILTIN.str." + policy_method_name)
    patch = patch_builder(orig_method, patch_policy)

    patch_manager.patch(owner, method_name, patch)


def property_getter(self):
    return contrast.STRING_TRACKER.get(self, None)


def property_setter(self, value):
    contrast.STRING_TRACKER.update_properties(self, value)


def enable_str_properties():
    strprop = property(fget=property_getter, fset=property_setter)

    smart_setattr(str, "cs__properties", strprop)
    smart_setattr(bytes, "cs__properties", strprop)
    smart_setattr(bytearray, "cs__properties", strprop)


def patch_strtype_method(strtype, method_name):
    if method_name == "join":
        builder = (
            build_bytearray_join_patch
            if strtype is bytearray
            else build_strtype_join_patch
        )
    elif method_name == "format":
        builder = build_str_format_patch
    elif method_name == "format_map":
        builder = build_str_formatmap_patch
    elif method_name == "translate" and strtype is str:
        builder = build_track_without_new_event_patch
    else:
        builder = (
            build_track_without_new_event_patch
            if strtype is bytearray
            else build_generic_strtype_patch
        )

    build_and_apply_patch(strtype, method_name, patch_builder=builder)


def unpatch_strtype_methods():
    """
    Replace all patched strtype methods with the original implementation
    """
    patch_manager.reverse_patches_by_owner(str)
    patch_manager.reverse_patches_by_owner(bytes)
    patch_manager.reverse_patches_by_owner(bytearray)

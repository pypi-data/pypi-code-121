# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent import scope
from contrast.agent.assess.policy.preshift import Preshift
from contrast.agent.assess.policy import propagation_policy
from contrast.agent.assess.policy import source_policy
from contrast.agent.assess.policy import trigger_policy
from contrast.agent.assess.utils import get_self_for_method
from contrast.agent.settings import Settings
from contrast.utils.decorators import fail_loudly, log_time


def check_or_enter_scope(orig_func):
    """
    Decorator that checks if we're in contrast scope. If so, return immediately, else
    call the original function in contrast scope.

    Sometimes it is essential that the very first action we take when a method is called
    is a scope check. If we hit any instrumented method before this check, we'll be in
    an infinite recursion. This decorator must be the topmost (first) if it's used.
    """

    def wrapper(*args, **kwargs):
        if scope.in_contrast_scope():
            return
        with scope.contrast_scope():
            orig_func(*args, **kwargs)

    return wrapper


@check_or_enter_scope  # NOTE: this decorator must come first!
@log_time("Entering analyze")
@fail_loudly("Failed to perform assess analysis.")
def analyze(context, patch_policy, result, args, kwargs):
    if not context or not Settings().is_assess_enabled():
        return

    self_obj = get_self_for_method(patch_policy, args)
    preshift = Preshift(self_obj, args, kwargs)

    _analyze(patch_policy, preshift, self_obj, result, args, kwargs)


def skip_analysis(context):
    """
    Skip analysis if there is no context, scope, or configuration is False
    :param context: RequestContext
    :return:
    """
    if not context:
        return True
    if scope.in_contrast_scope():
        return True
    return not Settings().is_assess_enabled()


def _analyze(patch_policy, preshift, self_obj, ret, orig_args, orig_kwargs=None):
    if not patch_policy:
        return

    context = contrast.CS__CONTEXT_TRACKER.current()
    if context is None:
        return

    if patch_policy.analysis_func is not None:

        rule = (
            patch_policy.trigger_nodes[0].rule if patch_policy.trigger_nodes else None
        )

        patch_policy.analysis_func(
            rule=rule,
            nodes=patch_policy.all_nodes,
            self_obj=self_obj,
            ret=ret,
            orig_args=orig_args,
            orig_kwargs=orig_kwargs,
            preshift=preshift,
        )
    else:
        _run_unoptimized_analysis(
            patch_policy, preshift, self_obj, ret, orig_args, orig_kwargs
        )


def _run_unoptimized_analysis(patch_policy, preshift, self_obj, ret, args, kwargs):
    if patch_policy.trigger_nodes:
        # Each node may potentially correspond to a different rule
        for node in patch_policy.trigger_nodes:
            trigger_policy.apply(
                rule=node.rule,
                nodes=[node],
                ret=ret,
                orig_args=args,
                orig_kwargs=kwargs,
            )

    if patch_policy.source_nodes:
        source_policy.apply(
            nodes=patch_policy.source_nodes,
            self_obj=self_obj,
            ret=ret,
            orig_args=args,
            orig_kwargs=kwargs,
        )

    if patch_policy.propagator_nodes:
        propagation_policy.apply(
            nodes=patch_policy.propagator_nodes, preshift=preshift, ret=ret
        )

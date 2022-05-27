# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Implementation of patches for the `re` module.

Other methods of the `re` module such as `split` and `escape` can be patched directly,
so they are implemented in policy.
"""
import functools
from contrast.extern import structlog as logging
import sys

from contrast.extern.wrapt import register_post_import_hook

import contrast
from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.apply_trigger import cs__apply_trigger
from contrast.agent.assess.policy.analysis import analyze
from contrast.agent.assess.policy.propagators import regex_propagator
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch
from contrast.utils.string_utils import ensure_string

logger = logging.getLogger("contrast")

PATTERN_CLASS = "re.Pattern"
MATCH_CLASS = "re.Match"


def build_group_hook(original_func, patch_policy, propagator):
    def group_hook(*args, **kwargs):
        context = contrast.CS__CONTEXT_TRACKER.current()
        result = original_func(*args, **kwargs)
        if context is not None and context.propagate_assess:
            with scope.propagation_scope():
                propagator(args[0], result, *args[1:])
        return result

    group_hook.__name__ = ensure_string(patch_policy.method_name)
    return group_hook


def wrap_repl(repl):
    repl_results = []

    def new_repl(match):
        result = repl(match)
        repl_results.append(result)
        return result

    functools.update_wrapper(new_repl, repl)
    return new_repl, repl_results


def get_propagation_node(node):
    return node.propagator_nodes[0] if node.propagator_nodes else None


@fail_quietly("Failed to propagate sub(n)")
def _analyze_sub(node, retval, repl_results, args, kwargs, new_args):
    if node.method_name == "subn":
        result, count = retval
    else:
        # Account for the fact that count could either be positional or kwarg
        count = args[3] if len(args) == 4 else kwargs.pop("count", 0)
        result = retval

    # Omit count (and flags) if they are part of posargs since they are being passed
    # explicitly to our propagator
    new_args = new_args[:3]
    new_kwargs = dict(count=count)
    if not node.instance_method:
        # Account for the fact that flags could either be positional or kwarg
        new_kwargs["flags"] = args[4] if len(args) > 4 else kwargs.get("flags", 0)

    with scope.propagation_scope():
        regex_propagator.propagate_sub(
            node, result, repl_results, *new_args[:3], **new_kwargs
        )


@fail_quietly("Failed to analyze redos trigger")
def _trigger_redos(name, result, args, kwargs):
    context = contrast.CS__CONTEXT_TRACKER.current()
    if context is None:
        return

    policy = Policy()
    rule = policy.triggers["redos"]

    if not scope.in_trigger_scope() and not scope.in_scope():
        if rule.disabled:
            # Given how often these patches are called within apps, it's well worth
            # returning early here even though this logic exists further down the stack.
            # However, we MUST call this here after the `in_scope` check because
            # `rule.disabled` calls on Settings code that recursively calls on
            # other patches.
            return

        trigger_node = _get_redos_trigger_node(name, rule)

        # Both trigger and contrast scope are needed here.
        with scope.trigger_scope(), scope.contrast_scope():
            # we cannot use trigger_policy.apply here due to the instance_method
            # logic it uses to remove self_obj from args. For the redos action,
            # specifically for re.Pattern.method nodes, we NEED the self_obj
            # to be in the args at this time.
            source = trigger_node.get_matching_sources(None, result, args, kwargs)[0]
            cs__apply_trigger(
                context,
                rule,
                trigger_node,
                source,
                None,
                result,
                None,
                args,
                kwargs,
            )


def _get_redos_trigger_node(trigger_name, rule):
    trigger_loc = "re"
    if "Pattern" in trigger_name:
        trigger_loc = PATTERN_CLASS

    func_name = trigger_name.split(".")[-1]
    trigger_nodes = rule.find_trigger_nodes(trigger_loc, func_name)

    return trigger_nodes[0]


def build_sub_hook(original_func, policy_node):
    policy_node = get_propagation_node(policy_node)

    def sub_hook(*args, **kwargs):
        """
        Hook for re.sub and re.subn used for propagation in assess

        The following explains why we can't simply patch these methods using
        policy.

        It is possible for the repl argument to be a callable. In this case, the
        callable is passed a Match object, and it returns the string to be used for
        the replacement. In order to correctly propagate the substitution
        operation, we need to keep track of the results of calling the replacement
        function.

        It might seem like we should just call the replacement function again
        during our propagation action. But this is not practicable for several
        reasons:

          1. We're in scope at the time, so any propagation that needs to occur
             within the replacement callable itself will be missed.
          2. Related to above, but methods of Match do not return the same object
             even when called multiple times with the same arguments, so we would
             not be tracking the strings that actually get used in the substitution
             result.
          3. There's no guarantee that the replacement function does not cause any
             side effects or rely on any state in application code. We definitely
             don't want to mess around with this.

        The solution is to wrap the replacement callable with our own function that
        records the results of each call. We then pass our wrapped callable to the
        original function, and we pass the accumulated results to the propagator.
        This has the additional benefit of allowing us to wrap the match object
        that is passed to the repl function with our proxied object so that we
        propagate any calls that are made within this function if necessary.
        """
        # Get the non-propagation case out of the way here
        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None or not context.propagate_assess:
            return original_func(*args, **kwargs)

        try:
            repl = args[1]
            new_repl, repl_results = wrap_repl(repl) if callable(repl) else (repl, None)
            new_args = tuple(args[:1]) + (new_repl,) + tuple(args[2:])
        except Exception:
            # This indicates that the original caller passed garbage, so call the original
            # function and let the error propagate back up to where they can clean up their
            # own mess.
            return original_func(*args, **kwargs)

        retval = original_func(*new_args, **kwargs)

        _trigger_redos(policy_node.name, retval, args, kwargs)
        _analyze_sub(policy_node, retval, repl_results, args, kwargs, new_args)

        return retval

    sub_hook.__name__ = ensure_string(policy_node.method_name)
    return sub_hook


@fail_quietly("Failed to analyze")
def _analyze_policy(name, result, args, kwargs):
    context = contrast.CS__CONTEXT_TRACKER.current()
    if context is None or not context.propagate_assess:
        return

    with scope.contrast_scope():
        policy = Policy()
        patch_policy = policy.policy_by_name.get(name)
        if not patch_policy:
            return

    analyze(context, patch_policy, result, args, kwargs)


def build_re_assess_hook(original_func, patch_policy):
    """Builds patch that analyzes for both redos trigger and regex propagation"""

    def assess_hook(*args, **kwargs):
        result = original_func(*args, **kwargs)
        _trigger_redos(patch_policy.name, result, args, kwargs)
        _analyze_policy(patch_policy.name, result, args, kwargs)
        return result

    assess_hook.__name__ = ensure_string(original_func.__name__)
    return assess_hook


def build_re_pattern_redos_hook(original_func, _):
    """
    Builds patch for re.Pattern methods that performs analysis for redos trigger only
    """

    method_name = original_func.__name__
    full_name = "re.Pattern." + method_name

    def redos_hook(*args, **kwargs):
        retval = original_func(*args, **kwargs)
        _trigger_redos(full_name, retval, args, kwargs)
        return retval

    redos_hook.__name__ = ensure_string(method_name)
    return redos_hook


def patch_re(re_module):
    # The re.Pattern and re.Match classes are not directly accessible in all versions
    # of Python, so we do this somewhat hacky workaround to get a reference to them.
    pattern_cls = re_module.compile("").__class__
    match_cls = re_module.match("", "").__class__

    build_and_apply_patch(re_module, "sub", build_sub_hook)
    build_and_apply_patch(re_module, "subn", build_sub_hook)

    build_and_apply_patch(pattern_cls, "sub", build_sub_hook, owner_name=PATTERN_CLASS)
    build_and_apply_patch(pattern_cls, "subn", build_sub_hook, owner_name=PATTERN_CLASS)
    build_and_apply_patch(
        pattern_cls,
        "split",
        build_re_assess_hook,
        owner_name=PATTERN_CLASS,
    )
    build_and_apply_patch(
        pattern_cls,
        "findall",
        build_re_assess_hook,
        owner_name=PATTERN_CLASS,
    )

    build_and_apply_patch(
        pattern_cls,
        "match",
        build_re_pattern_redos_hook,
        owner_name=PATTERN_CLASS,
    )
    build_and_apply_patch(
        pattern_cls,
        "search",
        build_re_pattern_redos_hook,
        owner_name=PATTERN_CLASS,
    )
    build_and_apply_patch(
        pattern_cls, "finditer", build_re_pattern_redos_hook, owner_name=PATTERN_CLASS
    )

    build_and_apply_patch(
        pattern_cls,
        "fullmatch",
        build_re_pattern_redos_hook,
        owner_name=PATTERN_CLASS,
    )

    build_and_apply_patch(
        match_cls,
        "group",
        build_group_hook,
        (regex_propagator.propagate_group,),
        owner_name=MATCH_CLASS,
    )
    build_and_apply_patch(
        match_cls,
        "groups",
        build_group_hook,
        (regex_propagator.propagate_groups,),
        owner_name=MATCH_CLASS,
    )
    build_and_apply_patch(
        match_cls,
        "groupdict",
        build_group_hook,
        (regex_propagator.propagate_groupdict,),
        owner_name=MATCH_CLASS,
    )


def register_patches():
    register_post_import_hook(patch_re, "re")


def reverse_patches():
    re_module = sys.modules.get("re")
    if not re_module:
        return

    pattern_cls = re_module.compile("").__class__
    match_cls = re_module.match("", "").__class__

    patch_manager.reverse_patches_by_owner(re_module)
    patch_manager.reverse_patches_by_owner(pattern_cls)
    patch_manager.reverse_patches_by_owner(match_cls)

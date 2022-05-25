# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Instrumentation for exec/eval.

This was defined outside of policy.json because we need to pass globals/locals from the
frame in which function was originally called
"""
from sys import _getframe as getframe

from contrast.extern.wrapt import register_post_import_hook

import builtins
import contrast
from contrast.agent import scope
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy import trigger_policy
from contrast.utils.patch_utils import build_and_apply_patch
from contrast.applies.assess.unsafe_code_execution import (
    apply_rule as apply_unsafe_code_exec_rule,
)
from contrast.utils.decorators import fail_quietly


INSTRUMENTED_FRAME_DEPTH = 1


@fail_quietly("Error applying rule for exec/eval patch")
def apply_rule(rule_applicator, orig_func, result, args, kwargs):
    context = contrast.CS__CONTEXT_TRACKER.current()
    if not (context and context.propagate_assess):
        return

    with scope.contrast_scope():
        rule_applicator("BUILTIN", orig_func.__name__, result, args, kwargs)


@fail_quietly("Error running path traversal assess rule")
def apply_pt_rule(module, method, result, args, kwargs):
    policy = Policy()
    trigger_rule = policy.triggers["path-traversal"]

    trigger_nodes = trigger_rule.find_trigger_nodes(module, method)

    trigger_policy.apply(trigger_rule, trigger_nodes, result, args, kwargs)


def build_exec_eval_patch(orig_func, _, rule_applicator):
    def exec_eval_patch(code, globs=None, locs=None):
        """
        Run exec/eval call with proper context to adjust for current frame

        Code ported from six module
        See https://github.com/benjaminp/six/blob/master/six.py#L694

        Reapplying the context from the 3rd frame (from top of stack) is necessary
        because the globals and locals in that frame are used in the original call to
        exec/eval. The exception to this is if the caller passes custom globals/locals
        to the function.

        If we fail provide this context we will see a number of errors due to things
        not defined in the scope of this function upon calling the original function
        definition.
        """
        result = None

        if globs is None:
            frame = getframe(INSTRUMENTED_FRAME_DEPTH)

            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs

        try:
            result = orig_func(code, globs, locs)
        except Exception:
            result = None
            raise
        finally:
            apply_rule(rule_applicator, orig_func, result, (code,), {})

        return result

    return exec_eval_patch


def patch_exec_and_eval(builtins_module):
    build_and_apply_patch(
        builtins_module, "eval", build_exec_eval_patch, (apply_unsafe_code_exec_rule,)
    )

    build_and_apply_patch(
        builtins_module,
        "exec",
        build_exec_eval_patch,
        (apply_unsafe_code_exec_rule,),
    )


def register_patches():
    register_post_import_hook(patch_exec_and_eval, builtins.__name__)

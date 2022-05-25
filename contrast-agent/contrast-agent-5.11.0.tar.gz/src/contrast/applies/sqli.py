# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Rule applicator for SQLi for dbapi2-compliant modules
"""
import contrast
from contrast.agent import scope
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy.analysis import skip_analysis
from contrast.agent.assess.policy import trigger_policy
from contrast.agent.settings import Settings
from contrast.utils.decorators import fail_quietly


@fail_quietly("Error running SQLi assess rule")
def assess_rule(context, adapter_name, method, result, args, kwargs):
    """
    Apply assess SQLi rule

    @param context: Current RequestContext instance
    @param adapter_name: String representing the adapter module (e.g. "sqlite3")
    @param method: String representing the database method (e.g. "execute")
    @param result: Object representing result of database action
    @param args: The args tuple passed to the original database function
    @param kwargs: The kwargs dict passed to the original database function
    """
    if scope.in_trigger_scope():
        return

    context.activity.query_count += 1

    policy = Policy()

    rule = policy.triggers["sql-injection"]
    trigger_nodes = rule.find_trigger_nodes(f"{adapter_name}.Cursor", method)

    trigger_policy.apply(rule, trigger_nodes, result, args, kwargs)


def apply_rule(adapter_name, orig_func, args, kwargs):
    """
    Common API for applying SQLi rule (applies both protect and assess rules)

    Applies the assess rule if assess is enabled. If protect is enabled,
    applies the protect rule. Important caveats:
      - neither rule will be applied if there is not an active request context
      - the assess rule will not be applied if we are already in scope

    The protect rule *must* be applied prior to calling the original function.
    This is the only way that we can raise a SecurityException if the rule is
    in BLOCK mode.

    The assess rule *must* be applied even if the original function results in
    an exception. Otherwise we won't detect vulnerable dataflows that may have
    just happened to result in an exception under testing.

    @param adapter_name: String representing the adapter (e.g. "sqlite3")
    @param orig_func: Original function (i.e. the one replaced by the patch)
    @param args: The args passed to the original database function
    @param kwargs: The kwargs passed to the original database function

    @return: Returns the object that is returned by calling orig_func
    """
    context = contrast.CS__CONTEXT_TRACKER.current()
    result = None

    if context is not None:
        _protect_rule(context, adapter_name, orig_func.__name__, args, kwargs)

    try:
        result = orig_func(*args, **kwargs)
    finally:
        if not skip_analysis(context):
            assess_rule(context, adapter_name, orig_func.__name__, result, args, kwargs)

    return result


@fail_quietly("Error running SQLi protect rule")
def _protect_rule(context, adapter_name, method, args, kwargs):
    """
    Run protect SQLi analysis if it's enabled.
    """
    if not Settings().is_protect_enabled() or len(args) <= 1:
        return

    # args[0] is self, args[1] is the query
    sql = args[1]

    # TODO: PYT-986: remove creating fake policy node and patch loc policy
    from contrast.agent.policy.patch_location_policy import PatchLocationPolicy
    from contrast.agent.policy.trigger_node import TriggerNode

    trigger_node = TriggerNode(adapter_name, "unused", True, method, "ARG_0")
    patch_policy = PatchLocationPolicy(trigger_node)

    rule = Settings().protect_rules.get(SqlInjection.RULE_NAME)
    rule.protect(patch_policy, sql, args, kwargs)

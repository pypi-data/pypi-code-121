# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy import trigger_policy
from contrast.utils.decorators import fail_quietly


@fail_quietly("Error running unsafe code execution assess rule")
def apply_rule(module_name, method_name, result, args, kwargs):
    if len(args) < 1:
        return

    if not isinstance(args[0], (str, bytes, bytearray)):
        return

    policy = Policy()
    trigger_rule = policy.triggers["unsafe-code-execution"]

    trigger_nodes = trigger_rule.find_trigger_nodes(module_name, method_name)

    trigger_policy.apply(trigger_rule, trigger_nodes, result, args, kwargs)

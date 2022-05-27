# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent import scope
from contrast.agent.assess.apply_trigger import cs__apply_trigger
from contrast.utils.decorators import log_time


@log_time("applying trigger policy")
def apply(
    rule, nodes, ret, orig_args, orig_kwargs=None, **kwargs
):  # pylint: disable=redefined-builtin
    """
    Iterates over all given trigger policy nodes and applies the given rule

    This method gets called from within a patched trigger function in order
    to determine whether the given rule has been violated.

    @param rule: `TriggerRule` instance representing rule to be evaluated
    @param nodes: List of `TriggerNode` instances
    @param ret: Result returned by the trigger function
    @param args: Tuple containing args passed to trigger function
    @param kwargs: Dict containing kwargs passed to trigger function
    """
    if not scope.in_trigger_scope():
        with scope.trigger_scope():
            orig_kwargs = orig_kwargs or {}

            context = contrast.CS__CONTEXT_TRACKER.current()
            if context is None:
                return

            for node in nodes:
                if node.instance_method:
                    self_obj = orig_args[0]
                    args = orig_args[1:]  # args[0] is `self` for instance methods
                else:
                    self_obj = None  # module-level functions do not have a self
                    args = orig_args

                possible_sources = node.get_matching_sources(
                    self_obj, ret, args, orig_kwargs
                )

                if not possible_sources:
                    if not rule.dataflow:
                        cs__apply_trigger(
                            context,
                            rule,
                            node,
                            None,
                            self_obj,
                            ret,
                            None,
                            args,
                            orig_kwargs,
                        )

                    return

                for source in possible_sources:
                    if isinstance(source, dict):
                        for key, value in source.items():
                            cs__apply_trigger(
                                context,
                                rule,
                                node,
                                key,
                                self_obj,
                                ret,
                                None,
                                args,
                                orig_kwargs,
                            )
                            # pass in the key here for building_finding
                            cs__apply_trigger(
                                context,
                                rule,
                                node,
                                value,
                                self_obj,
                                ret,
                                key,
                                args,
                                orig_kwargs,
                            )
                    elif isinstance(source, (tuple, list)):
                        for item in source:
                            cs__apply_trigger(
                                context,
                                rule,
                                node,
                                item,
                                self_obj,
                                ret,
                                None,
                                args,
                                orig_kwargs,
                            )
                    else:
                        cs__apply_trigger(
                            context,
                            rule,
                            node,
                            source,
                            self_obj,
                            ret,
                            None,
                            args,
                            orig_kwargs,
                        )

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.agent.policy import constants
from contrast.agent.assess.assess_exceptions import ContrastAssessException
from contrast.agent.assess.policy.trigger_actions.default_action import DefaultAction
from contrast.agent.assess.policy.trigger_actions import redos_action
from contrast.agent.assess.policy.trigger_actions import ssrf_action
from contrast.agent.policy.policy_node import PolicyNode


class TriggerNode(PolicyNode):

    TRIGGER_ACTIONS = {
        constants.TRIGGER_ACTION_DEFAULT: DefaultAction(),
        constants.TRIGGER_ACTION_REDOS: redos_action.RedosAction(),
        constants.TRIGGER_ACTION_SSRF: ssrf_action.SsrfAction(),
    }

    def __init__(
        self,
        module,
        class_name,
        instance_method,
        method_name,
        source,
        dataflow=True,
        good_value=None,
        bad_value=None,
        action=None,
        policy_patch=True,
        rule=None,
        protect_mode=False,
        unsafe_default=False,
    ):
        super().__init__(
            module,
            class_name,
            instance_method,
            method_name,
            source,
            None,
            policy_patch=policy_patch,
        )

        self.dataflow = dataflow

        self.good_value = (
            re.compile(good_value, flags=re.IGNORECASE) if good_value else None
        )
        self.bad_value = (
            re.compile(bad_value, flags=re.IGNORECASE) if bad_value else None
        )
        self.action = action or constants.TRIGGER_ACTION_DEFAULT

        self.rule = rule

        self.protect_mode = protect_mode
        self.unsafe_default = unsafe_default

        self.validate()

    @property
    def node_type(self):
        return "TYPE_METHOD"

    @property
    def dataflow_rule(self):
        return self.dataflow

    def validate(self):
        super().validate()

        if not self.dataflow_rule:
            return

        if not (self.sources and len(self.sources) != 0):
            raise ContrastAssessException(
                f"Trigger {self.name} did not have a proper source. Unable to create."
            )

    def get_matching_sources(self, self_obj, ret, args, kwargs):
        sources = []

        for source in self.sources:
            if source == constants.OBJECT:
                sources.append(self_obj)
            elif source == constants.ALL_ARGS:
                sources.append(args)
            elif source == constants.ALL_KWARGS:
                sources.append(kwargs)
            elif source == constants.RETURN:
                sources.append(ret)
            elif isinstance(source, int) and len(args) > source:
                sources.append(args[source])
            elif kwargs and source in kwargs:
                sources.append(kwargs[source])
            elif (
                isinstance(source, str)  # only consider kwarg sources
                and self.unsafe_default
                and source not in sources
            ):
                # if the default argument for this source is unsafe and we landed
                # here, we should trigger a finding. To do so, we add `None`,
                # with the assumption that most triggers will use `None`
                # as a default, but this won't always be correct. We may add a
                # trigger that uses a boolean as a default.

                # TODO: PYT-1764 special machinery to know what the default really is
                sources.append(None)
        return sources

    def get_protect_sources(self, args, kwargs):
        self_obj = args[0] if self.instance_method else None
        args = args[1:] if self.instance_method else args
        return self.get_matching_sources(self_obj, None, args, kwargs)

    @property
    def trigger_action(self):
        return self.TRIGGER_ACTIONS.get(self.action)

    @classmethod
    def from_dict(cls, obj, dataflow=True, rule=None):
        return cls(
            obj[constants.JSON_MODULE],
            obj.get(constants.JSON_CLASS_NAME, ""),
            obj.get(constants.JSON_INSTANCE_METHOD, True),
            obj[constants.JSON_METHOD_NAME],
            obj.get(constants.JSON_SOURCE, None),
            dataflow,
            obj.get(constants.JSON_GOOD_VALUE, None),
            obj.get(constants.JSON_BAD_VALUE, None),
            obj.get(constants.JSON_ACTION, None),
            policy_patch=obj.get(constants.JSON_POLICY_PATCH, True),
            rule=rule,
            protect_mode=obj.get(constants.JSON_PROTECT_MODE, False),
            unsafe_default=obj.get(constants.JSON_UNSAFE_DEFAULT, False),
        )

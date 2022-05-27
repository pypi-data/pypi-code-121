# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy import constants
from contrast.agent.assess.assess_exceptions import ContrastAssessException
from contrast.agent.policy.constants import ALL_ARGS, ALL_KWARGS, OBJECT
from contrast.agent.policy.policy_node import PolicyNode
from contrast.utils.decorators import cached_property


class PropagationNode(PolicyNode):
    TAGGER = "Tagger"
    PROPAGATOR = "Propagator"

    def __init__(
        self,
        module,
        class_name,
        instance_method,
        method_name,
        source,
        target,
        action,
        tags=None,
        untags=None,
        policy_patch=True,
    ):
        """
        :param class_name: class of the hook
        :param instance_method: if the method is an instance method vs static/bound/unbound
        :param method_name: method name to hook
        :param source: from where the tainted data flows, cannot be None
        :param target: to where the tainted data flows, cannot be None
        :param action: how the tainted data flows from source to target, should not be None
        :param tags: array of tags to apply to the target, can be None if no tags are added
        :param untags: array of tags to remove from the target, can be None if not tags are removed
        """
        super().__init__(
            module,
            class_name,
            instance_method,
            method_name,
            source,
            target,
            tags,
            policy_patch=policy_patch,
        )

        self.action = action
        self.untags = set(untags) if untags else set()

        self.validate()

    @property
    def node_class(self):
        return self.TAGGER if self.is_tagger else self.PROPAGATOR

    @property
    def node_type(self):
        return "TYPE_TAG" if self.is_tagger else "PROPAGATOR"

    @cached_property
    def is_tagger(self):
        return bool(self.tags) or bool(self.untags)

    def validate(self):

        super().validate()

        if not (self.targets and len(self.targets) != 0):
            raise ContrastAssessException(
                f"Propagator {self.method_name} did not have a proper target. Unable to create."
            )

        if not (self.sources and len(self.sources) != 0):
            raise ContrastAssessException(
                f"Propagator {self.method_name} did not have a proper source. Unable to create."
            )

        if not self.action:
            raise ContrastAssessException(
                f"Propagator {self.method_name} did not have a proper action. Unable to create."
            )

        self.validate_untags()

    def validate_untags(self):
        if not self.untags:
            return

        for item in self.untags:
            if item not in constants.VALID_TAGS:
                raise ContrastAssessException(
                    f"{self.node_type} {self.id} did not have a valid untag. {item} is not a known value."
                )

            if self.tags and item in self.tags:
                raise ContrastAssessException(
                    f"{self.node_type} {self.id} had the same tag and untag, {item}."
                )

    def get_matching_sources(self, preshift):
        sources = []
        args = (
            preshift.args[1:]
            # The string propagation hooks do not pass `self` as part of the args tuple
            # so we need to account for that here.
            if preshift.args and self.class_name != "str" and self.instance_method
            else preshift.args
        )

        for source in self.sources:
            if source == OBJECT:
                sources.append(preshift.obj)
            elif source == ALL_ARGS:
                sources.extend(args)
            elif source == ALL_KWARGS:
                sources.append(preshift.kwargs)
            elif isinstance(source, int) and len(args) > source:
                sources.append(args[source])
            elif preshift.kwargs and source in preshift.kwargs:
                sources.append(preshift.kwargs[source])

        return sources

    @classmethod
    def from_dict(cls, obj):
        return cls(
            obj[constants.JSON_MODULE],
            obj.get(constants.JSON_CLASS_NAME, ""),
            obj.get(constants.JSON_INSTANCE_METHOD, True),
            obj[constants.JSON_METHOD_NAME],
            obj[constants.JSON_SOURCE],
            obj[constants.JSON_TARGET],
            obj[constants.JSON_ACTION],
            obj.get(constants.JSON_TAGS, []),
            obj.get(constants.JSON_UNTAGS, []),
            policy_patch=obj.get(constants.JSON_POLICY_PATCH, True),
        )

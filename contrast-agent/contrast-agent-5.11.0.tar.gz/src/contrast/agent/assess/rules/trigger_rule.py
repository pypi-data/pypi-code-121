# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy import constants
from contrast.agent.assess.assess_exceptions import ContrastAssessException
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.assess.rules.base_rule import BaseRule
from contrast.agent.assess.utils import get_properties
from contrast.api import Finding, send_finding
from contrast.utils.assess.duck_utils import safe_getattr
from contrast.utils.decorators import cached_property
from contrast.utils.string_utils import equals_ignore_case


from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class TriggerRule(BaseRule):
    UNTRUSTED = "UNTRUSTED"

    ENCODER_START = "CUSTOM_ENCODED_"
    VALIDATOR_START = "CUSTOM_VALIDATED_"
    # If a level 1 rule comes from TeamServer, it will have the
    # tag "custom-encoder-#{name}" or "custom-validator-#{name}".
    # All rules should take this into account.
    # Additionally, if something is marked "limited-chars" it means
    # it has been properly vetted to not contain dangerous input.
    LIMITED_CHARS = "LIMITED_CHARS"
    CUSTOM_ENCODED = "CUSTOM_ENCODED"
    CUSTOM_VALIDATED = "CUSTOM_VALIDATED"

    def __init__(self, name, dataflow, disallowed_tags=None, required_tags=None):
        self._name = name
        self.dataflow = dataflow
        self.nodes = []

        self.required_tags = []
        self.populate_tags(required_tags)

        self.disallowed_tags = []
        self.populate_disallowed(disallowed_tags)

        super().__init__()

    @property
    def name(self):
        return self._name

    @cached_property
    def loud_name(self):
        return str(self.name.upper().replace("-", "_"))

    def populate_tags(self, required_tags):
        if not self.dataflow:
            return

        self.validate_tags(required_tags)

        self.required_tags = required_tags if required_tags else []
        if self.UNTRUSTED not in self.required_tags:
            self.required_tags.append(self.UNTRUSTED)

    def populate_disallowed(self, disallowed_tags):
        if not self.dataflow:
            return

        self.validate_tags(disallowed_tags)

        self.disallowed_tags = disallowed_tags if disallowed_tags else []

        self.disallowed_tags.append(self.LIMITED_CHARS)
        self.disallowed_tags.append(self.CUSTOM_ENCODED)
        self.disallowed_tags.append(self.CUSTOM_VALIDATED)
        self.disallowed_tags.append(self.ENCODER_START + self.loud_name)
        self.disallowed_tags.append(self.VALIDATOR_START + self.loud_name)

    def validate_tags(self, tags):
        if not tags:
            return

        for item in tags:
            if (
                item not in constants.VALID_TAGS
                and item not in constants.VALID_SOURCE_TAGS
            ):
                raise ContrastAssessException(
                    f"Rule {self.name} had an invalid tag. {item} is not a known value"
                )

    def _is_violated(self, node, source_properties, **kwargs):
        return node.trigger_action.is_violated(
            source_properties, self.required_tags, self.disallowed_tags, **kwargs
        )

    def is_violated_properties(self, node, properties):
        """
        Determine whether rule was violated based on properties
        """
        return self._is_violated(node, properties)

    def is_violated(self, node, source, **kwargs):
        """
        Determine whether rule was violated based on source object
        """
        if self.count_threshold_reached():
            return False

        # The rule is violated if the object is marked as source
        if safe_getattr(source, "cs__source", False):
            return True

        source_properties = get_properties(source)

        return self._is_violated(node, source_properties, **kwargs)

    def extract_source(self, node, source):
        """
        Extract source from given source string based on trigger action
        """
        return node.trigger_action.extract_source(source)

    def find_trigger_nodes(self, module, method):
        """
        Find the trigger node matching the module and method for this rule

        :param module: str of the module
        :param method: str of the method name
        :return: matching TriggerNode
        """
        trigger_nodes = []

        for node in self.nodes:
            if equals_ignore_case(node.location, module) and equals_ignore_case(
                method, node.method_name
            ):
                trigger_nodes.append(node)

        return trigger_nodes

    def create_finding(self, properties, node, target, **kwargs):
        return Finding(self, properties, **kwargs)

    def build_and_append_finding(self, context, properties, node, target, **kwargs):
        finding_msg = self.create_finding(properties, node, target, **kwargs)

        # if after creating the finding, we discover that this finding already exists
        # in context.activity, then do not add it and return early
        for curr_finding in context.activity.findings:
            if finding_msg.hash_code == curr_finding.hash_code:
                return

        logger.debug(
            "Trigger %s detected: %s triggered %s",
            node.name,
            str(id(target)),
            self.name,
        )

        self.finding_reported()
        send_finding(finding_msg, context)

    JSON_NAME = "name"
    JSON_DISALLOWED_TAGS = "disallowed_tags"
    JSON_REQUIRED_TAGS = "required_tags"
    JSON_NODES = "nodes"
    JSON_DATAFLOW = "dataflow"

    @classmethod
    def from_dict(cls, obj):
        dataflow = obj.get(cls.JSON_DATAFLOW, None)

        if dataflow is None:
            dataflow = True

        rule = cls(
            obj[cls.JSON_NAME],
            dataflow,
            obj.get(cls.JSON_DISALLOWED_TAGS, None),
            obj.get(cls.JSON_REQUIRED_TAGS, None),
        )

        for item in obj[cls.JSON_NODES]:
            node = TriggerNode.from_dict(item, dataflow, rule)

            # Uncomment if we re-implement version_mismatch
            # if not node.version_mismatch:
            rule.nodes.append(node)

        return rule

    def __repr__(self):
        return f"{self.__class__.__name__} - {self.name}"

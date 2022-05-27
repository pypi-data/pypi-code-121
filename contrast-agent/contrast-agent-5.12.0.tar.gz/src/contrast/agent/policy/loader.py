# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from collections import OrderedDict, defaultdict
import json
from os import path

import contrast
from contrast.agent.policy.patch_location_policy import PatchLocationPolicy
from contrast.agent.assess.policy.deadzone_node import DeadZoneNode
from contrast.agent.assess.policy.propagation_node import PropagationNode
from contrast.agent.assess.policy.source_node import SourceNode
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.assess.rules.dataflow_rule import DataflowRule
from contrast.agent.assess.rules.non_dataflow_rule import NonDataflowRule
from contrast.agent.policy.constants import (
    JSON_NAME,
    PROPAGATION_KEY,
    SOURCES_KEY,
    TRIGGERS_KEY,
    DEADZONE_KEY,
)
from contrast.agent.assess.rules.providers.hardcoded_key import HardcodedKey
from contrast.agent.assess.rules.providers.hardcoded_password import HardcodedPassword
from contrast.agent.assess.rules.triggers import (
    HttpOnlyRule,
    SecureFlagMissingRule,
    SessionTimeoutRule,
    SessionRewritingRule,
)
from contrast.utils.singleton import Singleton
from contrast.utils.decorators import cached_property, fail_loudly

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


POLICY_DATA_DIR = path.join(path.dirname(contrast.__file__), "data")


class Policy(Singleton):
    POLICY_JSON_PATH = path.join(POLICY_DATA_DIR, "policy.json")

    PROVIDER_CLASSES = [HardcodedKey, HardcodedPassword]
    TRIGGER_RULES = {
        "httponly": HttpOnlyRule,
        "session-timeout": SessionTimeoutRule,
        "secure-flag-missing": SecureFlagMissingRule,
        "session-rewriting": SessionRewritingRule,
    }

    def init(self):
        """
        Singletons should override init, not __init__.
        """
        self.sources = []
        self.propagators = []
        self.deadzones = []
        self.triggers = OrderedDict()
        self.providers = OrderedDict()

        self.propagators_by_name = defaultdict(list)
        # This is used to ensure that we only ever have one PatchLocationPolicy
        # instance per patch location.
        self.policy_by_name = OrderedDict()
        # This is used to represent a list of PatchLocationPolicy instances per each
        # module. It is what enables the application of module-level import hooks.
        self.policy_by_module = OrderedDict()

        self.protect_policy_by_module = OrderedDict()

        self.policy_data = {}

        self.initialize()

    def process_node(self, node):
        """
        Create patch location policy for node and update lookup tables if necessary
        """
        patch_policy = self.policy_by_name.setdefault(
            node.name, PatchLocationPolicy(node)
        )
        patch_policy.add_node(node)

        policy_list = self.policy_by_module.setdefault(node.module, [])
        policy_list.append(patch_policy)

        if isinstance(node, TriggerNode) and node.protect_mode:
            policy_list = self.protect_policy_by_module.setdefault(node.module, [])
            policy_list.append(patch_policy)

        return patch_policy

    def initialize(self):
        loaded_json = self._get_json_data()
        if not loaded_json:
            return

        self.policy_data = loaded_json

        self._load_sources()
        self._load_propagators()
        self._load_triggers()
        self._load_deadzones()

        self._load_providers()

    def _load_deadzones(self):
        for item in self.policy_data[DEADZONE_KEY]:
            dz = DeadZoneNode.from_dict(item)

            self.deadzones.append(dz)
            self.process_node(dz)

    def _load_sources(self):
        for framework, nodes in self.policy_data[SOURCES_KEY].items():
            for value in nodes:
                source_node = SourceNode.from_dict(framework, value)

                # Uncomment if we re-implement version_mismatch
                # if source_node.version_mismatch:
                #     continue

                if source_node.should_apply():
                    self.sources.append(source_node)
                    self.process_node(source_node)

    def _load_propagators(self):
        for item in self.policy_data[PROPAGATION_KEY]:
            prop = PropagationNode.from_dict(item)

            # Uncomment if we re-implement version_mismatch
            # if prop.version_mismatch:
            #     continue

            self.propagators.append(prop)
            self.propagators_by_name[prop.name].append(prop)
            self.process_node(prop)

    def _find_rule(self, json_node):
        """
        Find rule class corresponding to rule name

        First, look for special cases based on name. If none exist, determine whether
        to use dataflow or non-dataflow rule class based on JSON.
        """
        rule_name = json_node.get(JSON_NAME)
        trigger_rule = self.TRIGGER_RULES.get(rule_name)
        if trigger_rule:
            return trigger_rule

        is_dataflow = json_node.get(DataflowRule.JSON_DATAFLOW, True)
        return DataflowRule if is_dataflow else NonDataflowRule

    def _load_triggers(self):
        for item in self.policy_data[TRIGGERS_KEY]:
            rule_cls = self._find_rule(item)
            rule = rule_cls.from_dict(item)
            self.triggers[rule.name] = rule
            for node in rule.nodes:
                self.process_node(node)

    def _load_providers(self):
        for item in self.PROVIDER_CLASSES:
            instance = item()

            self.providers[instance.name] = instance

    @fail_loudly("Failed to read policy json file")
    def _get_json_data(self):
        with open(self.POLICY_JSON_PATH) as json_file:
            return json.load(json_file)

    @fail_loudly("Failed to add node to policy")
    def add_source_node(self, node):
        node.validate()
        self.sources.append(node)
        return self.process_node(node)

    @cached_property
    def string_method_nodes(self):
        return [
            node
            for node in self.policy_by_module["BUILTIN"]
            if node.class_name == "str"
        ]

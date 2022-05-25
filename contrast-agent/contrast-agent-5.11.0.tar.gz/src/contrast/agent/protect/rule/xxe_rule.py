# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.agent.protect.rule.xxe.entity_wrapper import EntityWrapper
from contrast.api.dtm_pb2 import RaspRuleSample, UserInput, XxeMatch, XxeWrapper
from contrast.utils.stack_trace_utils import build_and_clean_stack


class Xxe(BaseRule):
    """
    XXE Protection rule
    """

    RULE_NAME = "xxe"
    INPUT_NAME = "XML Prolog"

    EXTERNAL_ENTITY_PATTERN = re.compile(
        r"<!ENTITY\s+[a-zA-Z0-f]+\s+(?:SYSTEM|PUBLIC)\s+(.*?)>"
    )

    def __init__(self):
        super().__init__()

        self.prolog_xml = None

    def is_prefilter(self):
        return False

    def is_postfilter(self):
        return False

    def find_attack(self, candidate_string=None, **kwargs):
        if self.protect_excluded_by_code():
            return None

        last_idx = 0
        declared_entities = []
        entities_resolved = []

        for match in self.EXTERNAL_ENTITY_PATTERN.finditer(candidate_string):
            last_idx = match.end(0)

            entity_wrapper = EntityWrapper(match.group())
            if not entity_wrapper.is_external_entity():
                continue

            declared_entities.extend([self._build_match(match.group(), last_idx)])
            entities_resolved.extend([self._build_wrapper(entity_wrapper)])

        self.prolog_xml = candidate_string[:last_idx]

        attack = self.build_attack_with_match(
            candidate_string,
            declared_entities=declared_entities,
            entities_resolved=entities_resolved,
        )
        return attack

    def _build_match(self, match_string, end_idx):
        match = XxeMatch()
        match.end_idx = end_idx
        match.start_idx = end_idx - len(match_string)
        return match

    def _build_wrapper(self, entity_wrapper):
        wrapper = XxeWrapper()
        wrapper.system_id = entity_wrapper.system_id
        wrapper.public_id = entity_wrapper.public_id
        return wrapper

    def build_sample(self, evaluation, url, **kwargs):
        sample = self.build_base_sample(evaluation)
        declared_entities = kwargs["declared_entities"]
        if declared_entities:
            sample.xxe.declared_entities.extend(declared_entities)

        entities_resolved = kwargs["entities_resolved"]
        if entities_resolved:
            sample.xxe.entities_resolved.extend(entities_resolved)

        sample.xxe.xml = self.prolog_xml
        return sample

    def build_base_sample(self, evaluation, prebuilt_stack=None):
        sample = RaspRuleSample()
        sample.stack_trace_elements.extend(build_and_clean_stack())

        sample.user_input.CopyFrom(self.build_user_input(evaluation))

        return sample

    def build_user_input(self, evaluation):
        ui = UserInput()
        ui.key = self.INPUT_NAME
        ui.input_type = UserInput.UNKNOWN
        ui.value = self.prolog_xml
        return ui

    def infilter_kwargs(self, user_input, patch_policy):
        return dict(framework=patch_policy.method_name)

    def sample_dtm_to_json(self, sample):
        return {
            "xml": sample.xxe.xml,
            "declaredEntities": [
                {"start": entity.start_idx, "end": entity.end_idx}
                for entity in sample.xxe.declared_entities
            ],
            "entitiesResolved": [
                {"systemId": entity.system_id, "publicId": entity.public_id}
                for entity in sample.xxe.entities_resolved
            ],
        }

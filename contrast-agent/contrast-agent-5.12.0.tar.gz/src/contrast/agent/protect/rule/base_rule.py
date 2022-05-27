# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import inspect

import contrast
from contrast.agent.settings import Settings
from contrast.api.dtm_pb2 import AttackResult, RaspRuleSample, UserInput
from contrast.api.settings_pb2 import ProtectionRule
from contrast.api.settings_pb2 import InputAnalysisResult
from contrast.utils.decorators import fail_loudly, fail_quietly
from contrast.utils.decorators import cached_property
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.stack_trace_utils import build_and_clean_stack
from contrast.utils.timer import now_ms
from contrast.extern import structlog as logging
from contrast.utils.string_utils import ensure_string

logger = logging.getLogger("contrast")


BLOCKING_RULES = frozenset([ProtectionRule.BLOCK, ProtectionRule.BLOCK_AT_PERIMETER])
PREFILTER_RULES = frozenset([ProtectionRule.BLOCK_AT_PERIMETER])
POSTFILTER_RULES = frozenset(
    [ProtectionRule.BLOCK, ProtectionRule.MONITOR, ProtectionRule.PERMIT]
)

PREFILTER = "prefilter"
INFILTER = "infilter"
POSTFILTER = "postfilter"


class BaseRule(object):
    """
    Base rule object that all protection rules will inherit
    """

    RULE_NAME = "base-rule"

    def __init__(self):
        self.settings = Settings()
        self.settings.protect_rules[self.name] = self

    @property
    def name(self):
        return self.RULE_NAME

    @property
    def mode(self):
        """
        Return the mode for this rule based.

        Order of precedence:
        1. Config (contract_security.yaml)
        2. Settings from TS (Settings DTM)
        3. Default mode

        We have to assert if config_mode is not None because 0 is falsy
        """
        config_mode = self.mode_from_config()

        return config_mode if config_mode is not None else self.mode_from_settings()

    @cached_property
    def config_rule_path_mode(self):
        return f"protect.rules.{self.name}.mode"

    def mode_from_config(self):
        """
        Retrieve the mode based on the rule name

        Return None if it does no exist in the config which means default to settings
        """
        return self.settings.config.get(self.config_rule_path_mode, None)

    def mode_from_settings(self):
        """
        Retrieve the mode based on the rule name
        """
        app_settings = (
            self.settings.direct_ts_app_settings
            if self.settings.config.is_service_bypassed
            else self.settings.application_settings
        )
        for definition in app_settings.protection_rules:
            # "name" here is the "id" in the Settings DTM
            if definition.id == self.name:
                return definition.mode
        return ProtectionRule.NO_ACTION

    def is_prefilter(self):
        """
        Checks if a rules mode is for prefilter
        """
        return self.enabled and self.mode in PREFILTER_RULES

    def is_postfilter(self):
        """
        Checks if a rules mode is for postfilter
        """
        return self.enabled and self.mode in POSTFILTER_RULES

    def is_blocked(self):
        """
        Checks if a rules mode is for blocking
        """
        return self.enabled and self.mode in BLOCKING_RULES

    @property
    def enabled(self):
        """
        A rule is enabled only if all 3 conditions are met:
        1. protect is enabled in both config and server settings
        2. rule is not in disabled rules list
        3. rule mode is not NO_ACTION
        """
        if not self.settings.is_protect_enabled():
            return False

        disabled_rules = self.settings.config.get("protect.rules.disabled_rules", [])
        if disabled_rules and self.name in disabled_rules:
            return False

        return self.mode != ProtectionRule.NO_ACTION

    def should_block(self, attack):
        return attack and attack.response == AttackResult.BLOCKED

    def excluded(self, exclusions):
        """
        Check if rule is being excluded from evaluation
        :param exclusions:
        :return: True if excluded, else False
        """

        if not exclusions or len(exclusions) == 0:
            return False

        logger.debug("Checking %s exclusion(s) in %s", len(exclusions), self.name)
        return any(ex.match_protect_rule(self.name) for ex in exclusions)

    def protect_excluded_by_code(self):
        """
        Checks if analysis of code needs to be ignored based on code exceptions

        Checks stack for code exceptions
        """
        code_exclusions = self.settings.code_exclusion_matchers
        if not code_exclusions or len(code_exclusions) == 0:
            return False

        current_frame = inspect.currentframe()
        called_frame = inspect.getouterframes(current_frame, 2)
        logger.debug("caller name: %s", called_frame[1][3])
        stack = inspect.stack()

        return any(
            m.match_protect_rule(self.name) and m.match_code(stack)
            for m in code_exclusions
        )

    def prefilter(self):
        """
        Scans the input analysis for the rule and looks for matched attack signatures

        Will throw a SecurityException if a response needs to be blocked
        """
        logger.debug("PROTECT: Prefilter for %s", self.name)

        attack = self.find_attack(analysis_stage=PREFILTER)
        if attack is None or len(attack.samples) == 0:
            return

        self._append_to_activity(attack)

        if attack.response == AttackResult.BLOCKED_AT_PERIMETER:
            raise SecurityException(
                self, "Rule triggered in prefilter. Request blocked."
            )

    def infilter(self, match_string, **kwargs):
        """
        Scans the input analysis for the rule and looks for matched attack signatures. The call to this method may be
        rule specific and include additional context in a args list.
        """
        if self.mode in [ProtectionRule.NO_ACTION, ProtectionRule.PERMIT]:
            return

        logger.debug("PROTECT: Infilter for %s", self.name)

        attack = self.find_attack(match_string, analysis_stage=INFILTER, **kwargs)
        if attack is None or len(attack.samples) == 0:
            return

        self._append_to_activity(attack)

        if self.should_block(attack):
            raise SecurityException(self, f"Rule triggered. {match_string} blocked.")

    @fail_loudly("Failed to run protect rule")
    def protect(self, patch_policy, user_input, args, kwargs):
        if not self.enabled:
            return

        if self.skip_protect_analysis(user_input, args, kwargs):
            return

        self.increase_query_count()

        user_input = self.convert_input(user_input)
        if not user_input:
            return

        self.log_safely(patch_policy.method_name, user_input)

        self.infilter(user_input, **self.infilter_kwargs(user_input, patch_policy))

    def infilter_kwargs(self, user_input, patch_policy):
        return {}

    def skip_protect_analysis(self, user_input, args, kwargs):
        """
        We only want to run protect on user input that is of a type supported
        by the rule.

        Most rules use this implementation, but some override this depending on
        expected user input types.

        :return: Bool if to skip running protect infilter
        """
        if not user_input:
            return True

        if isinstance(user_input, (str, bytes)):
            return False

        logger.debug(
            "WARNING: unknown input type %s for rule %s", type(user_input), self.name
        )

        return True

    def convert_input(self, user_input):
        return ensure_string(user_input)

    def increase_query_count(self):
        """Only rules for database support increase the query count"""
        pass

    def postfilter(self):
        """
        Scans the input analysis for the rule and looks for matched attack signatures

        Appends attacker to the context if a positive evaluation is found
        """
        logger.debug("PROTECT: Postfilter for %s", self.name)

        if self.mode in [ProtectionRule.NO_ACTION, ProtectionRule.PERMIT]:
            return

        attack = self.find_attack(analysis_state=POSTFILTER)
        if attack is None or len(attack.samples) == 0:
            return

        self._append_to_activity(attack)

        if self.should_block(attack):
            raise SecurityException(
                self, f"Rule triggered in postfilter. {self.name} blocked."
            )

    def find_attack(self, candidate_string=None, analysis_stage=None, **kwargs):
        """
        Finds the attacker in the original string if present
        """
        if candidate_string is not None:
            logger.debug("Checking for %s in %s", self.name, candidate_string)

        if self.protect_excluded_by_code():
            return None

        # if rule mode is BAP, only speedracer determines if we should block
        if (
            analysis_stage == PREFILTER
            and self.mode == ProtectionRule.BLOCK_AT_PERIMETER
        ):
            return None

        evaluations_for_rule = self.evaluations_for_rule()

        attack = None
        for evaluation in evaluations_for_rule:
            if analysis_stage == POSTFILTER and (
                evaluation.attack_count > 0
                or evaluation.input_type == UserInput.QUERYSTRING
            ):
                continue

            if candidate_string:
                if candidate_string.find(evaluation.value) == -1:
                    continue

                attack = self.build_attack_with_match(
                    candidate_string, evaluation, attack, **kwargs
                )
            else:
                attack = self.build_attack_without_match(evaluation, attack, **kwargs)

        return attack

    def build_attack_with_match(
        self, candidate_string, evaluation=None, attack=None, **kwargs
    ):
        attack = self.build_or_append_attack(
            evaluation, attack, candidate_string, **kwargs
        )

        if evaluation:
            evaluation.attack_count += 1

        attack.response = self.response_from_mode(self.mode)
        self.log_rule_matched(evaluation, attack.response, candidate_string)
        return attack

    def build_attack_without_match(self, evaluation=None, attack=None, **kwargs):
        if self.mode == ProtectionRule.BLOCK_AT_PERIMETER:
            attack = self.build_or_append_attack(evaluation, attack, **kwargs)

            attack.response = self.response_from_mode(self.mode)
            self.log_rule_matched(evaluation, attack.response)
        elif evaluation is None or (
            evaluation.attack_count == 0
            and evaluation.score_level > InputAnalysisResult.WORTHWATCHING
        ):
            # an exploit was found first so we do not need to probe this
            attack = self.build_or_append_attack(evaluation, attack, **kwargs)
            attack.response = AttackResult.PROBED
            self.log_rule_probed(evaluation)

        return attack

    def build_or_append_attack(
        self, evaluation, attack=None, candidate_string=None, **kwargs
    ):
        if attack is None:
            attack = self.build_base_attack()
        self.append_sample(evaluation, attack, candidate_string, **kwargs)
        return attack

    def build_base_attack(self):
        attack = AttackResult()
        attack.rule_id = self.name
        return attack

    def append_sample(self, evaluation, attack, candidate_string, **kwargs):
        attack.samples.extend(
            [self.build_sample(evaluation, candidate_string, **kwargs)]
        )

    def build_sample(self, evaluation, candidate_string, **kwargs):
        return self.build_base_sample(evaluation)

    def build_user_input(self, evaluation):
        return UserInput(
            input_type=evaluation.input_type,
            matcher_ids=evaluation.ids,
            path=evaluation.path,
            key=evaluation.key,
            value=evaluation.value,
        )

    def build_base_sample(self, evaluation, prebuilt_stack=None):
        stack = prebuilt_stack if prebuilt_stack else build_and_clean_stack()
        sample = RaspRuleSample()
        sample.stack_trace_elements.extend(stack)

        if evaluation:
            sample.user_input.CopyFrom(self.build_user_input(evaluation))

        sample.timestamp_ms = now_ms()

        return sample

    def log_rule_matched(self, evaluation, response, _=None):
        """
        Logs the exploit for the rule to the security logger
        """
        if evaluation:
            key = str(evaluation.key) if evaluation.key else ""
            input_type_name = UserInput.InputType.Name(evaluation.input_type)

            rule_message = (
                f"{self.name} - {ensure_string(evaluation.value, errors='replace')}"
            )

            message = f"The {input_type_name} {key} had a value that successfully exploited: {ensure_string(rule_message, errors='replace')}"
        else:
            message = self.effective_attack_message()

        logger.debug("%s %s", AttackResult.ResponseType.Name(response), message)

    def log_rule_probed(self, evaluation):
        """
        Logs the probed attack for the rule to the security logger
        """

        if evaluation:
            key = str(evaluation.key) if evaluation.key else ""

            input_type_name = UserInput.InputType.Name(evaluation.input_type)

            rule_message = (
                f"{self.name} - {ensure_string(evaluation.value, errors='replace')}"
            )

            message = (
                f"The {input_type_name} {key} had a value that matched a signature but did not"
                f" exploit: {ensure_string(rule_message, errors='replace')}"
            )
        else:
            message = self.effective_attack_message()

        logger.debug(message)

    def effective_attack_message(self):
        return f"An effective attack was detected against {self.name}."

    def _append_to_activity(self, attack_result):
        """
        Appends the current context's request dtm to the defend activity along with attacks to the rules
        """
        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None:
            # do not remove; this case is not yet well-understood
            logger.debug(
                "WARNING: failed to get request context in _append_to_activity"
            )
            return

        context.activity.results.extend([attack_result])
        context.attacks.append(attack_result)

    _RESPONSE_MAP = {
        ProtectionRule.MONITOR: AttackResult.MONITORED,
        ProtectionRule.BLOCK: AttackResult.BLOCKED,
        ProtectionRule.BLOCK_AT_PERIMETER: AttackResult.BLOCKED_AT_PERIMETER,
        ProtectionRule.NO_ACTION: AttackResult.NO_ACTION,
        ProtectionRule.PERMIT: AttackResult.NO_ACTION,
    }

    def response_from_mode(self, mode):
        return self._RESPONSE_MAP.get(mode)

    def evaluations_for_rule(self):
        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None:
            # do not remove; this case is not yet well-understood
            logger.debug(
                "WARNING: failed to get request context in evaluations_for_rule"
            )
            return []

        if context.speedracer_input_analysis is None:
            return []

        evaluations = context.speedracer_input_analysis.results
        return [
            evaluation for evaluation in evaluations if evaluation.rule_id == self.name
        ]

    @fail_quietly("Failed to log user input for protect rule")
    def log_safely(self, method_name, user_input):
        """
        Attempt to log user supplied input but do not fail if unable to do so.
        """
        logger.debug(
            "Applying %s rule method %s with user input %s",
            self.name,
            method_name,
            ensure_string(user_input, errors="replace"),
        )

    def sample_dtm_to_json(self, _):
        """
        Used to extract rule-specific details inside a RaspRuleSample
        Should be implemented by each child class unless no details are known.
        """
        return {}

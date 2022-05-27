# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.agent.protect.rule.deserialization.pickle_searcher import PickleSearcher
from contrast.agent.protect.rule.deserialization.yaml_searcher import YAMLSearcher
from contrast.api.dtm_pb2 import AttackResult, UserInput
from contrast.api.settings_pb2 import InputAnalysisResult
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.string_utils import ends_with_any
from contrast.utils.stack_trace_utils import build_and_clean_stack

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Deserialization(BaseRule):
    """
    Deserialization Protection rule
    """

    RULE_NAME = "untrusted-deserialization"

    # pickle and pyyaml both use load
    METHODS = [
        "loads",
        "load",
        "construct_object",
        "construct_python_object_apply",
        "construct_mapping",
        "make_python_instance",
    ]
    FILENAMES = ["pickle.py", "yaml.constructor.py", "yaml.__init__.py"]

    UNKNOWN = "UNKNOWN"

    @property
    def custom_searchers(self):
        return [PickleSearcher(), YAMLSearcher()]

    def is_prefilter(self):
        return False

    def is_postfilter(self):
        return False

    def skip_protect_analysis(self, user_input, args, kwargs):
        """
        Deserialization rule will receive io streams as user input.

        :return: Bool if to skip running protect infilter
        """
        if not user_input:
            return True

        # checking if obj has attr "read" is more robust than using isinstance
        if hasattr(user_input, "read"):
            return False

        return super().skip_protect_analysis(user_input, args, kwargs)

    def convert_input(self, user_input):
        if isinstance(user_input, (str, bytes)):
            data = user_input
        else:
            data = self._get_stream_data(user_input)

        return super().convert_input(data)

    def _get_stream_data(self, user_input):
        """
        Get data from a stream object but make sure to return the stream position
        to the original location.

        :param user_input: obj we expect to be a stream with attrs read, tell and seek
        :return: str or bytes
        """
        if not all(hasattr(user_input, attr) for attr in ["read", "tell", "seek"]):
            return ""

        # Find current steam position
        try:
            seek_loc = user_input.tell()
        except Exception:
            seek_loc = 0

        # Read the object data
        try:
            data = user_input.read()
        except Exception:
            data = ""

        # Return object to original stream position so it can be re-read
        try:
            user_input.seek(seek_loc)
        except Exception:
            pass

        return data

    def infilter(self, match_string, **kwargs):
        logger.debug("PROTECT: Infilter for %s", self.name)

        if self.check_for_deserialization(
            kwargs.get("stack_elements", []), kwargs.get("deserializer", "")
        ):
            self.report_attack_without_finding(match_string, **kwargs)

        return super().infilter(match_string, **kwargs)

    def find_attack(self, candidate_string=None, **kwargs):
        """
        Finds the attacker in the original string if present
        """
        if candidate_string is not None:
            logger.debug("Checking for %s in %s", self.name, candidate_string)

        if self.protect_excluded_by_code():
            return None

        attack = None
        if self.evaluate_custom_searchers(candidate_string):
            evaluation = self.build_evaluation(candidate_string)
            attack = self.build_attack_with_match(
                candidate_string, evaluation, attack, **kwargs
            )

        return attack

    def report_attack_without_finding(self, value, **kwargs):
        evaluation = self.build_evaluation(value)
        attack = self.build_attack_with_match(value, evaluation, **kwargs)

        attack.response = AttackResult.BLOCKED

        self._append_to_activity(attack)

        raise SecurityException(
            self,
            "Found deserialization attempt in stack, triggered in infilter. Blocked.",
        )

    def check_for_deserialization(self, stack_elements, deserializer):
        found_on_stack = False

        for element in stack_elements[::-1]:
            lower_file_name = element.file_name.lower()

            if (
                element.method_name
                and element.method_name in self.METHODS
                and (
                    lower_file_name in self.FILENAMES
                    or ends_with_any(lower_file_name, self.FILENAMES)
                )
            ):
                found_on_stack = True
                break

        if found_on_stack and deserializer == self.UNKNOWN:
            return True

        return False

    def build_sample(self, evaluation, input_value, **kwargs):
        sample = self.build_base_sample(evaluation)

        sample.untrusted_deserialization.command = False

        if "deserializer" in kwargs:
            sample.untrusted_deserialization.deserializer = kwargs["deserializer"]

        return sample

    def evaluate_custom_searchers(self, attack_vector):
        searcher_score = 0
        for searcher in self.custom_searchers:
            impact = searcher.impact_of(attack_vector)

            if impact > 0:
                logger.debug("Match on custom searcher: %s", searcher.searcher_id)

                searcher_score += impact
                if searcher_score >= searcher.IMPACT_HIGH:
                    return True

        return False

    def build_evaluation(self, value):
        """
        Given a user-input value, aka gadget, create an InputAnalysisResult instance.

        :param value: the user input containing a Gadget
        :return: InputAnalysisResult for this input
        """
        ia_result = InputAnalysisResult()
        ia_result.rule_id = self.name
        ia_result.input_type = UserInput.UNKNOWN
        ia_result.value = value
        ia_result.key = self.name
        return ia_result

    def infilter_kwargs(self, user_input, patch_policy):
        stack_elements = build_and_clean_stack()

        return dict(
            deserializer=patch_policy.method_name, stack_elements=stack_elements
        )

    def sample_dtm_to_json(self, sample):
        return {
            "command": sample.untrusted_deserialization.command,
            "deserializer": sample.untrusted_deserialization.deserializer,
        }

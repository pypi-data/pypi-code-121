# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent.protect.rule.base_rule import BaseRule, UserInput

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class MethodTampering(BaseRule):
    RULE_NAME = "method-tampering"
    USER_INPUT_KEY = UserInput.InputType.Name(UserInput.METHOD)

    def postfilter(self):
        """
        At postfilter we generate activity if input analysis was found and depending on application response code.

        if response code is either 4xx or 5xx, application was not exploited (only probed) by an unexpected HTTP method.
        If response code is anything else, then an unexpected HTTP method successfully exploited the application.
        """
        logger.debug("PROTECT: Postfilter for %s", self.name)

        evaluations_for_rule = self.evaluations_for_rule()

        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None or not hasattr(context, "response"):
            # do not remove; this case is not yet well-understood
            logger.debug("WARNING: failed to get context in MethodTampering.postfilter")
            return

        response_code = context.response.status_code

        for evaluation in evaluations_for_rule:
            if str(response_code).startswith("4") or str(response_code).startswith("5"):
                attack = self.build_attack_without_match(
                    method=evaluation.value,
                    response_code=response_code,
                )
            else:
                attack = self.build_attack_with_match(
                    None,
                    method=evaluation.value,
                    response_code=response_code,
                )
            self._append_to_activity(attack)

    def build_sample(self, evaluation, candidate_string, **kwargs):
        sample = self.build_base_sample(None)

        method = kwargs.get("method", "")

        sample.method_tampering.method = method
        sample.method_tampering.response_code = kwargs.get("response_code", -1)
        sample.user_input.CopyFrom(self.build_user_input(method))

        return sample

    def build_user_input(self, method):
        ui = UserInput()
        ui.key = self.USER_INPUT_KEY
        ui.input_type = UserInput.METHOD
        ui.value = method
        return ui

    def sample_dtm_to_json(self, sample):
        return {
            "method": sample.method_tampering.method,
            "responseCode": sample.method_tampering.response_code,
        }

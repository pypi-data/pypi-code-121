# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Functions for communication with speedracer to receive input analysis
"""
import contrast
from contrast.agent import service_client
from contrast.agent.settings import Settings
from contrast.api.settings_pb2 import ProtectionRule
from contrast.utils.exceptions.security_exception import SecurityException

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def get_input_analysis():
    logger.debug("Getting input analysis from speedracer ...")

    context = contrast.CS__CONTEXT_TRACKER.current()
    message = context.activity.http_request

    responses = service_client.send_messages_get_responses([message])
    speedracer_response = responses[0] if responses else None

    if not speedracer_response or not speedracer_response.protect_state:
        logger.debug("No response from speedracer: %s", speedracer_response)
        return None

    if speedracer_response.input_analysis is None:
        logger.debug(
            "Speedracer returned nil input analysis - no evaluation for request"
        )

    context.do_not_track = speedracer_response.protect_state.track_request

    if speedracer_response.protect_state.security_exception:
        create_activity_from_speedracer_input_analysis(
            speedracer_response.input_analysis, context
        )
        raise SecurityException(context, "Speedracer said to block this request")

    logger.debug("Speedracer input analysis: %s", speedracer_response.input_analysis)
    return speedracer_response.input_analysis


def create_activity_from_speedracer_input_analysis(speedracer_input_analysis, context):
    """
    If speedracer returns any input analysis results, we should create
    attack result samples in case it did not create it.

    """
    if speedracer_input_analysis is None:
        return

    settings = Settings()

    for evaluation in speedracer_input_analysis.results:
        rule = settings.protect_rules[evaluation.rule_id]
        if rule.mode == ProtectionRule.BLOCK:
            # special case for rules (xss) that used to have infilter but now are only prefilter / BAP
            attack = rule.build_attack_with_match(evaluation.value, evaluation)
        else:
            attack = rule.build_attack_without_match(evaluation=evaluation)
        context.activity.results.extend([attack])
        context.attacks.append(attack)

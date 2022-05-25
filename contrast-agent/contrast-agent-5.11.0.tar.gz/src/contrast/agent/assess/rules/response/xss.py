# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent import scope
from contrast.agent.assess.policy import trigger_policy
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def analyze_xss(context, trigger_node):
    logger.debug("ASSESS: Running xss response analysis")

    # it is possible other forms (capital case) variants exist
    accepted_xss_response_content_types = [
        "/csv",
        "/javascript",
        "/json",
        "/pdf",
        "/x-javascript",
        "/x-json",
        "/plain",
    ]

    content_type = context.response.headers.get("content-type", "")

    if not any(
        [name for name in accepted_xss_response_content_types if name in content_type]
    ):
        apply_policy(context, trigger_node)


def apply_policy(context, trigger_node):
    """
    Evaluate xss rule for assess

    The xss rule is applied to the response body in order to determine whether it
    contains untrusted data. We rely on propagation through any template rendering
    and through the framework. The expectation is that untrusted data from
    a request will propagate successfully all the way to the response body, which
    we are able to see here.

    Each child middleware class must implement specific logic for the trigger node
    since the reporting will differ between frameworks.
    """
    from contrast.agent.policy.loader import Policy

    policy = Policy()

    rule = policy.triggers["reflected-xss"]

    # We need to exit scope here in order to account for the fact that some
    # frameworks evaluate the content lazily. We don't want to be in scope when
    # that occurs since it would make us lose propagation. This would prevent us
    # from seeing the response as a tracked string, which we require in order to
    # apply the rule.
    with scope.pop_contrast_scope():
        result = context.response.body

    trigger_node, args = trigger_node

    trigger_policy.apply(rule, [trigger_node], result, args)

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Utilities for updating preflight hashes with information from requests

This module is primarily tested by framework tests.
"""
from contrast.utils.decorators import fail_loudly
from contrast.utils.digest_utils import Digest

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def _get_route_for_hash(context):
    """
    Get route to be used for hashing according to preflight spec:

        1. Route signature
        2. Normalized uri - the agents best attempt at normalizing the URI
           for path parameters. typically this involves a regex to abstract
           numeric or UUID path segments, but is not well defined. ideally,
           this case will phase out as route coverage expands, so the
           definition does not need to be consistent across agents so long
           as it is consistent within them.
        3. Raw uri
    """
    route = context.current_route
    if route is not None and route.route:
        return route.route

    normalized_uri = context.request.get_normalized_uri()
    return normalized_uri or context.request.path_qs


def _get_verb_for_hash(context):
    route = context.current_route
    if route is not None and route.verb:
        return route.verb

    return context.request.method


@fail_loudly("Failed to update preflight hashes")
def update_preflight_hashes(context):
    """
    Update preflight hashes for all findings with available route/request info

    @param context: Current request context
    """
    for finding in context.activity.findings:
        hasher = Digest()
        hasher.update(finding.hash_code)

        hasher.update(_get_route_for_hash(context))
        hasher.update(_get_verb_for_hash(context))

        hash_code = hasher.finish()

        finding.hash_code = hash_code
        finding.preflight = ",".join([finding.rule_id, hash_code])
        logger.debug("updated preflight value: %s", finding.preflight)

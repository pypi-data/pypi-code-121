# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

import contrast
from contrast.extern.wrapt import register_post_import_hook
from contrast.agent.assess.policy.analysis import analyze
from contrast.agent.policy import patch_manager
from contrast.agent.policy.applicator import apply_assess_patch
from contrast.agent.policy.loader import Policy
from contrast.patches import urllib_patch
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch

PYRAMID_SESSION_MODULE = "pyramid.session"


@fail_quietly("Failed to apply policy to new session class")
def _apply_policy(session_cls):
    policy = Policy()

    for patch_policy in policy.policy_by_module[PYRAMID_SESSION_MODULE]:
        if patch_policy.class_name == "CookieSession":
            apply_assess_patch(session_cls, patch_policy)


@fail_quietly("Failed to apply assess policy for BaseCookieSessionFactory")
def _apply_assess(result, args, kwargs):
    context = contrast.CS__CONTEXT_TRACKER.current()

    policy = Policy()
    patch_policy = policy.policy_by_name["pyramid.session.BaseCookieSessionFactory"]

    analyze(context, patch_policy, result, args, kwargs)


def build_base_cookie_session_factory_patch(orig_func, patch_policy):
    def base_cookie_session_factory(*args, **kwargs):
        """
        base_cookie_session_factory is a function that returns a new CookieSession class

        Since we can't instrument the new class directly using normal policy machinery,
        we instead apply our policy on-demand to the newly created class.
        """
        session_cls = None

        try:
            session_cls = orig_func(*args, **kwargs)
            _apply_policy(session_cls)
        finally:
            _apply_assess(session_cls, args, kwargs)

        return session_cls

    return base_cookie_session_factory


def patch_session_pyramid(pyramid_session_module):
    build_and_apply_patch(
        pyramid_session_module,
        "BaseCookieSessionFactory",
        build_base_cookie_session_factory_patch,
    )


def patch_encode_pyramid(pyramid_encode_module):
    # We go ahead and apply all urllib patches here (even though policy
    # patches will happen later on) because we MUST have some urllib policy patches
    # already applied for these non-policy patches to work.
    # This would not be necessary if in _enable_patches policy_patches were applied
    # first.
    urllib_patch.register_patches()

    # We can reuse the urllib.parse.urlencode patch since it's exactly the same
    # as the pyramid.encode.urlencode patch
    build_and_apply_patch(
        pyramid_encode_module, "urlencode", urllib_patch.build_urlencode_patch
    )


def register_patches():
    register_post_import_hook(patch_session_pyramid, PYRAMID_SESSION_MODULE)
    register_post_import_hook(patch_encode_pyramid, "pyramid.encode")


def reverse_patches():
    pyramid_session = sys.modules.get(PYRAMID_SESSION_MODULE)
    pyramid_encode = sys.modules.get("pyramid.encode")

    if pyramid_session:
        patch_manager.reverse_patches_by_owner(pyramid_session)
    if pyramid_encode:
        patch_manager.reverse_patches_by_owner(pyramid_encode)
        urllib_patch.reverse_patches()

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys
from contrast.extern.wrapt import register_post_import_hook

from contrast.agent.policy.applicator import apply_module_patches
from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch

import urllib.parse as urllib

MODULE_NAME = "urllib.parse"


def build_urlencode_patch(orig_func, patch_policy):
    def urlencode_patch(*args, **kwargs):
        """
        Patch for urllib.urlencode / urllib.parse.urlencode.

        This is needed because of the unfortunate way urllib calls on
        `quote_via` as a kwarg.
        See https://github.com/python/cpython/blob/master/Lib/urllib/parse.py#L909

        Because of this behavior, the `quote_via` func is not our patched
        `quote_via` defined in policy.
        By patching `urlencode`, we intercept its call and instead of allowing
        it to use the default kwarg for `quote_via`, we pass our own
        patched `quote_via` in order to prevent false positive XSS findings.
        """
        # quote_plus MUST already be patched by policy in order
        # to pass in the patched func to urlencode
        kwargs.setdefault("quote_via", urllib.quote_plus)
        return orig_func(*args, **kwargs)

    return urlencode_patch


def patch_urllib(urllib_module):
    # We ask policy to go ahead and do all urllib patches here (even though policy
    # patches will happen later on) because we MUST have some urllib policy patches
    # already applied for these non-policy patches to work.
    # This would not be necessary if in _enable_patches policy_patches were applied
    # first.
    apply_module_patches(urllib_module)

    build_and_apply_patch(urllib_module, "urlencode", build_urlencode_patch)


def register_patches():
    register_post_import_hook(patch_urllib, MODULE_NAME)


def reverse_patches():
    urllib_module = sys.modules.get(MODULE_NAME)
    if not urllib_module:  # pragma: no cover
        return

    patch_manager.reverse_patches_by_owner(urllib_module)

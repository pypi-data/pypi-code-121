# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys
from contrast.extern.wrapt import register_post_import_hook

from contrast.agent.policy.applicator import apply_module_patches
from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch

MODULE_NAME = "bottle"


def build_prepare_patch(orig_func, patch_policy):
    def prepare_patch(*args, **kwargs):
        """
        Patch for bottle.SimpleTemplate.prepare.

        This is needed because of the unfortunate way bottle calls on
        `html_escape` as a kwarg in the prepare definition in SimpleTemplate.
        See https://github.com/bottlepy/bottle/blob/master/bottle.py#L3952

        Because of this behavior, the `html_escape` func is not our patched
        `html_escape` defined in policy.
        By patching prepare, we intercept its call and instead of allowing
        it to use the default kwarg for `html_escape`, we pass our own
        patched `html_escape` in order to prevent false positive XSS findings.
        """
        # import here instead of top of module because it ensures bottle module exists.
        import bottle

        # html_escape MUST already be patched by policy in order
        # to pass in the patched func to prepare
        kwargs.setdefault("escape_func", bottle.html_escape)
        return orig_func(*args, **kwargs)

    return prepare_patch


def patch_bottle(bottle_module):
    # We ask policy to go ahead and do all bottle patches here (even though policy
    # patches will happen later on) because we MUST have some bottle policy patches
    # already applied for these non-policy patches to work.
    # This would not be necessary if in _enable_patches policy_patches were applied
    # first.
    apply_module_patches(bottle_module)

    build_and_apply_patch(bottle_module.SimpleTemplate, "prepare", build_prepare_patch)


def register_patches():
    register_post_import_hook(patch_bottle, MODULE_NAME)


def reverse_patches():
    bottle_module = sys.modules.get(MODULE_NAME)
    if not bottle_module:
        return

    patch_manager.reverse_patches_by_owner(bottle_module)
    patch_manager.reverse_patches_by_owner(bottle_module.SimpleTemplate)

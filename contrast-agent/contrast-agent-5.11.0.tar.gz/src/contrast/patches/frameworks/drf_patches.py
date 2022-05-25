# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import register_post_import_hook

from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.settings import Settings
from contrast.utils.patch_utils import add_watermark

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

MODULE_NAME = "rest_framework.response"
PROPERTY_NAME = "rendered_content"


def build_fget(original_fget):
    def fget_patch(*args, **kwargs):
        logger.debug("Hit DRF Response.rendered_content deadzone")
        with scope.contrast_scope():
            return original_fget(*args, **kwargs)

    fget_patch.__name__ = original_fget.__name__
    return add_watermark(fget_patch)


def patch_rest_framework_response(rest_framework_response_module):
    """
    This is a property patch (fget only).
    We can't override fget on the original property object, so we create a new one
    and use the original fset and fdel. If either of these don't exist, they'll
    correctly be set to None on the new property object.
    """
    orig_property = getattr(rest_framework_response_module.Response, PROPERTY_NAME)
    property_with_patch = property(
        fget=build_fget(orig_property.fget),
        fset=orig_property.fset,
        fdel=orig_property.fdel,
    )
    patch_manager.patch(
        rest_framework_response_module.Response, PROPERTY_NAME, property_with_patch
    )


def register_patches():
    """
    This deadzone patch was implemented specifically for a customer, and it's
    off by default.

    Setting agent.python.enable_drf_response_analysis explicitly
    to False will enable this deadzone.
    """
    settings = Settings()
    if settings.config.get("agent.python.enable_drf_response_analysis") is False:
        register_post_import_hook(patch_rest_framework_response, MODULE_NAME)


def reverse_patches():
    rest_framework_response_module = sys.modules.get(MODULE_NAME)
    if not rest_framework_response_module:
        return

    patch_manager.reverse_patches_by_owner(rest_framework_response_module.Response)

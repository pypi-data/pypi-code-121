# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import register_post_import_hook
from contrast.agent import scope
from contrast.agent.assess.policy.source_policy import apply_stream_source
from contrast.agent.policy import patch_manager

from contrast.utils.patch_utils import build_and_apply_patch


FALCON_MULTIPART_MIDDLEWARE_MODULE = "falcon_multipart.middleware"
FALCON_MULTIPART_MIDDLEWARE_CLASS = "MultipartMiddleware"


def build_parse_patch(orig_method, patch_policy):
    def parse_patch(*args, **kwargs):
        """
        Deadzone for falcon_multipart.middleware.MultipartMiddleware.parse

        This method can cause an enormous amount of propagation to occur, which can
        cause requests to be extremely slow. This is because this middleware parses all
        of the multipart form data into memory on the request object. We deadzone this
        propagation in order to greatly improve performance. The parse_field method
        patch below ensures that we still track the relevant data.

        This method gets called before MultipartMiddleware.parse_field in
        MultipartMiddleware.process_request.
        """
        with scope.contrast_scope():
            return orig_method(*args, **kwargs)

    return parse_patch


def build_parse_field_patch(orig_method, patch_policy):
    def parse_field_patch(self, field, **kwargs):
        """
        Deadzone and source tracker for falcon_multipart.middleware.MultipartMiddleware

        First we deadzone the call to the original method in order to prevent
        unnecessary propagation and improve performance. Next, we create sources for
        the result so that we don't miss any input data.

        This method gets called after MultipartMiddleware.parse in
        MultipartMiddleware.process_request.
        """
        with scope.contrast_scope():
            result = orig_method(self, field)

        apply_stream_source("parse_field", result, self, result, (field,), kwargs)

        return result

    return parse_field_patch


def patch_falcon_multipart(module):
    middleware_cls = getattr(module, FALCON_MULTIPART_MIDDLEWARE_CLASS, None)
    if middleware_cls is None:
        return

    build_and_apply_patch(middleware_cls, "parse", build_parse_patch)
    build_and_apply_patch(middleware_cls, "parse_field", build_parse_field_patch)


def register_patches():
    register_post_import_hook(
        patch_falcon_multipart, FALCON_MULTIPART_MIDDLEWARE_MODULE
    )


def reverse_patches():
    module = sys.modules.get(FALCON_MULTIPART_MIDDLEWARE_MODULE)
    if module is None:  # pragma: no cover
        return

    middleware_cls = getattr(module, FALCON_MULTIPART_MIDDLEWARE_CLASS)
    if middleware_cls is None:  # pragma: no cover
        return

    patch_manager.reverse_patches_by_owner(middleware_cls)

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

import contrast

from contrast.extern.wrapt import register_post_import_hook
from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.assess.utils import copy_from, track_string

from contrast.utils.patch_utils import build_and_apply_patch
from contrast.utils.assess.stream_utils import ContrastFileProxy

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

SAFESTRING_MODULE_NAME = "django.utils.safestring"
UPLOADHANDLER_MODULE_NAME = "django.core.files.uploadhandler"
MARK_SAFE_NAME = "mark_safe"


def _get_source(args, kwargs):
    if args:
        return args[0]
    if kwargs:
        return kwargs.get("s")
    return None


def build_mark_safe_patch(orig_func, patch_policy):
    def mark_safe_patch(*args, **kwargs):
        """
        This patch implements a more optimized "deadzoned" original mark_safe call.

        We are deadzoning calling the original mark_safe because it may call SafeText,
        a class that inherits from str and that ends up propagating excessively.

        Because mark_safe is called many times when Django renders a template,
        excessive propagation is incredibly costly. So instead, we do the same work as
        the KEEP propagator would, but with a deadzoned call to the original function.
        """
        # if we're already in scope, don't bother doing any analysis
        if scope.in_scope():
            return orig_func(*args, **kwargs)

        # if we're not yet in scope, call orig_func and analysis in scope
        with scope.contrast_scope():
            # We don't wrap orig_func call in try/catch because if it raises an error
            # we don't want to do any analysis.
            result = orig_func(*args, **kwargs)

            if contrast.CS__CONTEXT_TRACKER.current() is not None:
                try:
                    logger.debug("Analyzing in %s custom propagator.", MARK_SAFE_NAME)
                    source = _get_source(args, kwargs)
                    track_string(result)
                    copy_from(result, source)
                except Exception as e:
                    logger.debug(
                        "Failed to analyse in %s propagator. %s", MARK_SAFE_NAME, str(e)
                    )

        return result

    return mark_safe_patch


def build_new_file_patch(orig_func, patch_policy):
    def new_file_patch(*args, **kwargs):
        """
        Patch for TemporaryFileUploadHandler.new_file

        Uploaded files that exceed the FILE_UPLOAD_MAX_MEMORY_SIZE threshold are
        streamed from a temporary file on disk rather than loaded into memory.

        This patch enables us to track the contents of uploaded files that exceed this
        threshold.

        - args[0] is self, which is an instance of TemporaryFileUploadHandler
        - args[0].file is a TemporaryUploadedFile, which is the stream we want to proxy
        """
        result = orig_func(*args, **kwargs)

        if args and hasattr(args[0], "file"):
            try:
                # This also marks the stream as a source While ContrastFileProxy was
                # originally intended for file objects in Py27, it also meets our needs
                # for proxying the TemporaryUploadedFile stream.  Eventually we may
                # decide to use a different proxy class, or at least a different name
                # (or change the docstring in ContrastFileProxy).
                args[0].file = ContrastFileProxy(args[0].file)
            except Exception as e:
                logger.debug(
                    "Failed to track large uploaded file as source stream: %s", str(e)
                )

        return result

    return new_file_patch


def patch_django_safestring(safestring_module):
    build_and_apply_patch(safestring_module, MARK_SAFE_NAME, build_mark_safe_patch)


def patch_django_uploadhandler(uploadhandler_module):
    build_and_apply_patch(
        uploadhandler_module.TemporaryFileUploadHandler,
        "new_file",
        build_new_file_patch,
    )


def register_patches():
    register_post_import_hook(patch_django_safestring, SAFESTRING_MODULE_NAME)
    register_post_import_hook(patch_django_uploadhandler, UPLOADHANDLER_MODULE_NAME)


def reverse_patches():
    safestring_module = sys.modules.get(SAFESTRING_MODULE_NAME)
    if safestring_module:
        patch_manager.reverse_patches_by_owner(safestring_module)

    uploadhandler_module = sys.modules.get(UPLOADHANDLER_MODULE_NAME)
    if uploadhandler_module:
        patch_manager.reverse_patches_by_owner(
            uploadhandler_module.TemporaryFileUploadHandler
        )

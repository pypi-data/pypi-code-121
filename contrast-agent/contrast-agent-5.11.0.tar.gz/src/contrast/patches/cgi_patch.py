# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

"""
FieldStorage objects and their MiniFieldStorage cousins are data containers for form
and multipart request bodies. The constructor for FieldStorage also parses the raw
request body. We deadzone this constructor but also explicitly track attributes on
the newly created object.

FieldStorage objects can hold one of two things:
    1. a list ("value" or "list") of other FieldStorage / MiniFieldStorage objects;
       even simple form data will have at least one top level FieldStorage with a
       list containing MiniFieldStorage objects for each form param
    2. a field, which has a fieldname ("name"), filename, and a file-like object
       ("file") containing the actual field data. Accessing "value" reads and resets
       the file in this case

MiniFieldStorage objects only hold a parameter name and value. They are used for
storing form data that isn't multipart.

getitem and direct attribute reference is the lower-level API for FieldStorage, but
methods like getvalue(), getfirst(), and getlist() also exist. Since we track the
underlying data directly, we don't need to worry about patches for the higher-level
API; however, we still test it.

The cpython source code for FieldStorage and MiniFieldStorage is written in Python
and the API is not terribly complicated. See the source code (cgi.py) for details.
"""

import sys

import contrast
from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.assess.policy.source_policy import cs__apply_source
from contrast.extern.wrapt import register_post_import_hook
from contrast.utils.assess import stream_utils
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


@fail_quietly("failed to track cgi.FieldStorage object")
def _track_fieldstorage(fs_obj, context, node):
    """
    Explicitly mark all relevant FieldStorage attributes as sources.

    :param fs_obj: FieldStorage object, the instance of cgi.FieldStorage to track
    :param context: RequestContext
    :param node: Source node for cgi.FieldStorage.__init__
    """
    for attr_name in ["name", "filename"]:
        _mark_source(fs_obj, attr_name, context, node)

    if (
        hasattr(fs_obj, "file")
        and fs_obj.file is not None
        and not isinstance(fs_obj.file, stream_utils.BaseStreamProxy)
    ):
        if hasattr(fs_obj.file, "cs__source"):
            fs_obj.file.cs__source = True
        else:
            fs_obj.file = stream_utils.ContrastBufferedReaderProxy(fs_obj.file)
        fs_obj.file.cs__source_type = node.type
        fs_obj.file.cs__source_tags = node.tags


@fail_quietly("failed to track cgi.MiniFieldStorage object")
def _track_minifieldstorage(fs_obj, context, node):
    """
    Same as _track_fieldstorage, but for MiniFieldStorage. This class only stores a
    name and value, both strings.
    """
    for attr_name in ["name", "value"]:
        _mark_source(fs_obj, attr_name, context, node)


def _mark_source(fs_obj, attr_name, context, node):
    attr = getattr(fs_obj, attr_name, None)
    if not attr:
        return
    cs__apply_source(
        context,
        node,
        attr,
        fs_obj,
        attr,
        (),
        {},
        # it's not totally clear what type filename / fieldname should be, so we're
        # sticking with PARAMETER
        source_type="PARAMETER",
        source_name=attr_name,
    )


def _build_patch(original_func, patch_policy, tracker_func):
    """
    Builds the patch for cgi.FieldStorage.__init__ and cgi.MiniFieldStorage.__init__.
    The appropriate tracking function is passed in as tracker_func.
    """
    node = patch_policy.source_nodes[0]

    def init_wrapper(fieldstorage_object, *args, **kwargs):
        # this is a deadzone; we explicitly track the resulting (Mini)FieldStorage
        # object after the fact
        with scope.contrast_scope():
            result = original_func(fieldstorage_object, *args, **kwargs)

        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None:
            return result

        tracker_func(fieldstorage_object, context, node)
        return result

    return init_wrapper


def build_cgi_fieldstorage_patch(original_func, patch_policy):
    return _build_patch(original_func, patch_policy, _track_fieldstorage)


def build_cgi_minifieldstorage_patch(original_func, patch_policy):
    return _build_patch(original_func, patch_policy, _track_minifieldstorage)


def patch_cgi(cgi_module):
    build_and_apply_patch(
        cgi_module.FieldStorage, "__init__", build_cgi_fieldstorage_patch
    )
    build_and_apply_patch(
        cgi_module.MiniFieldStorage, "__init__", build_cgi_minifieldstorage_patch
    )


def register_patches():
    register_post_import_hook(patch_cgi, "cgi")


def reverse_patches():
    cgi_module = sys.modules.get("cgi")
    if not cgi_module:
        return

    patch_manager.reverse_patches_by_owner(cgi_module.FieldStorage)
    patch_manager.reverse_patches_by_owner(cgi_module.MiniFieldStorage)

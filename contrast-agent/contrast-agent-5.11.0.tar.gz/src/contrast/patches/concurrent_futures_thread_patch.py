# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

import contrast
from contrast.assess_extensions import cs_str

from contrast.extern.wrapt import register_post_import_hook
from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch

MODULE_TO_PATCH = "concurrent.futures.thread"
CLASS_TO_PATCH = "_WorkItem"


def build__init__patch(orig_method, patch_policy):
    """
    This patch is executed when a new _WorkItem object is created. After this happens it is put on a thread safe queue.
    Worker threads in the ThreadPoolExecutor class deque and execute the call back function contained in this object.
    We attach our request context on object creation since the thread this function is running on is the same
    thread that initially served the request.
    """

    def work_item__init__patch(__cs_self, *args, **kwargs):
        ret = orig_method(__cs_self, *args, **kwargs)

        # Save the scope of the current thread to copy to the thread running the route function
        __cs_self.cs__parent_scope = cs_str.get_current_scope()
        __cs_self.cs__parent_context = contrast.CS__CONTEXT_TRACKER.current()

        return ret

    return work_item__init__patch


def build_run_patch(orig_method, patch_policy):
    """
    This patch is executed in the worker thread. We need to reapply the context saved in _WorkItem.__init__
    """

    def work_item_run_patch(__cs_self, *args, **kwargs):
        with contrast.CS__CONTEXT_TRACKER.lifespan(__cs_self.cs__parent_context):
            cs_str.set_exact_scope(__cs_self.cs__parent_scope)

            return orig_method(__cs_self, *args, **kwargs)

    return work_item_run_patch


def patch_concurrent_futurs_thread(module):
    cls = getattr(module, CLASS_TO_PATCH, None)
    if cls is None:
        return

    build_and_apply_patch(cls, "__init__", build__init__patch)
    build_and_apply_patch(cls, "run", build_run_patch)


def register_patches():
    register_post_import_hook(patch_concurrent_futurs_thread, MODULE_TO_PATCH)


def reverse_patches():
    module = sys.modules.get(MODULE_TO_PATCH)
    if module is None:  # pragma: no cover
        return

    cls = getattr(module, CLASS_TO_PATCH)
    if cls is None:  # pragma: no cover
        return

    patch_manager.reverse_patches_by_owner(cls)

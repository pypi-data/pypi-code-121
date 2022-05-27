# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import register_post_import_hook
from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch


def build_noop_patch(*_):
    def noop_intern(string):
        """
        Defeat interning by returning the original string

        sys.intern takes no kwargs
        """
        return string

    return noop_intern


def patch_sys(module):
    build_and_apply_patch(module, "intern", build_noop_patch)


def register_patches():
    register_post_import_hook(patch_sys, "sys")


def reverse_patches():
    # sys is always imported, no need to check
    patch_manager.reverse_patches_by_owner(sys)

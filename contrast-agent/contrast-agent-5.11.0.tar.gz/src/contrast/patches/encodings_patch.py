# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import register_post_import_hook

from contrast.agent.assess.policy.patches import build_assess_method_legacy
from contrast.agent.policy import patch_manager
from contrast.agent.policy.loader import Policy


CODEC_MODULES_TO_PATCH = [
    "encodings.ascii",
    "encodings.latin_1",
    "encodings.raw_unicode_escape",
    "encodings.unicode_escape",
    "encodings.unicode_internal",
]


def build_codec_patch(module, method_name):
    module_name = module.__name__

    orig_method = getattr(module.Codec, method_name)
    patch_policy = Policy().policy_by_name.get(f"{module_name}.Codec.{method_name}")

    assess_method = build_assess_method_legacy(orig_method, patch_policy)

    def codec_patch(*args, **kwargs):
        return assess_method(*args, **kwargs)

    return codec_patch


def patch_codec_module(module):
    patch_manager.patch(module.Codec, "encode", build_codec_patch(module, "encode"))
    patch_manager.patch(module.Codec, "decode", build_codec_patch(module, "decode"))

    import encodings

    # Clear the encodings cache so that our patches are seen
    encodings._cache.clear()


def register_patches():
    for module in CODEC_MODULES_TO_PATCH:
        register_post_import_hook(patch_codec_module, module)


def reverse_patches():
    for name in CODEC_MODULES_TO_PATCH:
        module = sys.modules.get(name)
        if module is not None:
            patch_manager.reverse_patches_by_owner(module.Codec)

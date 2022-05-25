# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

from contrast.agent import scope, rewriter
from contrast.agent.assess.policy import string_propagation
from contrast.agent.policy.applicator import register_import_hooks
from contrast.agent.policy.loader import Policy
from contrast.agent.settings import Settings
from contrast.assess_extensions import cs_str
from contrast.patches import (
    cs_str as cs_str_patches,
    register_assess_patches,
    register_common_patches,
    register_library_patches,
)
from contrast.utils.namespace import Namespace
from contrast.utils.patch_utils import repatch_imported_modules


ALWAYS_PURE_PYTHON_METHODS = ["format"]


class module(Namespace):
    hook = None
    enabled = False


hook_module_map = {
    str: cs_str.create_unicode_hook_module(),
    bytes: cs_str.create_bytes_hook_module(),
    bytearray: cs_str.create_bytearray_hook_module(),
}


def apply_extension_hook(funchook, strtype, hook_module, method_name):
    """
    Apply extension hook for a particular string method

    Returns False if the hook failed to apply and True otherwise
    """
    hook_name = f"apply_{method_name}_hook"
    hook_method = getattr(hook_module, hook_name)

    try:
        hook_method(funchook)
    except RuntimeError as e:
        logger.debug(
            "Failed to apply C extension hook for %s.%s. Will retry in pure python. %s",
            strtype.__name__,
            method_name,
            e,
        )
        return False

    return True


def enable_method_hooks(funchook, hook_module_map, use_extension_hooks=True):
    """
    Enable string propagation hooks for individual string type methods

    This method uses policy to determine all of the string methods that need to be
    patched. For each string type, it first attempts to apply the patch using C
    extension hooks (if not explicitly disallowed by `use_extension_hooks`). If that
    fails for any reason, it will then fall back to applying a pure Python patch.
    """
    for strtype, hook_module in hook_module_map.items():
        for node in Policy().string_method_nodes:
            method_name = node.method_name

            if method_name.lower() in ["__repr__", "cast", "concat"]:
                # these are applied directly in the C extension only
                continue

            real_method_name = (
                "format_map" if method_name == "formatmap" else method_name
            )

            if not hasattr(strtype, real_method_name):
                continue

            if method_name not in ALWAYS_PURE_PYTHON_METHODS and use_extension_hooks:
                if apply_extension_hook(funchook, strtype, hook_module, method_name):
                    logger.debug(
                        "Applied C extension hook for %s.%s",
                        strtype.__name__,
                        method_name,
                    )
                    continue

            cs_str_patches.patch_strtype_method(strtype, real_method_name)
            logger.debug(
                "Applied pure Python patch for %s.%s", strtype.__name__, method_name
            )


def enable_assess_patches(use_extension_hooks=True):
    """
    Enables extension hooks and other string patches.

    Has no effect if these patches are already enabled.
    """
    if module.enabled:
        return

    # NOTE: This function *must* be called before the extension is initialized
    # string_propagation.build_string_propagator_functions()
    string_propagation.build_string_propagator_functions()

    try:
        module.hook = cs_str.initialize(logger)
        cs_str.enable_required_hooks(module.hook)
    except RuntimeError:
        logger.error(
            "Local python builds on OSX may lead to 'Failed to unprotect memory'"
        )
        logger.error(
            "If this applies to you, try running `contrast-fix-interpreter-permissions`"
        )
        raise

    use_extension_hooks = use_extension_hooks and not Settings().config.get(
        "agent.python.assess.use_pure_python_hooks"
    )

    cs_str_patches.enable_str_properties()
    enable_method_hooks(
        module.hook, hook_module_map, use_extension_hooks=use_extension_hooks
    )

    try:
        cs_str.install(module.hook)
    except RuntimeError:
        logger.error(
            "Local python builds on OSX may lead to 'Failed to unprotect memory'"
        )
        logger.error(
            "If this applies to you, try running `contrast-fix-interpreter-permissions`"
        )
        raise

    module.enabled = True


def disable_assess_patches():
    """
    Disables extension hooks and other string patches.

    Has no effect if these patches are not already enabled.
    """
    if not module.enabled:
        return

    cs_str.disable(module.hook)

    # Disable any string patches that were applied through Python
    cs_str_patches.unpatch_strtype_methods()

    module.enabled = False


def _enable_patches():
    settings = Settings()

    if settings.is_analyze_libs_enabled():
        register_library_patches()

    if settings.is_protect_enabled():
        register_common_patches()

        logger.debug("adding protect policy")
        register_import_hooks(protect_mode=True)

        # This has no effect if the patches are not enabled
        disable_assess_patches()

    if settings.is_assess_enabled():
        enable_assess_patches()

        logger.debug("enabled assess string patches")
        register_common_patches()
        register_assess_patches()

        logger.debug("adding assess policy")
        register_import_hooks()

        rewriter.register()

    logger.debug("revisiting imported modules to apply patches")
    repatch_imported_modules()


def enable_patches():
    """
    Enable all patches for agent based on current settings
    """
    # Being in scope here prevents us from inadvertently propagating while we are
    # applying patches and navigating policy. This has a fairly significant performance
    # impact for assess initialization, and also promotes correctness/safety.
    with scope.contrast_scope():
        _enable_patches()

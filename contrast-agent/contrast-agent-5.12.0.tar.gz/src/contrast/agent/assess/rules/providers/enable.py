# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy.loader import Policy
from contrast.utils.patch_utils import get_loaded_modules


def enable_providers():
    """
    Providers are non-dataflow rules that analyze the contents of a module.
    """
    for _, module in get_loaded_modules(use_for_patching=True).items():
        for provider in Policy().providers.values():
            if provider.applies_to(module):
                provider.analyze(module)

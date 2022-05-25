# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from .cs_str import set_attr_on_type


def smart_setattr(owner, name, patch):
    """
    Use either setattr or set_attr_on_type as appropriate
    """
    # For some reason, set_attr_on_type doesn't work for special methods
    # We may eventually need to refine this logic
    force_patch = isinstance(owner, type) and not (
        name.startswith("__") and name.endswith("__")
    )

    setattr(owner, name, patch) if not force_patch else set_attr_on_type(
        owner, name, patch
    )

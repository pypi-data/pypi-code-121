# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from contrast.agent.assess.utils import copy_from
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.utils.string_utils import ensure_string


class ReprPropagator(BasePropagator):
    """
    Propagation method for __repr__ method of stringy types

    If the string itself is faithfully represented in the the repr, then we simply copy
    the tags to the correct offset to account for boilerplate. Otherwise, we just splat
    across the result.
    """

    def _propagate(self):
        # Get a stringy version of the source
        if isinstance(self.first_source, bytearray):
            string = ensure_string(bytes(self.first_source), errors="ignore")
        else:
            string = ensure_string(self.first_source, errors="ignore")

        # See whether the stringy version is inside the repr
        offset = self.target.find(string)
        # Handle edge case where the string itself is "bytearray" or something like that
        if offset == 0:
            offset = self.target.rfind(string)

        if offset >= 0:
            copy_from(self.target, self.first_source, offset, self.node.untags)
            return

        # If it's not, then just splat to account for encoding, etc.
        self.splat_tags(self.first_source, self.target)

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.agent.assess.utils import copy_from


class KeepPropagator(BasePropagator):
    def _propagate(self):
        self.first_source = self.sources[0]
        copy_from(self.target, self.first_source, 0, self.node.untags)

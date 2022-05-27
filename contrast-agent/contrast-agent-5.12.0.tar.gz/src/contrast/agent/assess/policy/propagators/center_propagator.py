# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from __future__ import division
import math

from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.agent.assess.utils import copy_from


class CenterPropagator(BasePropagator):
    def _propagate(self):
        start_index = math.ceil((len(self.target) - len(self.first_source)) / 2)
        copy_from(self.target, self.first_source, start_index, self.node.untags)

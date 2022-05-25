# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.agent.assess.utils import copy_from


class ReductivePropagator(BasePropagator):
    def _propagate(self):
        copy_from(self.target, self.first_source, 0, self.node.untags)

        source_index = 0
        target_index = 0

        remove_ranges = []
        current_range = None

        # loop over the target, the result of the delete
        # every range of characters that it differs from the source
        # represents a section that was deleted. these sections
        # need to have their tags updated
        while target_index < len(self.target) and source_index < len(self.first_source):
            target_char = self.target[target_index]
            source_char = self.first_source[source_index]

            if target_char == source_char:
                target_index += 1

                if current_range:
                    current_range.stop = source_index

                    remove_ranges.append(current_range)
                    current_range = None
            elif current_range is None:
                current_range = AdjustedSpan(target_index, len(self.first_source))

            source_index += 1

        if source_index != len(self.first_source):
            remove_ranges.append(AdjustedSpan(target_index, len(self.first_source)))

        self.target_properties.delete_tags_at_ranges(remove_ranges)

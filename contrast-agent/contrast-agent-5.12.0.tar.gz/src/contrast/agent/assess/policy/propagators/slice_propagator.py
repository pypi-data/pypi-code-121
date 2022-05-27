# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.propagators import BasePropagator
from contrast.agent.assess.utils import copy_events, get_properties
from contrast.utils.assess.tag_utils import merge_tags


class SlicePropagator(BasePropagator):
    def _propagate(self):
        slice_ = self.preshift.args[0] if self.preshift.args else None

        # Offset in the target string
        target_offset = 0

        source_properties = get_properties(self.preshift.obj)

        # This is like the coolest thing ever. I found it here:
        # https://stackoverflow.com/a/42883770/4312739
        # It converts a slice to a range of indices
        offsets = list(range(self.preshift.obj_length)[slice_])

        for source_offset in offsets:
            span = AdjustedSpan(source_offset, source_offset + 1)
            source_tags = source_properties.tags_at_range(span)
            for name in source_tags:
                end_offset = target_offset + 1
                new_span = AdjustedSpan(target_offset, end_offset)
                self.target_properties.add_tag(name, new_span)

            target_offset += 1

        copy_events(self.target_properties, source_properties)
        merge_tags(self.target_properties.tags)

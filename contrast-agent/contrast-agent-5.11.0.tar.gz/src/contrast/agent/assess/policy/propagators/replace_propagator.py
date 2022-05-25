# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.agent.assess.utils import (
    copy_events,
    copy_tags_to_offset,
    get_properties,
)


class ReplacePropagator(BasePropagator):
    def _copy_span_tags_to_offset(self, orig_properties, start_idx, end_idx, offset):
        old_span = AdjustedSpan(start_idx, end_idx)
        source_tags = orig_properties.tags_at_range(old_span)
        copy_tags_to_offset(self.target_properties, source_tags, offset)

    def _propagate_tags(
        self, orig_properties, new_properties, orig_str, old_str, new_str
    ):
        source_offset = 0
        target_offset = 0

        count = orig_str.count(old_str)
        # Account for count parameter (ha!)
        if len(self.preshift.args) > 2:
            count = min(count, self.preshift.args[2])

        while count > 0:
            found_idx = orig_str.find(old_str, source_offset)
            # copy old tags to the new location
            if source_offset != found_idx and orig_properties is not None:
                self._copy_span_tags_to_offset(
                    orig_properties,
                    source_offset,
                    found_idx,
                    target_offset,
                )

            target_offset += found_idx - source_offset
            source_offset = found_idx + len(old_str)

            # copy any tags from the new string
            if new_properties is not None:
                copy_tags_to_offset(
                    self.target_properties, new_properties.tags, target_offset
                )

            target_offset += len(new_str)
            count -= 1

        if source_offset < len(orig_str) and orig_properties is not None:
            self._copy_span_tags_to_offset(
                orig_properties,
                source_offset,
                len(orig_str),
                target_offset,
            )

    def _propagate(self):
        orig_str = self.preshift.obj
        old_str, new_str = self.preshift.args[:2]

        orig_properties = get_properties(orig_str)
        new_properties = get_properties(new_str)

        if orig_properties is None and new_properties is None:
            return

        self._propagate_tags(
            orig_properties, new_properties, orig_str, old_str, new_str
        )

        copy_events(self.target_properties, orig_properties)
        copy_events(self.target_properties, new_properties)

        self.target_properties.cleanup_tags()

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators import BasePropagator
from contrast.agent.assess.utils import (
    copy_events,
    copy_tags_in_span,
    get_properties,
)
from contrast.utils.assess import tracking_util


class SplitPropagator(BasePropagator):

    PARTITION_METHODS = ["partition", "rpartition"]
    REVERSE_METHODS = ["rsplit", "rpartition"]

    def track_target(self):
        # NOP. Let propagate handle the decision to track
        pass

    @property
    def needs_propagation(self):
        if not self.preshift:
            return False

        return tracking_util.recursive_is_tracked(self.preshift.obj)

    def build_event(self, target_properties, tagged):
        parent_ids = self.get_parent_ids(tagged)
        # For split, the tagged individual string is passed when building the
        # event, but the target is actually the array of strings that was
        # returned by split.
        target_properties.build_event(
            self.node,
            tagged,
            self.preshift.obj,
            self.target,
            self.preshift.args,
            self.preshift.kwargs,
            parent_ids,
            None,
        )

    def add_tags_and_properties(self, ret):
        for target in self.target:
            if self.node.tags:
                self.apply_tags(self.node, target)

            if self.node.untags:
                self.apply_untags(self.node, target)

            target_properties = get_properties(target)
            if target_properties is None:
                continue

            target_properties.add_properties(self.node.properties)

            self.build_event(target_properties, target)

    def propagate(self):

        reverse = self.node.method_name in self.REVERSE_METHODS

        if self.node.method_name in self.PARTITION_METHODS:
            partition = self.preshift.args[0]
        else:
            partition = None

        source = self.preshift.obj
        source_properties = get_properties(source)

        # Offset in the original string
        source_offset = 0

        # The target (result of split) is an array of strings
        target = self.target[::-1] if reverse else self.target

        for newstr in target:
            if reverse:
                source_offset = source.rfind(newstr)
                source = source[:source_offset]
            else:
                source_offset = source.find(newstr, source_offset)

            if partition and newstr == partition:
                # Make sure that we don't skip another string that just happens
                # to be the same as the partition string.
                partition = None
                continue

            span = (source_offset, source_offset + len(newstr))
            copy_tags_in_span(newstr, source_properties, span)

            target_properties = get_properties(newstr)
            if target_properties is not None:
                copy_events(target_properties, source_properties)

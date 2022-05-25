# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators import SUPPORTED_TYPES, BasePropagator
from contrast.utils.assess.tag_utils import merge_tags
from contrast.agent.assess.utils import (
    copy_events,
    get_last_event_ids_from_sources,
    get_properties,
    is_tracked,
)
from contrast.utils.decorators import cached_property


class JoinPropagator(BasePropagator):
    def _add_tags(self, target_props, source_props, offset):
        for label, tags in source_props.tags.items():
            for tag in tags:
                new_tag = tag.copy_modified(offset)
                target_props.add_existing_tag(label, new_tag)

    def __init__(self, node, preshift, target):
        super().__init__(node, preshift, target)
        self.strings_to_join = self.preshift.args[0] if self.preshift.args else []
        self.separator = self.preshift.obj

    def get_parent_ids(self, *args):
        return get_last_event_ids_from_sources(self.sources)

    @cached_property
    def sources(self):
        return [self.preshift.obj] + self.preshift.args[0]

    @property
    def needs_propagation(self):
        """
        This is a fairly hot code path in some applications; be mindful of performance
        """
        if not isinstance(self.target, SUPPORTED_TYPES):
            return False

        # No need to propagate since the join had no effect
        if len(self.strings_to_join) == 0:
            return False

        if is_tracked(self.target):
            return True

        if not self.preshift:
            return False

        for s in self.sources:
            if is_tracked(s):
                return True

        return False

    def _propagate(self):

        # Offset in the target string
        target_offset = 0

        base_properties = get_properties(self.preshift.obj)

        for i, item in enumerate(self.strings_to_join):
            item_properties = get_properties(item)
            if item_properties is not None:
                self._add_tags(self.target_properties, item_properties, target_offset)
                copy_events(self.target_properties, item_properties)

            target_offset += len(item)

            if i < len(self.strings_to_join) - 1 and base_properties is not None:
                self._add_tags(self.target_properties, base_properties, target_offset)

            target_offset += len(self.separator)

        if base_properties is not None:
            copy_events(self.target_properties, base_properties)

        merge_tags(self.target_properties.tags)

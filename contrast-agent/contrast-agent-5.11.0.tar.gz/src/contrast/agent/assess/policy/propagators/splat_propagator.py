# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators.base_propagator import (
    BasePropagator,
    SUPPORTED_TYPES,
)
from contrast.agent.assess.utils import (
    copy_from,
    is_tracked,
    get_properties,
    track_string,
)
from contrast.utils.assess.duck_utils import is_iterable, safe_iterator
from contrast.utils.decorators import fail_quietly

from contrast.utils.string_utils import ensure_binary


class SplatPropagator(BasePropagator):
    """
    Takes all tags from source string and applies each to entire length of the target
    """

    @fail_quietly("Splat propagation failed")
    def track_and_propagate(self, ret):
        """
        For splat, we'll track the target ourselves but ensure node tags and untags are applied
        """
        self.track_target()
        self.propagate()
        self.add_tags_and_properties(ret)
        self.reset_tags()

    def track_target(self):
        target_properties = get_properties(self.target)

        if not target_properties:
            target_properties = track_string(self.target)

        self.target_properties = target_properties

    def _propagate(self):
        if self._should_copy:
            track_string(self.sources[0])
            copy_from(self.target, self.sources[0], 0, self.node.untags)
            self.target_properties.cleanup_tags()
            return

        if not self.target or not isinstance(self.target, SUPPORTED_TYPES):
            return

        tracked_inputs = self._get_tracked_inputs()
        self._apply_splat_tags(tracked_inputs)

    @property
    def _should_copy(self):
        """
        Determine whether SPLAT operation should really be a copy (KEEP) instead

        If we can determine that the values of the source and target are the same, even
        if they are not the same type, then we should attempt to copy instead.  This
        will help improve accuracy. Specifically, it should help prevent some false
        negatives where a safe encoded tag may get splatted across an unsafe range as
        the result of an encode operation or some such.
        """
        if len(self.sources) != 1:
            return False

        try:
            if len(self.sources[0]) != len(self.target):
                return False

            return ensure_binary(self.sources[0]) == ensure_binary(self.target)
        except Exception:
            return False

    def _get_tracked_inputs(self):
        tracked_inputs = []

        def _append_if_tracked(val):
            if is_tracked(val):
                tracked_inputs.append(val)

        for source in self.sources:
            if isinstance(source, SUPPORTED_TYPES):
                _append_if_tracked(source)
            elif isinstance(source, dict):
                for key, value in source.items():
                    _append_if_tracked(key)
                    _append_if_tracked(value)
            elif is_iterable(source):
                for item in safe_iterator(source):
                    _append_if_tracked(item)

        return tracked_inputs

    def _apply_splat_tags(self, tracked_inputs):
        for item in tracked_inputs:
            if item is not self.target:
                item_properties = get_properties(item)

                if not item_properties:
                    continue

                for event in item_properties.events:
                    self.target_properties.events.append(event)

                self.splat_tags(item, self.target)

        self.target_properties.cleanup_tags()

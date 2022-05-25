# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.source_policy import get_parent_ids
from contrast.agent.assess.tag import Tag
from contrast.utils.assess import tracking_util
from contrast.utils.assess.tag_utils import combine, is_covered
from contrast.utils.decorators import cached_property, fail_quietly
from contrast.agent.assess.utils import (
    is_tracked,
    get_properties,
    track_string,
)

SUPPORTED_TYPES = (
    str,
    bytes,
    bytearray,
)


class BasePropagator(object):
    def __init__(self, node, preshift, target):
        """
        :param node: instance of PropagationNode
        """
        self.node = node
        self.preshift = preshift
        self.target = target
        self.target_properties = None

    @cached_property
    def sources(self):
        """
        Get all the sources for the propagation node.
        """
        return self.node.get_matching_sources(self.preshift)

    @property
    def any_source_tracked(self):
        return any(tracking_util.recursive_is_tracked(s) for s in self.sources)

    @property
    def needs_propagation(self):
        if not isinstance(self.target, SUPPORTED_TYPES):
            return False

        if tracking_util.recursive_is_tracked(self.target):
            return True

        if not self.preshift:
            return False

        return self.inputs_require_propagation

    @property
    def inputs_require_propagation(self):
        return self.any_source_tracked

    def track_target(self):
        for source in self.sources:
            if is_tracked(source):
                track_string(self.target)

    def propagate(self):
        """
        Any propagators that inherit from BasePropagator and are able to follow
        this same propagation pattern should define _propagate.

        Some propagators continue to define their own propagate method.
        """
        self.target_properties = get_properties(self.target)
        if self.target_properties is None:
            return

        self.first_source = self.sources[0]
        self._propagate()
        self.target_properties.cleanup_tags()

    def get_parent_ids(self, ret):
        """Some derived classes may need to override this method"""
        return get_parent_ids(
            self.node, self.preshift.obj, ret, self.preshift.args, self.preshift.kwargs
        )

    def build_event(self, target_properties, ret):
        parent_ids = self.get_parent_ids(ret)
        target_properties.build_event(
            self.node,
            self.target,
            self.preshift.obj,
            ret,
            self.preshift.args,
            self.preshift.kwargs,
            parent_ids,
            None,
        )

    def splat_tags(self, source, ret):
        """
        SPLAT copies tags for cases where the string transformation is unknown

        SPLAT is subject to the following rules:
            1. Any UNTRUSTED tags on the input are applied to the entire length of the
               output.
            2. Any other tags that cover the entire length of the input are copied to
               the entire length of the output.
            3. Any tags that cover all UNTRUSTED ranges on the input are copied to the
               entire length of the output.
            4. No other tags are copied.

        These rules are intended to minimize the number of false negatives that result
        from accidentally copying safe tags from the input to regions of the output
        that are not actually safe.
        """
        source_props = get_properties(source)
        if source_props is None:
            return

        ret_props = get_properties(ret)
        if ret_props is None:
            return

        ret_length = len(ret)

        untrusted_ranges = source_props.tags.get("UNTRUSTED") or []
        if untrusted_ranges:
            # splat UNTRUSTED ranges across the entire output
            ret_props.add_tag("UNTRUSTED", AdjustedSpan(0, ret_length))

        for name, ranges in source_props.tags.items():
            if name == "UNTRUSTED":
                continue

            if untrusted_ranges and is_covered(untrusted_ranges, ranges):
                ret_props.add_tag(name, AdjustedSpan(0, ret_length))

            combined = combine(ranges)
            if combined[0] == Tag(len(source), 0):
                ret_props.add_tag(name, AdjustedSpan(0, ret_length))

    def apply_tags(self, node, target, span=None):
        target_properties = get_properties(target)
        if not target_properties:
            return

        span = span or AdjustedSpan(0, len(target))
        for tag in node.tags:
            target_properties.add_tag(tag, span)

    def apply_untags(self, node, target):
        target_properties = get_properties(target)

        if target_properties:
            for tag in node.untags:
                target_properties.delete_tag(tag)

    def add_tags(self):
        if self.node.tags:
            self.apply_tags(self.node, self.target)

        if self.node.untags:
            self.apply_untags(self.node, self.target)

    def add_tags_and_properties(self, ret):
        self.add_tags()

        target_properties = get_properties(self.target)

        # ignore un-tracked targets; possible interning
        if target_properties is None:
            return

        target_properties.add_properties(self.node.properties)

        self.build_event(target_properties, ret)

    def reset_tags(self):
        """
        Some propagators will store the original set of tags but then restore them.
        This is because PropagationNode are only initialized once (for the entire server-startup cycle)
        from their policy.json representation, so if a propagator has to add/delete a tag, we need
        to restore the original tags.

        In the future, we could avoid doing this reset by re-instantiating nodes
        every time, albeit with a cost to performance.
        """
        pass

    @fail_quietly("Error during propagation")
    def track_and_propagate(self, ret):
        self.track_target()
        self.propagate()
        self.add_tags_and_properties(ret)

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from copy import copy
import time

import contrast
from contrast.agent.assess.contrast_event import ContrastEvent
from contrast.agent.assess.tag import (
    ABOVE,
    BELOW,
    HIGH_SPAN,
    LOW_SPAN,
    Tag,
    WITHIN,
    WITHOUT,
)
from contrast.api.dtm_pb2 import TraceTaintRange
from contrast.utils.assess.tag_utils import merge_tags, ordered_merge
from contrast.utils.string_utils import protobuf_safe


class Properties(object):
    def __init__(self, origin):
        self.origin = origin
        self.reset()

    def reset(self):
        self.tags = {}
        self.events = []
        self.dynamic_source_metadata = {}
        self.timestamp = time.time()

    def copy(self, tag_offset=0):
        """
        Return a (shallow) copy of this object
        """
        new = self.__class__(self.origin)

        # Copy tags to given offset
        new.tags = {}
        for name, tag_list in self.tags.items():
            new.tags[name] = [tag.copy_modified(tag_offset) for tag in tag_list]

        # Creating copies of the events themselves should not be necessary
        new.events = self.events[:]
        new.dynamic_source_metadata = dict(self.dynamic_source_metadata)
        # Since the timestamp is used for age-off, it should not be copied
        new.timestamp = time.time()
        return new

    def __repr__(self):
        return repr(self.origin)

    def is_tracked(self):
        return bool(self.tags)

    def is_empty(self):
        return not self.is_tracked()

    def is_tagged(self, label):
        return label in self.tags

    def add_property(self, name, value):
        if not name or not value:
            return

        self.dynamic_source_metadata[name] = value

    def add_properties(self, dict_):
        if dict_:
            self.dynamic_source_metadata.update(dict_)

    def tag_keys(self):
        return self.tags.keys()

    def get_tags_at(self, index):
        """
        Find all of the tags that span a given index.
        """
        tags_at = set()

        for key, value in self.tags.items():
            for tag in value:
                if tag.covers(index):
                    tags_at.add(key)

        return list(tags_at)

    def last_tagged_index(self):
        """
        Returns the highest index of any tag range

        Since we can't reliably compute the length of the tagged object, we use this
        to determine the extent of all of the tag ranges that cover this object.
        """
        last_idx = 0

        for tag_list in self.tags.values():
            for tag in tag_list:
                if tag.end_index > last_idx:
                    last_idx = tag.end_index

        return last_idx

    def tags_at_range(self, tag_range):
        """
        Given a range, select all tags in that range the selected tags are
        shifted such that the start index of the new tag (0) aligns with the
        given start index in the range

        Example:
          current tags: 5-15
          range       : 5-10
          result      : 0-05
        :param tag_range: AdjustedSpan object with range of tag
        """
        location = {}

        length = tag_range.length()

        for key, value in self.tags.items():

            add = []

            for tag in value:

                comparison = tag.compare_range(tag_range.start, tag_range.stop)

                if comparison in [ABOVE, BELOW]:
                    continue
                elif comparison == LOW_SPAN:
                    add.append(Tag(tag.end_index - tag_range.start))
                elif comparison == HIGH_SPAN:
                    add.append(
                        Tag(
                            tag_range.stop - tag.start_index,
                            tag.start_index - tag_range.start,
                        )
                    )
                elif comparison == WITHOUT:
                    add.append(Tag(length))
                elif comparison == WITHIN:
                    add.append(Tag(tag.length, tag.start_index - tag_range.start))

            if len(add) != 0:
                location[key] = add

        return location

    def add_tag(self, label, tag_range):
        """
        Given a tag name and range object, add a new tag to this
        collection. If the given range touches an existing tag,
        we'll combine the two, adjusting the existing one and
        dropping this new one.

        :param label: tag label string
        :param tag_range: AdjustedSpan of tag range
        :return:
        """
        length = tag_range.length()
        tag = Tag(length, tag_range.start)
        self.add_existing_tag(label, tag)

    def add_existing_tag(self, label, tag):
        """
        Add an existing tag

        This function should really be called "add_tag", and the existing
        function with that name should be "add_tag_at".
        """
        existing = self.fetch_tags(label)
        self.set_tag(label, ordered_merge(existing, tag))

    def set_tag(self, label, tag_ranges):
        self.tags[label] = tag_ranges

    def delete_tag(self, label):
        try:
            del self.tags[label]
        except KeyError:
            pass

    def clear(self):
        self.tags = {}

    def cleanup_tags(self):
        """
        Merged tags that are touching or overlapping and delete empty tags
        """
        merge_tags(self.tags)

        # delete empty lists
        to_delete = [key for key, value in self.tags.items() if not value]
        for key in to_delete:
            del self.tags[key]

    def fetch_tags(self, label):
        return self.tags.get(label)

    ENCODED_MARKER = "_ENCODED"

    def fetch_encoded_tags(self):
        """
        Fetch all tags that end with *_ENCODED
        """
        return [
            self.tags[item] for item in self.tags if item.endswith(self.ENCODED_MARKER)
        ]

    def tags_to_dtm(self, splat_range=None):
        """
        Convert Tag objects to TraceTaintRange objects for the service
        """
        ranges = []
        for key, value in self.tags.items():

            if not value:
                continue

            for tag in value:
                taint_range = TraceTaintRange()

                taint_range.tag = key
                tag_range = splat_range or (tag.start_index, tag.end_index)
                taint_range.range = "{}:{}".format(*tag_range)

                ranges.append(taint_range)

        return ranges

    def delete_tags_at_ranges(self, ranges, shift=True):
        """
        Remove all tags within the given ranges.
        This does not delete an entire tag if part of that tag is
        outside this range, meaning we may reduce sizes of tags
        or split them.

        If shift is true, it is assumed the characters at those ranges were
        removed. If shift is false, it is assumed those ranges were replaced
        by the same number of characters and no shift is needed.

        current tags: 0-15
        range:        5-10
        result:       0-5, 10-15

        :param shift:
        :param ranges: list of AdjustedSpan objects
        """
        current_shift = 0

        for tag_range in ranges:
            self.remove_tag(tag_range)

            if shift:
                self.shift_tags_for_deletion(tag_range, current_shift)

                current_shift += tag_range.length()

        merge_tags(self.tags)

    def shift_tags(self, ranges):
        """
        Shift all the tags in this object by the given ranges.
        This method assumes the ranges are sorted, meaning
        the leftmost (lowest) range is first

        current tags: 0-15
        range:        5-10
        result:       0-5, 10-20
        """
        for item in ranges:
            self.shift_tags_for_insertion(item)

    def add_event(self, event):
        """
        Add event to properties
        """
        self.events.append(event)

        self.report_source()

        return self

    def build_event(
        self,
        policy_node,
        tagged,
        self_obj,
        ret,
        args,
        kwargs,
        parent_ids,
        possible_key=None,
        source_type=None,
        source_name=None,
    ):
        """
        Build ContrastEvent from an applied policy method

        After creation of the ContrastEvent, report the event to the ObservedRoute in the RequestContext
        """
        event = ContrastEvent(
            policy_node,
            tagged,
            self_obj,
            ret,
            args,
            kwargs,
            parent_ids,
            possible_key,
            source_type,
            source_name,
        )
        self.add_event(event)

    def report_source(self):
        """
        This is for Route-based Auto-remediation

        We want to associate source events with routes. However, we only want to record
        sources if they are actually used. The reason for this is that the Python agent
        is fairly aggressive with source tracking, and so we preemptively track many
        sources even if they are never used. But to avoid inaccurate RBAV reports, we
        want to make sure sources are recorded only if they actually get used. For
        these purposes, being "used" means a source is the parent of another event.

        Criteria:
        - Previous event doesn't have a source type, do nothing
        - No current context and therefore no observed route, do nothing
        - There is an event of the same name and type, do nothing
        - Can create the TraceEventSource, append to the observed route sources

        :return: None
        """
        if len(self.events) < 2:
            return

        # Check whether the last event before the newest one was a source event.
        # Before this method is called, we add the newest event, which is now
        # self.events[-1]. So we check the event prior to that to see whether it's a
        # source event.
        event = self.events[-2]

        if not event.source_type:
            return

        context = contrast.CS__CONTEXT_TRACKER.current()

        if not context:
            return

        # ignore if the source already exists
        any_source_name_and_type_match = any(
            [
                source.type == event.source_type and source.name == event.source_name
                for source in context.observed_route.sources
            ]
        )

        if any_source_name_and_type_match:
            return

        event_source_dtm = event.build_source_event(protobuf_safe(event.source_name))

        if not event_source_dtm:
            return

        context.observed_route.sources.extend([event_source_dtm])

    def remove_tag(self, tag_range):
        """
        Remove tag ranges in the given range
        :param tag_range: range of tags to delete
        :return: None
        """
        full_delete = []
        for key, tags in list(self.tags.items()):
            indexes_to_remove, tags_to_add = self._find_new_and_old_tags(
                tags, tag_range
            )

            for index in sorted(indexes_to_remove, reverse=True):
                del tags[index]

            ordered_merge(tags, tags_to_add)

            if not tags:
                full_delete.append(key)

        for item in full_delete:
            del self.tags[item]

    def _find_new_and_old_tags(self, tags, tag_range):
        indexes_to_remove = []
        tags_to_add = []

        for index, tag in enumerate(tags):
            comparison = tag.compare_range(tag_range.start, tag_range.stop)

            if comparison == LOW_SPAN:
                tag.set_end(tag_range.start)
            elif comparison == WITHIN:
                indexes_to_remove.append(index)
            elif comparison == WITHOUT:
                new_tag = copy(tag)
                new_tag.set_start(tag_range.stop)

                tags_to_add.append(new_tag)

                tag.set_end(tag_range.start)
            elif comparison == HIGH_SPAN:
                tag.set_start(tag_range.stop)
            elif comparison == ABOVE:
                continue

        return indexes_to_remove, tags_to_add

    def shift_tags_for_deletion(self, tag_range, shift):
        """
        Shift the tag ranges covering the given range
        We assume this is for a deletion, meaning we
        have to move tags to the left
        """
        for value in list(self.tags.values()):
            for tag in value:
                comparison = tag.compare_range(
                    tag_range.start - shift, tag_range.stop - shift
                )
                length = tag_range.length()

                if comparison == ABOVE:
                    tag.shift(0 - length)

    def shift_tags_for_insertion(self, tag_range):
        """
        Shift the tag ranges covering the given range
        We assume this is for a insertion, meaning we
        have to move tags to the right
        """
        for tags in list(self.tags.values()):
            add = []

            for tag in tags:
                comparison = tag.compare_range(tag_range.start, tag_range.stop)

                length = tag_range.length()

                if comparison in [LOW_SPAN, WITHOUT]:
                    add.append(
                        Properties.clone_tag_for_shift(tag, tag_range.start, length)
                    )
                elif comparison in [ABOVE, HIGH_SPAN, WITHIN]:
                    tag.shift(length)

            ordered_merge(tags, add)

    @staticmethod
    def clone_tag_for_shift(tag, new_start, length):
        """
        Copies a new tag and updates its start and end after shifting
        """
        new_tag = copy(tag)

        new_tag.set_start(new_start)

        new_tag.shift(length)

        tag.set_end(new_start)

        return new_tag

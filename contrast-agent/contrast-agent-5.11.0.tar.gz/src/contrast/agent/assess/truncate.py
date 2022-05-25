# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.dtm_pb2 import TraceTaintRange
from contrast.utils.assess.tag_utils import merge_tags
from contrast.agent.assess.tag import Tag


ELLIPSIS = "..."
TRUNCATION_FRAGMENT_LENGTH = 50
TRUNCATION_LENGTH = TRUNCATION_FRAGMENT_LENGTH * 2 + len(ELLIPSIS)


def truncate(str_representation, length_factor=1):
    """
    Truncate + return the provided string
    """
    fragment_length = TRUNCATION_FRAGMENT_LENGTH * length_factor
    if len(str_representation) <= 2 * fragment_length + len(ELLIPSIS):
        return str_representation
    return "".join(
        [
            str_representation[:fragment_length],
            ELLIPSIS,
            str_representation[-fragment_length:],
        ]
    )


def truncate_tainted_string(str_representation, event):
    """
    Truncate + return the provided string and update the provided event's taint_ranges
    accordingly.

    This function assumes:
    - event.taint_ranges has already been calculated
    - each range in event.taint_ranges follows the format "{}:{}"
    - str_representation is the string representation of the tainted object associated
      with the given event, i.e. event.taint_ranges describes str_representation
    """
    if len(str_representation) <= TRUNCATION_LENGTH:
        return str_representation
    if len(event.taint_ranges) == 0:
        return truncate(str_representation)

    # In the eyes of TS, all tags are equally important for taint range calculation.
    # We take advantage of this here to maximally merge and simplify all tags
    # (regardless of tag key).
    merged_tags = _parse_and_merge_tags(event.taint_ranges)

    truncated, truncated_ranges = _truncate_tainted_string(
        str_representation, merged_tags
    )

    _update_event_taint_ranges(event, truncated_ranges)

    return truncated


def _parse_and_merge_tags(taint_range_objs):
    """
    Given a TraceEvent, parse out the existing tag ranges and merge them.

    merge_tags expects a dict, and merges based on tag key (dict key). We use a
    temporary key here for convenience; critically, all tags are given the same key so
    that they're merged together for TS taint calculations.
    """
    tags = {"temp": []}
    for taint_range_obj in taint_range_objs:
        start_idx, end_idx = (int(s) for s in taint_range_obj.range.split(":"))
        tags["temp"].append(Tag(end_idx - start_idx, start_idx))
    merge_tags(tags)
    return tags["temp"]


def _truncate_tainted_string(str_representation, merged_tags):
    """
    The core logic of tainted string truncation. Given a string and a list of simplified
    and merged Tags, truncate the string approximately according to this specification:

    https://bitbucket.org/contrastsecurity/assess-specifications/src/master
    filename: truncate-event-snapshots.md

    Note: this follows the specification very closely, but not exactly.
    """
    truncated = ""
    truncated_ranges = []
    curr_index = 0
    for tag in merged_tags:
        if curr_index < tag.start_index:
            truncated += truncate(str_representation[curr_index : tag.start_index])
        new_fragment = truncate(
            str_representation[tag.start_index : tag.end_index], length_factor=2
        )
        truncated += new_fragment
        truncated_ranges.append((len(truncated) - len(new_fragment), len(truncated)))
        curr_index = tag.end_index
    if curr_index < len(str_representation):
        truncated += truncate(str_representation[curr_index:])

    return truncated, truncated_ranges


def _update_event_taint_ranges(event, truncated_ranges):
    """
    Update a TraceEvent DTM's taint_ranges according to the provided list of ranges.
    """
    # protobuf RepeatedComposite fields don't support clear(), so we resort to this
    while len(event.taint_ranges) > 0:
        event.taint_ranges.pop()

    for start_idx, end_idx in truncated_ranges:
        taint_range = TraceTaintRange()
        # this is not a "real" tag; TS only cares about ranges. The overall ranges
        # produced by this method are correct, but we drop individual tag ranges in
        # favor of a vastly simplified truncation algorithm.
        taint_range.tag = "UNTRUSTED"
        taint_range.range = f"{start_idx}:{end_idx}"
        event.taint_ranges.append(taint_range)

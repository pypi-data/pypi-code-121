# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import io

from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.propagation_node import PropagationNode
from contrast.agent.assess.utils import (
    copy_events,
    copy_tags_in_span,
    copy_tags_to_offset,
    get_last_event_id,
    get_properties,
    set_properties,
)


from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def _get_class_name(obj):
    return obj.__class__.__name__


def _get_stream_len(stream, curpos):
    stream.seek(0, io.SEEK_END)
    size = stream.tell()
    stream.seek(curpos)
    return size


def _propagate_stream_read(node, preshift, target, tag_span, ret):
    """Copies tags and creates event for stream read operations"""
    source_properties = get_properties(preshift.obj)
    target_properties = copy_tags_in_span(target, source_properties, tag_span)
    if target_properties is None:
        return

    copy_events(target_properties, source_properties)
    parent_ids = [get_last_event_id(source_properties)]
    target_properties.build_event(
        node, target, preshift.obj, ret, preshift.args, preshift.kwargs, parent_ids
    )


def propagate_stream_read(method_name, preshift, target, ret):
    class_name = _get_class_name(preshift.obj)
    node = PropagationNode(
        "io", class_name, True, method_name, "OBJ", "RETURN", "STREAM_READ"
    )

    curpos = preshift.obj.tell()
    startpos = curpos - len(target)
    tag_span = (startpos, curpos)

    _propagate_stream_read(node, preshift, target, tag_span, ret)


def propagate_stream_readlines(method_name, preshift, target, ret):
    # Nothing to do if there are no results
    if len(target) < 1:
        return

    class_name = _get_class_name(preshift.obj)
    node = PropagationNode(
        "io", class_name, True, method_name, "OBJ", "RETURN", "STREAM_READ"
    )

    curpos = preshift.obj.tell()
    startpos = curpos - sum(len(x) for x in target)

    # Readlines returns a list of lines (including newlines)
    for line in target:
        tag_span = (startpos, startpos + len(line))
        _propagate_stream_read(node, preshift, line, tag_span, ret)
        startpos += len(line)


def propagate_stream_getvalue(method_name, preshift, target, ret):
    class_name = _get_class_name(preshift.obj)
    node = PropagationNode(
        "io", class_name, True, method_name, "OBJ", "RETURN", "STREAM_GETVALUE"
    )

    tag_span = (0, len(target))

    _propagate_stream_read(node, preshift, target, tag_span, ret)


def _copy_old_props_from_stream(stream, startpos, curpos):
    if not stream.cs__tracked:
        return None

    old_props = get_properties(stream)
    new_props = old_props.copy()
    # Tags will be updated below
    new_props.tags = {}

    # Copy all tags from the stream prior to the newly written data
    prefix_tags = old_props.tags_at_range(AdjustedSpan(0, startpos))
    copy_tags_to_offset(new_props, prefix_tags, 0)

    # Copy all tags from the stream after the newly written data
    streamlen = _get_stream_len(stream, curpos)
    postfix_tags = old_props.tags_at_range(AdjustedSpan(curpos, streamlen))
    copy_tags_to_offset(new_props, postfix_tags, curpos)

    return new_props


def propagate_stream_write(method_name, preshift, target, ret):
    # This would indicate an error made by the caller, so we can just quit
    if len(preshift.args) < 1:
        return

    # If the stream is a source, no action required (for now)
    # We don't really expect this to occur, and if it does occur frequently it means
    # the stream involved should potentially not be marked as a source after all.
    # The current behavior means that any data written to a source stream will
    # be tagged as UNTRUSTED when it gets read out, regardless of whether it
    # was tracked or not to begin with.
    if preshift.obj.cs__source:
        logger.debug("Data written to source stream; no propagation occurred")
        return

    # Think of write as a special case of writelines
    lines = preshift.args[0] if method_name == "writelines" else [preshift.args[0]]
    props = [get_properties(line) for line in lines]
    # Short circuit here if none of the data, new or old, is tracked
    if not any(props) and not preshift.obj.cs__tracked:
        return

    # Get the current position of the stream cursor (after the write has finished)
    curpos = preshift.obj.tell()
    # Compute the position of the stream cursor before the write occurred
    startpos = curpos - sum([len(line) for line in lines])

    # Copy any tags from the original stream outside of the span of newly written data
    new_props = _copy_old_props_from_stream(preshift.obj, startpos, curpos)

    parent_ids = []

    # TODO: PYT-911 this is not quite right. We make it look like the most recent event on
    # the original string contributes to the `write` event, but that's not really
    # accurate. Instead, the write event and the stream event should contribute to any
    # subsequent `read` events. But this requires an additional level of bookkeeping.
    # We'll pass for now since it only affects trace reports, and not accuracy.
    if new_props is not None and new_props.events:
        parent_ids.append(new_props.events[-1].event_id)

    # Iterate over all newly written lines and copy tags if the line is tracked
    for line, source_props in zip(lines, props):
        if source_props is not None:
            # This means that the original stream was not tracked at all
            if new_props is None:
                new_props = source_props.copy(tag_offset=startpos)
            else:
                copy_tags_to_offset(new_props, source_props.tags, startpos)
                copy_events(new_props, source_props)

            if source_props.events:
                parent_ids.append(source_props.events[-1].event_id)

        startpos += len(line)

    # Update with new properties on stream object
    preshift.obj.cs__tracked = True
    set_properties(preshift.obj, new_props)

    # Add event
    class_name = _get_class_name(preshift.obj)
    node = PropagationNode(
        "io", class_name, True, method_name, "ARG_0", "OBJ", "STREAM_WRITE"
    )
    new_props.build_event(
        node, target, preshift.obj, ret, preshift.args, preshift.kwargs, parent_ids
    )

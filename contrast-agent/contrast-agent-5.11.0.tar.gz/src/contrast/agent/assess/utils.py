# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.utils.assess.duck_utils import safe_getattr
from contrast.utils.assess.tag_utils import merge_tags


def get_properties(value):
    return safe_getattr(value, "cs__properties", None)


def set_properties(obj, props):
    obj.cs__properties = props


def clear_properties():
    contrast.STRING_TRACKER.clear()


def is_trackable(obj):
    return hasattr(obj, "cs__properties")


def is_tracked(value):
    return bool(get_properties(value))


def track_string(value):
    return contrast.STRING_TRACKER.track(value)


def copy_events(target_props, source_props):
    if source_props is None or target_props is None or target_props is source_props:
        return

    for event in source_props.events:
        target_props.events.append(event)


def copy_from(to_obj, from_obj, shift=0, skip_tags=None):
    """Copy events and tags from from_obj to to_obj"""
    if from_obj is to_obj:
        return

    if not is_tracked(from_obj):
        return

    from_props = get_properties(from_obj)

    # we assume to_obj has already been tracked and has properties
    to_props = get_properties(to_obj)

    if from_props == to_props:
        return

    copy_events(to_props, from_props)

    for key in from_props.tag_keys():
        if skip_tags and key in skip_tags:
            continue

        new_tags = []

        from_props_tags = from_props.fetch_tags(key)

        for tag in from_props_tags:
            new_tags.append(tag.copy_modified(shift))

        existing_tags = to_props.fetch_tags(key)

        if existing_tags:
            existing_tags.extend(new_tags)
        else:
            to_props.set_tag(key, new_tags)


def get_self_for_method(patch_policy, args):
    """
    Retrieves self for a method's PatchLocationPolicy,

    If any node in the policy has a False instance_method attribute return None
    """
    for node in patch_policy.all_nodes:
        if not node.instance_method:
            return None

    return args[0] if args else None


def get_last_event_id(source_properties):
    if source_properties.events and source_properties.events[-1]:
        last_event = source_properties.events[-1]
        return last_event.event_id
    return None


def get_last_event_ids_from_sources(sources):
    """
    Gathers from given sources the parent IDs that should be used for an event
    """
    id_list = []

    for source in sources:
        source_properties = get_properties(source)
        if source_properties is None:
            continue

        event_id = get_last_event_id(source_properties)
        if event_id is not None and event_id not in id_list:
            id_list.append(event_id)

    return id_list


def copy_tags_in_span(target, source_properties, span, offset=0):
    """
    Given source properties, copies tags at a given span to the target
    """
    span = AdjustedSpan(*tuple(x + offset for x in span))
    source_tags = source_properties.tags_at_range(span)
    if not source_tags:
        return get_properties(target)

    target_properties = track_string(target)
    if target_properties is None:
        return get_properties(target)

    for name, tags in source_tags.items():
        for tag in tags:
            target_properties.add_existing_tag(name, tag)

    merge_tags(target_properties.tags)
    return target_properties


def copy_tags_to_offset(target_properties, source_tags, target_offset):
    """
    Given source tags, copy to target properties at offset.

    The caller is responsible for updating the string tracker if necessary.
    """
    for name, tags in source_tags.items():
        for tag in tags:
            new_tag = tag.copy_modified(target_offset)
            target_properties.add_existing_tag(name, new_tag)

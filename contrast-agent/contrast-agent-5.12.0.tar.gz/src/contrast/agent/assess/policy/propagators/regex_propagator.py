# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.agent import scope
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy.preshift import Preshift
from contrast.agent.assess.utils import (
    copy_events,
    copy_tags_in_span,
    copy_tags_to_offset,
    get_properties,
    get_last_event_id,
    track_string,
)
from contrast.utils.decorators import fail_quietly

from functools import lru_cache

from .split_propagator import SplitPropagator


@lru_cache(maxsize=10)
def _get_regex_policy_node(method_name):
    policy = Policy()
    patch_policy = policy.policy_by_name.get(f"re.Match.{method_name}")
    return patch_policy.propagator_nodes[0] if patch_policy.propagator_nodes else None


def _propagate_group_string(
    method_name, target, source_properties, span, preshift, retval
):

    policy_node = _get_regex_policy_node(method_name)
    if policy_node is None:
        return

    target_properties = copy_tags_in_span(target, source_properties, span)
    # This can be None if len(target) < 2
    if target_properties is None:
        return

    parent_ids = [get_last_event_id(source_properties)]

    copy_events(target_properties, source_properties)

    target_properties.build_event(
        policy_node,
        target,
        preshift.obj,
        retval,
        preshift.args,
        preshift.kwargs,
        parent_ids,
    )


@fail_quietly("Failed to propagate regex group")
def propagate_group(self_obj, target, *args):
    """
    Propagator for re.Match.group()

    self_obj:
        re.Match object
    target:
        str result of calling .group()
    """
    source_properties = get_properties(self_obj.string)
    if source_properties is None:
        return

    # If no args are given, we simply process the 0th group, which is the
    # match for the entire pattern.
    if not args:
        args = [0]

    # If fewer than two args are given, the result is a single string match.
    # Otherwise, the result is an iterable of strings.
    if len(args) < 2:
        target = [target]

    preshift = Preshift(self_obj.string, args, {})

    for string, group in zip(target, args):
        _propagate_group_string(
            "group", string, source_properties, self_obj.span(group), preshift, target
        )


@fail_quietly("Failed to propagate regex groups")
def propagate_groups(self_obj, target, *args):
    """
    Propagator for re.Match.groups()

    self_obj:
        re.Match object
    target:
        tuple of str objects; result of calling .group()
    """
    # If there were no groups, this will be an empty tuple
    if not target:
        return

    source_properties = get_properties(self_obj.string)
    if source_properties is None:
        return

    preshift = Preshift(self_obj.string, args, {})

    for string, span in zip(target, self_obj.regs[1:]):
        _propagate_group_string(
            "groups", string, source_properties, span, preshift, target
        )


@fail_quietly("Failed to propagate regex groupdict")
def propagate_groupdict(self_obj, target, *args):
    """
    Propagator for re.Match.groupdict()

    self_obj:
        re.Match object
    target:
        dict with group names as keys and matched strings as values
    """
    # If there were no named groups, this will be an empty tuple
    if not target:
        return

    source_properties = get_properties(self_obj.string)
    if source_properties is None:
        return

    preshift = Preshift(self_obj.string, args, {})

    for name, value in target.items():
        _propagate_group_string(
            "groupdict", value, source_properties, self_obj.span(name), preshift, target
        )


def _propagate_sub_tags(
    target_properties,
    orig_properties,
    repl_properties,
    string,
    count,
    source_matches,
    repl_results,
):

    source_offset = 0
    target_offset = 0

    for i in range(count):
        match = source_matches[i]
        # Copy any tags from the source string prior to the match
        if orig_properties is not None:
            span = AdjustedSpan(source_offset, match.start())
            source_tags = orig_properties.tags_at_range(span)
            copy_tags_to_offset(target_properties, source_tags, target_offset)

        target_offset += match.start() - source_offset
        source_offset = match.end()

        # Copy any tags from the replacement string
        if repl_properties[i] is not None:
            copy_tags_to_offset(
                target_properties, repl_properties[i].tags, target_offset
            )

        target_offset += len(repl_results[i])

    if source_offset < len(string) and orig_properties is not None:
        old_span = AdjustedSpan(source_offset, len(string))
        source_tags = orig_properties.tags_at_range(old_span)
        copy_tags_to_offset(target_properties, source_tags, target_offset)


def _propagate_sub_events(
    node,
    target_properties,
    orig_properties,
    repl_properties,
    target,
    args,
    kwargs,
):

    parent_ids = []
    if orig_properties is not None:
        parent_ids.append(get_last_event_id(orig_properties))

    copy_events(target_properties, orig_properties)

    for props in repl_properties:
        copy_events(target_properties, props)
        if props is not None:
            parent_ids.append(get_last_event_id(props))

    target_properties.build_event(node, target, None, target, args, kwargs, parent_ids)


@fail_quietly("Failed to propagate regex sub(n)")
def propagate_sub(node, target, repl_results, pattern, repl, string, count=0, **kwargs):
    """
    Propagator for re.sub and re.subn
    """
    with scope.contrast_scope():
        # contrast scope required here to prevent analysis in finditer patch.
        source_matches = (
            list(pattern.finditer(string))
            if node.instance_method
            else list(re.finditer(pattern, string, kwargs.get("flags", 0)))
        )

    # No propagation necessary because no replacement occurred
    if len(source_matches) == 0:
        return

    count = min(len(source_matches), count) if count > 0 else len(source_matches)

    # If the repl was not a callable, then the replacement string is the same
    # for each occurrence of the pattern
    if repl_results is None:
        repl_results = [repl] * len(source_matches)

    orig_properties = get_properties(string)
    repl_properties = [get_properties(x) for x in repl_results]
    if orig_properties is None and not any(repl_properties):
        return

    target_properties = get_properties(target) or track_string(target)

    _propagate_sub_tags(
        target_properties,
        orig_properties,
        repl_properties,
        string,
        count,
        source_matches,
        repl_results,
    )

    args = (pattern, repl, string)
    _propagate_sub_events(
        node,
        target_properties,
        orig_properties,
        repl_properties,
        target,
        args,
        kwargs,
    )

    target_properties.cleanup_tags()


class RegexSplitPropagator(SplitPropagator):
    @property
    def needs_propagation(self):
        if not self.preshift:
            return False

        return self.any_source_tracked

    @property
    def is_pattern_method(self):
        return self.node.class_name == "Pattern"

    def _get_flags(self):
        if self.is_pattern_method:
            return self.preshift.obj.flags
        if len(self.preshift.args) == 4:
            return self.preshift.args[-1]
        return self.preshift.kwargs.get("flags", 0)

    def _get_pattern(self):
        return self.preshift.obj if self.is_pattern_method else self.preshift.args[0]

    def _propagate(self, string, flags, pattern, source_properties):
        source_offset = 0
        target_index = 0

        while target_index < len(self.target):
            # If the pattern passed to re.split contains any groupings, then
            # those groupings need to be propagated appropriately.
            if self.is_pattern_method:
                match = pattern.match(string[source_offset:])
            else:
                match = re.match(pattern, string[source_offset:], flags=flags)
            if match is not None:
                for target, span in zip(self.target[target_index:], match.regs[1:]):
                    target_properties = copy_tags_in_span(
                        target, source_properties, span, offset=source_offset
                    )
                    copy_events(target_properties, source_properties)
                    target_index += 1
                source_offset += len(match.group())

            if target_index < len(self.target):
                target = self.target[target_index]
                span = (source_offset, source_offset + len(target))
                target_properties = copy_tags_in_span(target, source_properties, span)
                copy_events(target_properties, source_properties)

                source_offset += len(target)
                target_index += 1

    def propagate(self):
        string = self.sources[0]
        flags = self._get_flags()
        pattern = self._get_pattern()

        source_properties = get_properties(string)
        if source_properties is None:
            return

        self._propagate(string, flags, pattern, source_properties)


class RegexFindallPropagator(RegexSplitPropagator):
    def propagate(self):
        """
        Propagation action for re.findall and re.Pattern.findall

        When the number of groups in the given pattern is 1 or 0 (which indicates an
        implicit group corresponding to the whole pattern), findall returns a flat list
        representing one result per match. In this case, the propagation action is
        identical to the action for re.split, so we simply call the parent method.

        When the number of groups is greater than 1, findall returns a list of tuples
        where each tuple represents the groups corresponding to a given match. In this
        case, we use finditer to get the corresponding Match instances in order to
        determine the spans to use for propagation.
        """
        string = self.sources[0]
        source_props = get_properties(string)
        if source_props is None:
            return

        flags = self._get_flags()
        pattern = re.compile(self._get_pattern())
        if pattern.groups < 2:
            self._propagate(string, flags, pattern, source_props)
            return

        # We know we're in scope here, so we're safe to call finditer
        matches = (
            pattern.finditer(string)
            if self.is_pattern_method
            else re.finditer(pattern, string, flags)
        )

        for target, match in zip(self.target, matches):
            for i, result in enumerate(target):
                target_properties = copy_tags_in_span(
                    result,
                    source_props,
                    # skip the first span since it duplicates the entire match
                    match.span(i + 1),
                )

                # This can be None if len(target) < 2
                if target_properties is None:
                    continue

                parent_ids = [get_last_event_id(source_props)]

                copy_events(target_properties, source_props)

                target_properties.build_event(
                    self.node,
                    result,
                    self.preshift.obj,
                    result,
                    self.preshift.args,
                    self.preshift.kwargs,
                    parent_ids,
                )

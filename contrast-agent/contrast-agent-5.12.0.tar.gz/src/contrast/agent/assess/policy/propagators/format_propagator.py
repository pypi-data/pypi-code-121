# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.policy.propagators import BasePropagator
from contrast.agent.assess.utils import (
    copy_events,
    get_last_event_ids_from_sources,
    get_properties,
    track_string,
)
from contrast.utils.assess import tracking_util
from contrast.utils.assess.tag_utils import merge_tags
from contrast.utils.assess.formatting import FormatToken, StringToken
from contrast.utils.assess.formatting.tokenize_format import tokenize_format
from contrast.utils.assess.formatting.tokenize_cformat import (
    tokenize_format as tokenize_cformat,
)
from contrast.utils.decorators import cached_property


class FormatPropagator(BasePropagator):
    def __init__(self, node, preshift, target):
        super().__init__(node, preshift, target)
        if node.method_name == "cformat":
            self.tokens = tokenize_cformat(preshift.obj)
        else:
            self.tokens = tokenize_format(preshift.obj)
        self._tracked_args = None

    def any_args_tracked(self):
        for string in self.sources:  # pylint: disable=not-an-iterable
            if tracking_util.recursive_is_tracked(string):
                return True

        return False

    @cached_property
    def sources(self):
        sources = []
        # Any string that corresponds to a format token is a source
        for token in self.tokens:
            if isinstance(token, FormatToken):
                sources.append(token.get_arg(self.preshift.args, self.preshift.kwargs))
        return sources + [self.preshift.obj]

    @property
    def tracked_args(self):
        if self._tracked_args is None:
            self._tracked_args = self.any_args_tracked()
        return self._tracked_args

    def get_parent_ids(self, *args):
        return get_last_event_ids_from_sources(self.sources)

    @property
    def inputs_require_propagation(self):
        if tracking_util.recursive_is_tracked(self.preshift.obj):
            return True

        return self.tracked_args

    def track_target(self):
        if tracking_util.recursive_is_tracked(self.preshift.obj) or self.tracked_args:
            track_string(self.target)

    def _propagate(self):
        args, kwargs = self.preshift.args, self.preshift.kwargs

        # Offset in the target string
        target_offset = 0

        source_properties = get_properties(self.preshift.obj)

        for token in self.tokens:
            if isinstance(token, StringToken):
                self._propagate_formatted_string_properties(
                    token, target_offset, source_properties, self.target_properties
                )
                target_offset += len(token)
            else:  # FormatToken
                # Format the original input string, accounting for conversion
                # and spec, so that we know exactly how long it is in the
                # result string. We are in scope so this is safe
                orig_value, formatted = token.format(args, kwargs)
                self._propagate_formatted_string_properties(
                    token,
                    target_offset,
                    source_properties,
                    self.target_properties,
                    formatted=formatted,
                )
                self._propagate_format_specifier_properties(
                    orig_value, self.target_properties, target_offset
                )
                target_offset += len(formatted)

        if source_properties is not None:
            copy_events(self.target_properties, source_properties)

        merge_tags(self.target_properties.tags)

    def _propagate_formatted_string_properties(
        self, token, target_offset, source_properties, target_properties, formatted=None
    ):
        """
        Any tag that spans a format specifier will be expanded to
        cover the entirety of the formatted portion of the result
        """
        if source_properties:
            source_tags = source_properties.tags_at_range(token.span)

            if formatted is not None:
                token_len = len(formatted)
            else:
                token_len = len(token)

            for name in source_tags:
                end_offset = target_offset + token_len
                new_span = AdjustedSpan(target_offset, end_offset)
                target_properties.add_tag(name, new_span)

    def _propagate_format_specifier_properties(
        self, orig_value, target_properties, target_offset
    ):
        format_properties = get_properties(orig_value)
        if format_properties:
            for name, tag_ranges in format_properties.tags.items():
                for tag in tag_ranges:
                    # The span of the tag should not include any of the
                    # padding that is added by the formatter since it
                    # does not belong to the original string
                    new_span = tag.to_span(shift=target_offset)
                    target_properties.add_tag(name, new_span)

            copy_events(target_properties, format_properties)

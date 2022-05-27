# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import copy

from contrast.agent.assess.policy.propagators import SplatPropagator


class EncodeHtmlSplatPropagator(SplatPropagator):
    """
    This propagator is used by sanitizers such as markupsafe.escape
    and other escape functions with functionality that does not escape
    an input string if this input string has an attribute __html__.

    Because of this, if the input string has this __html__ attr,
    we remove the HTML_ENCODED tag in this propagator as we know it will
    not be sanitized by the original function (escape or the like).

    Note that we have to store the original tags because PropagationNode instances
    are only initialized once.
    """

    def propagate(self):
        """
        Store the original tags to be able to restore them later
        and then check if the input string has an __html__ attr.
        If it does, we remove the HTML_ENCODED tag for this propagation
        cycle, but then restore all tags so it does not affect
        the next time the propagation node has to be used.
        """
        string_to_escape = self.sources[0]
        self.original_tags = copy.copy(self.node.tags)

        if hasattr(string_to_escape, "__html__"):
            self.node.tags.discard("HTML_ENCODED")

        super().propagate()

    def reset_tags(self):
        self.node.tags = self.original_tags

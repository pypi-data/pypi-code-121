# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators.base_propagator import (
    BasePropagator,
    SUPPORTED_TYPES,
)
from contrast.agent.assess.utils import (
    is_tracked,
    get_properties,
    track_string,
)
from contrast.utils.assess.duck_utils import is_iterable, safe_iterator


class JsonPropagator(BasePropagator):
    """
    JSON Propagator to check if any sources in a dict are tracked
    If tracked, splat tags to result string

    This propagator is specifically for json.dumps; this method will convert a dict to a string
    We need to check if any tracked items in the dict are tracked, if any of them are, we need
    to transition any tags over to the result and track the new dumped string

    Example:
        tracked = 'vuln'
        dict = {'user': 'bob', 'account': tracked}

        result = json.dumps(dict)  # '{"user": "bob", "account": "vuln"}' <= track this
    """

    @property
    def inputs_require_propagation(self):
        return True

    def propagate(self):
        """
        json.dumps only has one source ARG_0;
        ARG_1 for json.dump is the output IO so not a source
        """
        self.first_source = self.sources[0]
        self._propagate(self.first_source)

    def _propagate(self, item):
        if not item:
            return

        if isinstance(item, SUPPORTED_TYPES):
            if is_tracked(item):
                self._apply_tags(item)
        elif isinstance(item, dict):
            for key, value in item.items():
                self._propagate(key)
                self._propagate(value)
        elif is_iterable(item):
            for it in safe_iterator(item):
                self._propagate(it)

    def _apply_tags(self, item):
        """
        Transfer all items from the item to the target, our result
        :param item: value from the dict

        This is a private method and does not overload the base `apply_tags`
        method as it doesn't require the same args.
        """
        target = self.target

        item_properties = get_properties(item)
        target_properties = get_properties(target) or track_string(target)

        if item_properties and target_properties:
            for event in item_properties.events:
                target_properties.events.append(event)

            self.splat_tags(item, target)

            target_properties.cleanup_tags()

        return target_properties

    def track_target(self):
        """NOP; Let propagate handle the decision to track"""
        pass

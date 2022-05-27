# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.agent.assess.utils import (
    copy_events,
    copy_tags_to_offset,
    copy_from,
    get_properties,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class AppendPropagator(BasePropagator):
    def _propagate(self):
        second_source = None

        if len(self.sources) > 1:
            second_source = self.sources[1]

        # if the object and the return are the same length just copy the tags
        # from the object(since nothing from args was added to return)
        if len(self.first_source) == len(self.target):
            copy_from(self.target, self.first_source, 0, self.node.untags)
        else:
            # find original in the target, copy tags to the new position in target
            try:
                original_start_index = self.target.index(self.first_source)
            except Exception:
                logger.debug(
                    "%s was not found in the target %s", self.first_source, self.target
                )
                return

            copy_from(
                self.target, self.first_source, original_start_index, self.node.untags
            )

            start = original_start_index + len(self.first_source)
            if second_source is not None:
                source_properties = get_properties(second_source)
                if source_properties is not None:
                    copy_tags_to_offset(
                        self.target_properties, source_properties.tags, start
                    )
                    copy_events(self.target_properties, source_properties)

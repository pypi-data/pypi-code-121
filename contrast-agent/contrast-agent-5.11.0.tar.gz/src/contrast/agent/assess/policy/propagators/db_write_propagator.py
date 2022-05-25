# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.utils import get_properties
from contrast.agent.assess.policy.propagators.base_propagator import BasePropagator
from contrast.utils.decorators import fail_quietly

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DBWritePropagator(BasePropagator):
    """
    Propagator to handle stored XSS. This propagator assumes the database
    column names are passed in via ALL_KWARGS.

    For each column name, patch the getter/setter property for the column name
    and create dynamic sources for these properties.
    """

    @property
    @fail_quietly(
        "Failed to determine if DB_WRITE needs propagation", return_value=False
    )
    def needs_propagation(self):
        """
        Here, the source is ALL_KWARGS. self.sources[0] is the kwarg dictionary.
        Each key is a column name, and each value is the value for this particular
        ORM instance (corresponding to a DB row) in that column.

        We need to check if any of the values are tracked strings. If so, we save
        all relevant information to be used in propagate().
        """
        from contrast.agent.policy.applicator import build_method_name

        self.new_column_sources = {}
        cls = self.preshift.obj.__class__
        source = self.sources[0]

        for col_name, value in source.items():
            if not value:
                continue

            cs_method_name = build_method_name(col_name)
            if hasattr(cls, cs_method_name):
                continue

            col_value_properties = get_properties(value)
            if col_value_properties is None:
                continue

            self.new_column_sources[col_name] = col_value_properties

        return len(self.new_column_sources) > 0

    def track_target(self):
        """
        This propagator does not track the target because the target is
        an instance of an ORM model, such as django's Model class. If it
        were a string instead, we would track it.
        """
        pass

    def add_tags_and_properties(self, ret):
        """
        Because the target is an instance of an ORM model,
        such as django's Model class, and not a string, we do this
        work inside self.propagate(). Later on we could refactor
        to move the work here.
        """
        pass

    def propagate(self):
        from contrast.agent.policy.applicator import (
            apply_patch_to_dynamic_property,
            save_original_method,
            build_method_name,
        )

        cls = self.preshift.obj.__class__

        for col_name, col_value_properties in self.new_column_sources.items():
            cs_method_name = build_method_name(col_name)
            old_property = getattr(cls, col_name)
            if not save_original_method(cls, cs_method_name, old_property):
                continue

            self.apply_tags(self.node, col_value_properties.origin)

            tags = [tag for tag in col_value_properties.tags]
            logger.debug("DB_WRITE adding column as dynamic source: %s", col_name)
            apply_patch_to_dynamic_property(cls, col_name, tags)

            col_value_properties.build_event(
                self.node,
                col_value_properties.origin,
                self.preshift.obj,
                self.target,
                self.preshift.args,
                self.preshift.kwargs,
                [],
                0,
                None,
            )

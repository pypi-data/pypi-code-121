# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Event type systemfield for events records."""

import inspect

from invenio_records.systemfields import ModelField

from ...customizations import EventType
from ...proxies import current_event_type_registry


class EventTypeField(ModelField):
    """Systemfield for managing the request event type."""

    @staticmethod
    def get_instance(value):
        """Ensure that always an instance is returned."""
        if inspect.isclass(value):
            # if a class was passed rather than an instance, try to instantiate it
            value = value()

        if isinstance(value, str):
            value = current_event_type_registry.lookup(value)

        if not isinstance(value, EventType):
            raise TypeError(f"Expected 'EventType' but got: '{type(value)}'")
        return value

    def _set(self, model, value):
        """Initialize model value."""
        value = EventTypeField.get_instance(value)
        super()._set(model, value.type_id)

    def set_obj(self, instance, obj):
        """."""
        self.set_dictkey(instance, obj.type_id)
        self._set_cache(instance, obj)
        self._set(instance.model, obj)

    def __set__(self, record, value):
        """."""
        assert record is not None
        value = EventTypeField.get_instance(value)
        self.set_obj(record, value)

    def obj(self, instance):
        """Get the request type."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        # check model for the type_id
        type_id = super().__get__(instance)
        if not type_id:
            # check in passed instance for the type_id
            type_id = self.get_dictkey(instance)
        obj = EventTypeField.get_instance(type_id)
        self._set_cache(instance, obj)

        return obj

    def __get__(self, record, owner=None):
        """Get the request type."""
        # Class access
        if record is None:
            return self

        return self.obj(record)

    #
    # Record extension
    #
    def pre_init(self, record, data, model=None, **kwargs):
        """Ensure type is always in the registry."""
        _type = kwargs.get("type")
        if _type is None:
            # retrieve type from instantiated model
            _type = model.type
        value = EventTypeField.get_instance(_type).type_id
        try:
            # validate type
            current_event_type_registry.lookup(value)
        except KeyError:
            raise TypeError(f"Event type {value} is not registered.")

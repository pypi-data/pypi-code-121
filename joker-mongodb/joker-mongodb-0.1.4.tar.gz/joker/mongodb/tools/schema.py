#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Iterable, Type, TypeVar

from bson import ObjectId
from pymongo.collection import Collection


class MongoFieldSchemator:
    _bsontype_of_pytypes = {
        str: 'string',
        dict: 'object',
        type(None): 'null',
        datetime.datetime: 'date',
        int: 'long',
        bool: 'bool',
        ObjectId: 'objectId',
    }

    _max_enum_length = 7
    _max_type_length = 3

    def __init__(self):
        self._bsontypes = set()
        self._enum_values = set()

    @property
    def _enum_enabled(self) -> bool:
        if len(self._enum_values) > self._max_enum_length:
            return False
        return set not in self._enum_values

    def _add_bsontype(self, val):
        try:
            bsontype = self._bsontype_of_pytypes[type(val)]
        except KeyError:
            return
        self._bsontypes.add(bsontype)

    def _add_enum_value(self, val):
        if self._enum_enabled:
            return
        try:
            self._enum_values.add(val)
        except TypeError:
            self._enum_values.add(set)

    def add(self, val):
        self._add_enum_value(val)
        self._add_bsontype(val)

    @property
    def bsontype(self) -> str | list[str] | None:
        if not self._bsontypes:
            return
        if len(self._bsontypes) > self._max_type_length:
            return
        _bsontypes = list(self._bsontypes)
        if len(_bsontypes) > 1:
            return _bsontypes
        return _bsontypes[0]

    @property
    def enum(self) -> list | None:
        if not self._enum_enabled or not self._enum_values:
            return
        return list(sorted(self._enum_values))

    def to_jsonschema_property(self) -> dict:
        """
        Returns:
            e.g.
            {
               "bsonType": "string",
               "enum": ["low", "mid", "high"],
            }
        """
        p = {'bsonType': self.bsontype, 'enum': self.enum}
        return {k: v for k, v in p.items() if v is not None}


T = TypeVar('T')


class MongoDocumentSchemator:
    def __init__(self, fieldnames: set[str]):
        if not isinstance(fieldnames, set):
            fieldnames = set(fieldnames)
        self._fieldnames = fieldnames
        self._required = fieldnames.copy()
        self._fields = defaultdict(MongoFieldSchemator)

    @classmethod
    def from_initial_records(cls: Type[T], records: Iterable[dict]) -> T:
        fieldnames = set()
        for rec in records:
            fieldnames.update(set(rec))
        return cls(fieldnames)

    @classmethod
    def from_collection(cls: Type[T], coll: Collection) -> T:
        skmtr = MongoDocumentSchemator.from_initial_records(coll.find())
        skmtr.add_many(coll.find())
        return skmtr

    @property
    def fieldnames(self) -> set:
        return self._fieldnames.copy()

    def add(self, record: dict):
        for key in self._fieldnames:
            val = record.get(key)
            self._fields[key].add(val)
            if val is None and val in self._required:
                self._required.remove(key)

    def add_many(self, records: Iterable[dict]):
        for rec in records:
            self.add(rec)

    def get_properties(self) -> dict[str, dict]:
        return {k: v.to_jsonschema_property() for k, v in self._fields.items()}

    def get_required(self) -> list[str]:
        return list(sorted(self._required))

    def to_jsonschema(self) -> dict:
        return {
            # $jsonSchema keyword '$schema' is not currently supported
            # "$schema": "http://json-schema.org/draft-04/schema#",
            'type': 'object',
            'properties': self.get_properties(),
            'required': self.get_required(),
        }


__all__ = ['MongoFieldSchemator', 'MongoDocumentSchemator']

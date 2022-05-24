# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing

from shapelets.model.sequence import Sequence


class AttributeNames(Enum):
    BEGIN = "begin"
    CORRELATION = "correlation"
    END = "end"
    ID = "id"
    MATCH = "Match"
    PROPERTIES = "properties"
    SEQUENCE = "sequence"
    SEQUENCE_ID = "sequence_id"
    VIEW = "view"
    VIEW_GROUP_ENTRY = "ViewGroupEntry"


class View:
    def __init__(self, sequence: Sequence, begin: int, end: int):
        self.sequence = sequence
        self.begin = begin
        self.end = end

    def __hash__(self):
        return hash((self.sequence, self.begin, self.end))

    def __eq__(self, other):
        return (isinstance(other, View) and
                self.sequence == other.sequence and
                self.begin == other.begin and
                self.end == other.end)

    def __str__(self):
        return (f"{AttributeNames.VIEW.value}({AttributeNames.SEQUENCE.value}={self.sequence}, "
                f"{AttributeNames.BEGIN.value}={self.begin}, "
                f"{AttributeNames.END.value}={self.end})")

    def __repr__(self):
        return (f"{AttributeNames.VIEW.value}({AttributeNames.SEQUENCE.value}={self.sequence}, "
                f"{AttributeNames.BEGIN.value}={self.begin}, "
                f"{AttributeNames.END.value}={self.end})")

    def to_dict(self):
        return {
            AttributeNames.SEQUENCE_ID.value: self.sequence.sequence_id,
            AttributeNames.BEGIN.value: self.begin,
            AttributeNames.END.value: self.end
        }

    @staticmethod
    def from_dict(dct: dict):
        return View(
            sequence=dct[AttributeNames.SEQUENCE.value],
            begin=dct[AttributeNames.BEGIN.value],
            end=dct[AttributeNames.END.value])


class ViewGroupEntry:
    def __init__(self, entry_id: str, view: View, properties: typing.Dict[str, str]):
        self.entry_id = entry_id
        self.view = view
        self.properties = properties

    def __hash__(self):
        return hash((self.entry_id, self.view, self.properties))

    def __eq__(self, other):
        return (isinstance(other, ViewGroupEntry) and
                self.entry_id == other.entry_id and
                self.view == other.view and
                self.properties == other.properties)

    def __str__(self):
        return (f"{AttributeNames.VIEW_GROUP_ENTRY.value}({AttributeNames.ID.value}={self.entry_id}, "
                f"{AttributeNames.VIEW.value}={self.view}, "
                f"{AttributeNames.PROPERTIES.value}={self.properties})")

    def __repr__(self):
        return (f"{AttributeNames.VIEW_GROUP_ENTRY.value}({AttributeNames.ID.value}={self.entry_id}, "
                f"{AttributeNames.VIEW.value}={self.view}, "
                f"{AttributeNames.PROPERTIES.value}={self.properties})")

    def to_dict(self):
        return {
            AttributeNames.ID.value: self.entry_id,
            AttributeNames.VIEW.value: self.view.to_dict(),
            AttributeNames.PROPERTIES.value: self.properties
        }

    @staticmethod
    def from_dict(dct: dict):
        return ViewGroupEntry(
            entry_id=dct[AttributeNames.ID.value],
            view=View.from_dict(dct[AttributeNames.VIEW.value]),
            properties=dct[AttributeNames.PROPERTIES.value])


class Match:
    def __init__(self, correlation: float, view: View):
        self.correlation = correlation
        self.view = view

    def __hash__(self):
        return hash((self.correlation, self.view))

    def __eq__(self, other):
        return (isinstance(other, Match) and
                self.correlation == other.correlation and
                self.view == other.view)

    def __repr__(self):
        return (f"{AttributeNames.MATCH.value}({AttributeNames.CORRELATION.value}={self.correlation},"
                f" {AttributeNames.VIEW.value}={self.view})")

    def to_dict(self):
        return {
            AttributeNames.CORRELATION.value: self.correlation,
            AttributeNames.VIEW.value: self.view.to_dict()
        }

    @staticmethod
    def from_dict(dct: dict):
        return Match(
            correlation=dct[AttributeNames.CORRELATION.value],
            view=View.from_dict(dct[AttributeNames.VIEW.value]))

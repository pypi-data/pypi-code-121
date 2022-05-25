""" Location field module."""

from dataclasses import dataclass
from typing import Iterator, List
from uuid import UUID


class LocationField:
    """ This class allows saving and reading location in fields """

    @dataclass
    class Point:
        """A point contained within a location field"""
        name: str
        latitude: float
        longitude: float
        address: str

    _property_id: UUID
    _points: List[Point]

    def __init__(self, property_id: UUID):
        self._property_id = property_id
        self._points = []

    def add_point(self, name: str, latitude: float, longitude: float, address: str):
        location = self.Point(name=name, latitude=latitude, longitude=longitude, address=address)
        self._points.append(location)

    def get_points(self):
        return self._points

    def __getitem__(self, key: int):
        return self._points[key]

    def __set__item__(self, key: int, value: Point):
        self._points[key] = value

    def __len__(self):
        return len(self._points)

    def __iter__(self) -> Iterator[Point]:
        return iter(self._points)

    def __reversed__(self) -> Iterator[Point]:
        return reversed(self._points)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._property_id == other._property_id and self._points == other._points

    def append(self, value: Point):
        self._points.append(value)

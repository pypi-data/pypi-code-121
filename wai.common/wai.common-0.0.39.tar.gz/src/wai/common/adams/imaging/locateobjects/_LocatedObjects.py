from collections import UserList
from numbers import Real
from typing import List, Optional, Iterable, Union, Set, Iterator, Dict

from ....file.report import Report, DataType, Field, AbstractField
from ._LocatedObject import LocatedObject
from . import constants


class LocatedObjects(UserList):
    def __init__(self, objects: Optional[Iterable[LocatedObject]] = None):
        super().__init__(objects)

    def subset(self, indices: List[int]) -> "LocatedObjects":
        """
        Returns a new instance using the specified object indices.

        :param indices: The indices for the subset.
        :return:        The subset.
        """
        # Ensure unique indices
        indices = set(indices)

        return LocatedObjects((obj for obj in self if obj.get_index() in indices))

    def remove(self, item: Union[LocatedObject, List[int]]) -> None:
        """
        Removes the objects with the specified indices.

        :param item:    The indices to remove.
        """
        # List implementation
        if isinstance(item, LocatedObject):
            return super().remove(item)

        # Ensure unique indices
        indices: Set[int] = set(item)

        # Pop any objects with indices in the set
        i: int = 0
        while i < len(self):
            if self[i].get_index() in indices:
                self.pop(i)
            else:
                i += 1

    def find(self, index: Union[int, str]) -> Optional[LocatedObject]:
        """
        Returns the object with the specified index.

        :param index:   The index to look for.
        :return:        The object, None if not found.
        """
        # Get both a string and integer representation
        if isinstance(index, str):
            try:
                int_index = int(index)
            except Exception:
                int_index = None
        else:
            int_index = index
            index = str(index)

        for obj in self:
            # Try for exact match
            obj_index_string: str = obj.get_index_string()
            if obj_index_string is not None and obj_index_string == index:
                return obj

            # Try for numeric match
            if int_index is not None and obj.get_index() == int_index:
                return obj

        return None

    def scale(self, scale: float):
        """
        Scales all objects with the provided scale factor.

        :param scale:   The scale factor.
        """
        for obj in self:
            obj.scale(scale)

    def to_report(self, prefix: str = "Object", offset: int = 0, update_index: bool = False) -> Report:
        """
        Turns the located objects into a report. Using a prefix like "Object." will
        result in the following report entries for a single object:

        Object.1.x
        Object.1.y
        Object.1.width
        Object.1.height
        Object.1.poly_x -- if polygon data present
        Object.1.poly_y -- if polygon data present

        :param prefix:          The prefix to use.
        :param offset:          The offset for the index to use.
        :param update_index:    Whether to update the index in the metadata.
        :return:                The generated report.
        """
        # Make sure the prefix doesn't end in a dot
        if prefix.endswith("."):
            prefix = prefix[:-1]

        # Create the empty report
        result: Report = Report()

        # Create a shortcut for adding values
        def add_value(count_string: str, suffix: str, type: DataType, value):
            field: Field = Field(f"{prefix}.{count_string}.{suffix}", type)
            result.add_field(field)
            result.set_value(field, value)

        count: int = 0
        width: int = len(str(len(self)))
        for obj in self:
            count += 1
            count_string: str = str(count + offset).rjust(width, "0")

            # Metadata
            for key, value in obj.metadata.items():
                # Get the datatype of the meta-data
                type: DataType = DataType.UNKNOWN
                if isinstance(value, Real):
                    type = DataType.NUMERIC
                elif isinstance(value, bool):
                    type = DataType.BOOLEAN
                elif isinstance(value, str):
                    type = DataType.STRING

                add_value(count_string, key, type, value)

            # Index
            if update_index:
                add_value(count_string, constants.KEY_INDEX, DataType.STRING, count_string)

            add_value(count_string, constants.KEY_X, DataType.NUMERIC, obj.x)  # X
            add_value(count_string, constants.KEY_Y, DataType.NUMERIC, obj.y)  # Y
            add_value(count_string, constants.KEY_WIDTH, DataType.NUMERIC, obj.width)  # Width
            add_value(count_string, constants.KEY_HEIGHT, DataType.NUMERIC, obj.height)  # Height
            add_value(count_string, constants.KEY_LOCATION, DataType.STRING, obj.get_location())  # Location

            # Polygon
            if obj.has_polygon():
                add_value(count_string, constants.KEY_POLY_X, DataType.STRING, ",".join(map(str, obj.get_polygon_x())))
                add_value(count_string, constants.KEY_POLY_Y, DataType.STRING, ",".join(map(str, obj.get_polygon_y())))

        # Count
        field: Field = Field(f"{prefix}.{constants.KEY_COUNT}", DataType.NUMERIC)
        result.add_field(field)
        result.set_value(field, len(self))

        return result

    @classmethod
    def from_report(cls, report: Report, prefix: str = "Object.") -> "LocatedObjects":
        """
        Retrieves all object from the report.

        :param report:  The report to process.
        :param prefix:  The prefix to look for.
        :return:        The objects found.
        """
        # Make sure the prefix ends in a dot
        if not prefix.endswith("."):
            prefix = prefix + "."

        result: LocatedObjects = LocatedObjects()
        fields: List[AbstractField] = report.get_fields()

        # Group fields
        groups: Dict[str, List[AbstractField]] = {}
        for field in fields:
            if field.name.startswith(prefix):
                current: str = field.name[:field.name.rindex(".")]
                if current not in groups:
                    groups[current] = []
                groups[current].append(field)

        # Process grouped fields
        for group, group_fields in groups.items():
            # Meta-data
            meta = {}
            if len(group) <= len(prefix):
                continue
            meta[constants.KEY_INDEX] = group[len(prefix):]
            for field in group_fields:
                fname = field.name[len(group) + 1:]
                if fname in [constants.KEY_X, constants.KEY_Y, constants.KEY_WIDTH, constants.KEY_HEIGHT]:
                    continue
                meta[field.name[field.name.rindex(".") + 1:]] = report.get_value(field)

            try:
                if (report.has_value(f"{group}.{constants.KEY_X}") and
                        report.has_value(f"{group}.{constants.KEY_Y}") and
                        report.has_value(f"{group}.{constants.KEY_WIDTH}") and
                        report.has_value(f"{group}.{constants.KEY_HEIGHT}")):
                    x: int = round(report.get_real_value(f"{group}.{constants.KEY_X}"))
                    y: int = round(report.get_real_value(f"{group}.{constants.KEY_Y}"))
                    width: int = round(report.get_real_value(f"{group}.{constants.KEY_WIDTH}"))
                    height: int = round(report.get_real_value(f"{group}.{constants.KEY_HEIGHT}"))
                    obj: LocatedObject = LocatedObject(x, y, width, height, **meta)
                    result.append(obj)

                    # Polygon
                    if (report.has_value(f"{group}.{constants.KEY_POLY_X}") and
                            report.has_value(f"{group}.{constants.KEY_POLY_Y}")):
                        obj.metadata[constants.KEY_POLY_X] = report.get_string_value(f"{group}.{constants.KEY_POLY_X}")
                        obj.metadata[constants.KEY_POLY_Y] = report.get_string_value(f"{group}.{constants.KEY_POLY_Y}")
            except Exception:
                # Ignored
                pass

        return result

    # PyCharm doesn't seem to be able to work out the typing for this
    def __iter__(self) -> Iterator[LocatedObject]:
        return super().__iter__()

""" Table module.

This module offers functionality for accessing assets and properties through the abstraction provided by the table class.

Classes:
    Table: Rows represent assets and columns properties.
    RowReference: Reference which can be assigned to relationship fields.
    FieldDef: Definition of a field.
    TableDef: Definition of a table.
"""
from enum import Flag
from functools import reduce
import logging
import uuid
from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any, ByteString, Generator, List, Generic, Mapping, Optional, Type, TypeVar
from uuid import UUID, uuid4
import grpc

from kes.fields.imagefield import ImageField

from kes.proto.table_pb2 import AddRowsRequest, DeleteRowsRequest, ReadTableRequest, Rows, LocationPoint, Field as pb_Field
from kes.proto.table_pb2_grpc import TableStub

from kes.fields.locationfield import LocationField

RowType = TypeVar('RowType')


@dataclass
class RowElement(Generic[RowType]):
    row: RowType
    asset_id: UUID


ParticipantType = TypeVar('ParticipantType')


@dataclass
class RowReference(Generic[ParticipantType]):
    """ Opaque class which represents a reference to a table row """
    asset_type_id: UUID
    asset_id: UUID


class TableFull(Exception):
    """ Exception indication when a row could not be inserted
    because the table is full."""
    ...


@dataclass
class FieldDef:
    """Defines a field.

    This class is used by the script scaffolder to define fields.

    Attributes:
        property_id: Id of the property corresponsing with the field
        flag_constructor: Holds the type of the flag field if applicable.
    """
    property_id: UUID
    flag_type: Type[Flag] | None


PropertyMap = Mapping[str, FieldDef]


@dataclass
class TableDef(Generic[RowType]):
    """Defines a table.

    This class is used by the script scaffolder to define tables.

    Attributes:
        row_type: Row type of this table.
        asset_type_id: UUID of the asset type associated with this table.
        property_map: Mapping from property names to property ids.

    """
    row_type: Type[RowType]
    asset_type_id: UUID
    property_map: PropertyMap


class Table(Generic[RowType], Sequence[RowType]):
    """Table

    Tables are the primary abstraction for manipulating Kes activities.
    This class acts as a container for rows.
    A table corresponds to a asset type, with rows corresponding to assets.

    Operations such as adding rows and deleting rows are executed immediately.
    For example, after executing append_row, the corresponding asset is immediately
    visible in Kes.

    Note that modifying a row is not yet supported. To work around this, delete the
    row and reinsert it.

    Type parameters:
        RowType: The type of rows hold by this class.
    """

    _stub: TableStub
    _activity_id: UUID
    _row_type: Type[RowType]
    _asset_type_id: UUID
    _rows: List[RowElement[RowType]]
    _property_map: PropertyMap
    _rev_property_map: Mapping[UUID, tuple[str, Type[Flag] | None]]

    def __init__(self, stub: TableStub, activity_id: UUID, row_type: Type[RowType], asset_type_id: UUID, property_map: PropertyMap):
        self._stub = stub
        self._activity_id = activity_id
        self._row_type = row_type
        self._asset_type_id = asset_type_id
        self._rows = []
        self._property_map = property_map
        self._rev_property_map = {v.property_id: (k, v.flag_type) for k, v in property_map.items()}

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, key: int):
        return self._rows[key].row

    def __set__item__(self, key: int, value: RowType):
        if not isinstance(value, self._row_type):
            raise TypeError
        self._rows[key].row = value

    def __delitem__(self, key: int):
        asset_id = self._rows[key].asset_id

        request = DeleteRowsRequest(rowIds=[str(asset_id)], activityId=str(self._activity_id))
        self._stub.deleteRows(request)

        del self._rows[key]

    def __iter__(self) -> Generator[RowType, None, None]:
        return (rowElem.row for rowElem in self._rows)

    def __reversed__(self) -> Generator[RowType, None, None]:
        return (rowElem.row for rowElem in reversed(self._rows))

    def append_row(self, value: RowType) -> RowReference[RowType]:
        """Adds the row to the end of the table.

        Args:
            value (RowType): the row to insert.

        Returns: A row reference which can be assigned to relationship fields.

        Raises:
            TableFull: Indicates table cannot hold any more rows.

        """
        if not isinstance(value, self._row_type):
            raise TypeError

        request = AddRowsRequest()
        request.activityId = str(self._activity_id)
        request.tableId = str(self._asset_type_id)
        row = request.rows.add()
        asset_id = uuid4()
        row.assetId = str(asset_id)

        for fieldName, fieldDef in self._property_map.items():
            pb_field = row.fields.add()
            pb_field.propertyId = str(fieldDef.property_id)
            field = getattr(value, fieldName)
            if self._field_is_empty(field):
                continue
            self._serialize_field(field, pb_field)
        try:
            self._stub.addRows(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise TableFull
            else:
                raise

        self._rows.append(RowElement[RowType](value, asset_id))
        return RowReference[RowType](self._asset_type_id, asset_id)

    def get_reference_by_row_index(self, rowIndex: int):
        """Get a reference to the specified row.

            Args:
                rowIndex (int): Index of row to get a reference to.
        """
        asset_id = self._rows[rowIndex].asset_id
        return RowReference[RowType](self._asset_type_id, asset_id)

    def load(self):
        """Load the rows of this table.

        After instantiating a table, it is empty. Call this method to load assets from the Kes activity.
        """

        self._rows = []
        reply: Rows = self._stub.readTable(ReadTableRequest(
            activityId=str(self._activity_id), tableId=str(self._asset_type_id)
        ))
        for row in reply.rows:
            localRow: RowType = self._row_type()

            for field in row.fields:
                revFieldDef = self._rev_property_map.get(UUID(field.propertyId))
                if (revFieldDef is None):
                    logging.warning(
                        'Field with property id %s not found', field.propertyId)
                    continue
                self._deserialize_field(localRow, *revFieldDef, field)

            self._rows.append(RowElement[RowType](
                localRow, uuid.UUID(row.assetId)))

    def save_image(self, image: ImageField, name: str, data: bytes):
        """Save image data and associated name to an image field.

        Args:
            image (ImageField): Image field to write to.
            name (str): The name of the image as visible in Kes.
            data (bytes): Contents of the image file.
        """
        image.save(self._stub, name, data)

    def load_image(self, image: ImageField) -> Optional[ByteString]:
        """Load image data.

        If the image field has an image, return the image data.
        The resulting bytestream can for example be written to a file.
        If there is no image, return `None`.

        Args:
            image (ImageField): The image field whose image data should be read.

        Returns:
             Optional[ByteString]: The image data, or None if there is no image
        """
        return image.load(self._stub)

    def clear(self):
        """Delete all the rows of the table."""
        asset_ids: List[str] = []
        for row_element in self._rows:
            asset_id = str(row_element.asset_id)
            asset_ids.append(asset_id)

        request = DeleteRowsRequest(rowIds=asset_ids, activityId=str(self._activity_id))
        self._stub.deleteRows(request)

        self._rows.clear()

    def _field_is_empty(self, field: Any) -> bool:
        if self is None:
            return True

        if isinstance(field, ImageField):
            return field.is_empty()

        return False

    def _serialize_field(self, field: Any, pb_field: pb_Field):
        match field:
            case float(floatValue):
                pb_field.numbers.elements.append(floatValue)
            case str(textValue):
                pb_field.strings.elements.append(textValue)
            case ImageField() as imageValue:
                if imageValue.key != "":
                    pb_field.image.fileName = imageValue.name
                    pb_field.image.tempKey = imageValue.key
                else:
                    del pb_field
            case LocationField() as locationValue:
                for point in locationValue:
                    locPoint = LocationPoint(name=point.name, latitude=point.latitude,
                                             longitude=point.longitude, address=point.address)
                    pb_field.locations.elements.append(locPoint)
            case Flag() as flag:
                for i, c in enumerate(bin(flag.value)[:1:-1], 1):
                    if c == '1':
                        pb_field.members.elements.append(i)
            case RowReference():
                pb_field.rowReferences.elements.append(str(field.asset_id))
            case firstNumber, *rest if isinstance(firstNumber, float):
                pb_field.numbers.elements[:] = [firstNumber, *rest]
            case firstString, *rest if type(firstString) == str:
                pb_field.strings.elements[:] = [firstString, *rest]
            case firstRowReference, *rest if isinstance(firstRowReference, RowReference):
                for reference in field:
                    if isinstance(reference, RowReference):
                        pb_field.rowReferences.elements.append(str(reference.asset_id))
                    else:
                        raise TypeError
            case _:
                pass

    def _deserialize_field(self, row: Any, attribute_name: str, flag_type: Type[Flag] | None, pb_field: pb_Field):
        match pb_field.WhichOneof("value"):
            case "numbers" if pb_field.multi:
                setattr(row, attribute_name,
                        pb_field.numbers.elements)
            case "numbers":
                value = next(iter(pb_field.numbers.elements), None)
                setattr(row, attribute_name, value)
            case "strings" if pb_field.multi:
                setattr(row, attribute_name,
                        pb_field.strings.elements)
            case "strings":
                value = next(iter(pb_field.strings.elements), None)
                setattr(row, attribute_name, value)
            case "image":
                imageRef = ImageField.ImageRef(pb_field.image.fileName, UUID(pb_field.image.id))
                imageField = ImageField(property_id=UUID(pb_field.propertyId), image_ref=imageRef)
                setattr(row, "_" + attribute_name, imageField)
            case "locations":
                locationField = LocationField(property_id=UUID(pb_field.propertyId))
                for point in pb_field.locations.elements:
                    locationField.add_point(point.name, point.latitude, point.longitude, point.address)
                setattr(row, "_" + attribute_name, locationField)
            case "members":
                if flag_type is None:
                    raise LookupError("Flag type not set")
                flagValue = reduce(lambda r, m: r | 2**(m - 1),
                                   pb_field.members.elements, 0)
                setattr(row, attribute_name, flag_type(flagValue))
            case "rowReferences" if pb_field.multi:
                values: List[UUID] = []
                for row_reference in pb_field.rowReferences.elements:
                    values.append(UUID(row_reference))
                setattr(row, attribute_name, values)
            case "rowReferences":
                value = next(iter(pb_field.rowReferences.elements), None)
                setattr(row, attribute_name, UUID(value))
            case _:
                pass

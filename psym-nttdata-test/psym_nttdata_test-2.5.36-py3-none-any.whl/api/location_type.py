#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Iterator, List, Mapping, Optional

from psym._utils import (
    get_graphql_property_type_inputs,
    get_graphql_document_category_inputs,
)
from psym.client import SymphonyClient
from psym.common.cache import LOCATION_TYPES
from psym.common.data_class import (
    Location,
    LocationType,
    PropertyDefinition,
    PropertyValue,
    DocumentCategory,
)
from psym.common.data_enum import Entity
from psym.common.data_format import (
    format_to_document_category_inputs,
    format_to_location_type,
    format_to_property_type_inputs,
)

from ..exceptions import EntityNotFoundError
from ..graphql.input.add_location_type_input import AddLocationTypeInput
from ..graphql.input.edit_location_type_input import EditLocationTypeInput
from ..graphql.mutation.add_location_type import AddLocationTypeMutation
from ..graphql.mutation.edit_location_type import EditLocationTypeMutation
from ..graphql.mutation.remove_location_type import RemoveLocationTypeMutation
from ..graphql.query.location_type_details import LocationTypeDetailsQuery
from ..graphql.query.location_type_locations import LocationTypeLocationsQuery
from ..graphql.query.location_types import LocationTypesQuery
from .location import delete_location


def _populate_location_types(client: SymphonyClient) -> None:
    location_types = LocationTypesQuery.execute(client)
    if not location_types:
        return
    edges = location_types.edges
    for edge in edges:
        node = edge.node
        if node:
            LOCATION_TYPES[node.name] = format_to_location_type(
                location_type_fragment=node
            )


def add_location_type(
    client: SymphonyClient,
    name: str,
    properties: List[PropertyDefinition],
    map_type: Optional[str] = None,
    map_zoom_level: int = 8,
    is_site: bool = False,
    document_categories: List[DocumentCategory] = None,
) -> LocationType:
    """This function creates new location type.

    :param name: Location type name
    :type name: str
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param document_categories: List of documents category
    :type document_categories: List[ :class:`~psym.common.data_class.DocumentCategory` ]
    :param map_type: Map type
    :type map_type: str, optional
    :param map_zoom_level: Map zoom level
    :type map_zoom_level: int
    :param is_site: Is site flag
    :type is_site: bool

    :raises:
        FailedOperationException: Internal symphony error

    :return: LocationType object
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        location_type = client.add_location_type(
            name="city",
            properties=[
                PropertyDefinition(
                    property_name="Contact",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=False
                )
            ],
            document_categories=[
                DocumentCategory(
                    index=0,
                    name="DATAFILLS"
                ),
                DocumentCategory(
                    index=1,
                    name="TOPOLOGIA"
                ),
            ],
            map_zoom_level=5,
        )
    """
    new_property_types = format_to_property_type_inputs(data=properties)
    new_document_categories = format_to_document_category_inputs(
        document_category_list=document_categories
    )

    result = AddLocationTypeMutation.execute(
        client,
        AddLocationTypeInput(
            name=name,
            mapZoomLevel=map_zoom_level,
            mapType=map_type if map_type else None,
            isSite=is_site,
            properties=new_property_types,
            documentCategories=new_document_categories,
            surveyTemplateCategories=[],
        ),
    )

    location_type = format_to_location_type(location_type_fragment=result)
    LOCATION_TYPES[result.name] = location_type
    return location_type


def add_property_types_to_location_type(
    client: SymphonyClient,
    location_type_id: str,
    new_properties: List[PropertyDefinition],
) -> LocationType:
    """This function adds new property types to existing location type.

    :param location_type_id: Existing location type ID
    :type location_type_id: str
    :param new_properties: List of property definitions
    :type new_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :raises:
        FailedOperationException: Internal symphony error

    :return: LocationType object
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        location_type = client.add_property_types_to_location_type(
            location_type_id="12345678",
            new_properties=[
                PropertyDefinition(
                    property_name="Contact",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=True
                )
            ],
        )
    """
    location_type = get_location_type_by_id(client=client, id=location_type_id)
    new_property_type_inputs = format_to_property_type_inputs(data=new_properties)
    new_document_categories = format_to_document_category_inputs(
        document_category_list = location_type.document_categories
    )
    result = EditLocationTypeMutation.execute(
        client,
        EditLocationTypeInput(
            id=location_type.id,
            name=location_type.name,
            mapType=location_type.map_type,
            mapZoomLevel=location_type.map_zoom_level,
            isSite=location_type.is_site,
            properties=new_property_type_inputs,
            documentCategories=new_document_categories,
        ),
    )
    edited = format_to_location_type(location_type_fragment=result)
    LOCATION_TYPES.pop(location_type.name)
    LOCATION_TYPES[edited.name] = edited
    return edited


def edit_location_type(
    client: SymphonyClient,
    location_type_id: str,
    new_name: Optional[str] = None,
    new_properties_defaults: Optional[Mapping[str, PropertyValue]] = None,
    new_map_type: Optional[str] = None,
    new_map_zoom_level: Optional[int] = 8,
    new_is_site: Optional[bool] = False,
    new_document_categories: Optional[List[DocumentCategory]] = None,
) -> LocationType:
    """This function edits existing LocationType.

    :param location_type_id: Existing location type ID
    :type location_type_id: str
    :param new_name: Location type new name
    :type new_name: str, optional
    :param new_properties_defaults: Mapping of property name to property default value

        * str - property name
        * PropertyValue - new default value of the same type for this property

    :type new_properties_defaults: Mapping[str, PropertyValue], optional
    :param map_type: New map type
    :type map_type: str, optional
    :param map_zoom_level: New map zoom level
    :type map_zoom_level: int, optional
    :param new_is_site: New is site flag
    :type new_is_site: bool, optional
    :param new_document_categories: List of documents category
    :type new_document_categories: List[ :class:`~psym.common.data_class.DocumentCategory` ]

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Location type does not exist

    :return: LocationType
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        edited_location_type = client.edit_location_type(
            location_type_id="12345678,
            new_name="New name",
            new_description="New description",
            new_properties_defaults = {
                "CONTACT": "ALEN",
                "DATE": date(2021, 9, 1),
                "DATETIME": datetime(2021, 11, 28, 23, 55)
            },
            document_categories= {
                "DATAFILLS": "NEW_DATAFILLS",
                "TOPOLOGIA": "NEW_TOPOLOGIA"
            }
        )
    """
    location_type = get_location_type_by_id(client=client, id=location_type_id)
    new_name = location_type.name if new_name is None else new_name

    new_property_type_inputs = []
    if new_properties_defaults:
        property_types = location_type.property_types
        new_property_type_inputs = get_graphql_property_type_inputs(
            property_types, new_properties_defaults
        )

    new_document_categories_inputs = []
    if new_document_categories:
        new_document_categories_inputs = get_graphql_document_category_inputs(
            location_type.document_categories, new_document_categories
        )

    result = EditLocationTypeMutation.execute(
        client,
        EditLocationTypeInput(
            id=location_type.id,
            name=new_name,
            mapType=new_map_type,
            mapZoomLevel=new_map_zoom_level,
            isSite=new_is_site,
            properties=new_property_type_inputs,
            documentCategories=new_document_categories_inputs,
        ),
    )
    edited = format_to_location_type(location_type_fragment=result)
    LOCATION_TYPES.pop(location_type.name)
    LOCATION_TYPES[edited.name] = edited
    return edited


def get_location_types(client: SymphonyClient) -> Iterator[LocationType]:
    """Get the iterator of location types

    :raises:
        FailedOperationException: Internal symphony error

    :return: LocationType Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.LocationType` ]

    **Example**

    .. code-block:: python

        location_types = client.get_location_types()
        for location_type in location_types:
            print(location_type.name)
    """
    result = LocationTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_location_type(location_type_fragment=node)


def get_location_type_by_id(client: SymphonyClient, id: str) -> LocationType:
    """This function gets existing LocationType by its ID.

    :param id: Location type ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Location type does not exist

    :return: Location type
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        client.get_location_type_by_id(id="12345678")
    """
    result = LocationTypeDetailsQuery.execute(client, id=id)

    if result is None:
        raise EntityNotFoundError(entity=Entity.WorkOrderType, entity_id=id)

    return format_to_location_type(location_type_fragment=result)


def get_location_type_by_name(client: SymphonyClient, name: str) -> LocationType:
    """This function gets existing LocationType by its name.

    :param name: Location type name
    :type name: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Location type does not exist

    :return: Location type
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        client.get_location_type_by_name(name="COUNTRY")
    """
    all_location_types = get_location_types(client)
    location_type_searched = None
    for item in all_location_types:
        if item.name == name:
            location_type_searched = item
            break

    if location_type_searched is None:
        raise EntityNotFoundError(entity=Entity.LocationType, entity_name=name)

    return location_type_searched


def delete_locations_by_location_type(
    client: SymphonyClient, location_type: LocationType
) -> None:
    """Delete locatons by location type.

    :param location_type: LocationType object
    :type location_type: :class:`~psym.common.data_class.LocationType`

    :raises:
        `psym.exceptions.EntityNotFoundError`: `location_type` does not exist

    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_locations_by_location_type(location_type=location_type)
    """
    location_type_with_locations = LocationTypeLocationsQuery.execute(
        client, id=location_type.id
    )
    if location_type_with_locations is None:
        raise EntityNotFoundError(
            entity=Entity.LocationType, entity_id=location_type.id
        )
    locations = location_type_with_locations.locations
    if locations is None:
        return
    for location in locations.edges:
        node = location.node
        if node:
            delete_location(
                client,
                Location(
                    id=node.id,
                    name=node.name,
                    latitude=node.latitude,
                    longitude=node.longitude,
                    external_id=node.externalId,
                    location_type_name=node.locationType.name,
                    properties=node.properties,
                ),
            )


def delete_location_type_with_locations(
    client: SymphonyClient, location_type: LocationType
) -> None:
    """Delete locaton type with existing locations.

    :param location_type: LocationType object
    :type location_type: :class:`~psym.common.data_class.LocationType`

    :raises:
        `psym.exceptions.EntityNotFoundError`: `location_type` does not exist

    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_location_type_with_locations(location_type=location_type)
    """
    delete_locations_by_location_type(client, location_type)
    delete_location_type(client, location_type_id=location_type.id)


def delete_location_type(client: SymphonyClient, location_type_id: str) -> None:
    """This function deletes LocatoinType.

    :param location_type_id: Location type ID
    :type location_type_id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Location type does not exist

    **Example**

    .. code-block:: python

        client.delete_location_type(
            location_type_id="12345678"
        )
    """
    location_type = get_location_type_by_id(client=client, id=location_type_id)
    if location_type is None:
        raise EntityNotFoundError(
            entity=Entity.LocationType, entity_id=location_type_id
        )
    RemoveLocationTypeMutation.execute(client, id=location_type_id)
    del LOCATION_TYPES[location_type.name]

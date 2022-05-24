#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Dict, Iterator, List, Optional

from psym.client import SymphonyClient
from psym.common.cache import PORT_TYPES
from psym.common.data_class import EquipmentPortType, PropertyDefinition, PropertyValue
from psym.common.data_enum import Entity
from psym.common.data_format import (
    format_to_equipment_port_type,
    format_to_property_type_inputs,
)

from .._utils import get_graphql_property_type_inputs
from ..exceptions import EntityNotFoundError
from ..graphql.input.add_equipment_port_type_input import AddEquipmentPortTypeInput
from ..graphql.input.edit_equipment_port_type_input import EditEquipmentPortTypeInput
from ..graphql.mutation.add_equipment_port_type import AddEquipmentPortTypeMutation
from ..graphql.mutation.edit_equipment_port_type import EditEquipmentPortTypeMutation
from ..graphql.mutation.remove_equipment_port_type import (
    RemoveEquipmentPortTypeMutation,
)
from ..graphql.query.equipment_port_type import EquipmentPortTypeQuery
from ..graphql.query.equipment_port_types import EquipmentPortTypesQuery


def _populate_equipment_port_types(client: SymphonyClient) -> None:
    edges = EquipmentPortTypesQuery.execute(client).edges

    for edge in edges:
        node = edge.node
        if node:
            PORT_TYPES[node.name] = format_to_equipment_port_type(
                equipment_port_type_fragment=node
            )


def add_equipment_port_type(
    client: SymphonyClient,
    name: str,
    properties: List[PropertyDefinition],
    link_properties: List[PropertyDefinition],
) -> EquipmentPortType:
    """This function creates an equipment port type.

    :param name: Equipment port type name
    :type name: str
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ])
    :param link_properties: List of property definitions
    :type link_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ])

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentPortType object
    :rtype: :class:`~psym.common.data_class.EquipmentPortType`

    **Example**

    .. code-block:: python

        from psym.common.data_class import PropertyDefinition
        from psym.graphql.enum.property_kind import PropertyKind
        port_type1 = client.add_equipment_port_type(
            name="port type 1",
            properties=[
                PropertyDefinition(
                    property_name="port property",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=True
                )
            ],
            link_properties=[
                PropertyDefinition(
                    property_name="link port property",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=True
                )
            ],
        )
    """

    formated_property_types = format_to_property_type_inputs(data=properties)
    formated_link_property_types = format_to_property_type_inputs(data=link_properties)
    result = AddEquipmentPortTypeMutation.execute(
        client,
        AddEquipmentPortTypeInput(
            name=name,
            properties=formated_property_types,
            linkProperties=formated_link_property_types,
        ),
    )

    added = format_to_equipment_port_type(equipment_port_type_fragment=result)
    PORT_TYPES[added.name] = added
    return added


def get_equipment_port_type(
    client: SymphonyClient, equipment_port_type_id: str
) -> EquipmentPortType:
    """This function returns an equipment port type.
    It gets the requested equipment port type ID

    :param equipment_port_type_id: Equipment port type ID
    :type equipment_port_type_id: str

    :raises:
        :class:`~psym.exceptions.EntityNotFoundError`: Equipment port type does not found

    :return: EquipmentPortType object
    :rtype: :class:`~psym.common.data_class.EquipmentPortType`

    **Example**

    .. code-block:: python

        port_type = client.get_equipment_port_type(equipment_port_type_id=port_type1.id)
    """
    result = EquipmentPortTypeQuery.execute(client, id=equipment_port_type_id)
    if not result:
        raise EntityNotFoundError(
            entity=Entity.EquipmentPortType, entity_id=equipment_port_type_id
        )

    return format_to_equipment_port_type(equipment_port_type_fragment=result)


def get_equipment_port_types(client: SymphonyClient) -> Iterator[EquipmentPortType]:
    """Get the iterator of equipment port types

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentPortType Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.EquipmentPortType` ]

    **Example**

    .. code-block:: python

        equipment_port_types = client.get_equipment_port_types()
        for equipment_port_type in equipment_port_types:
            print(equipment_port_type.name)
    """
    result = EquipmentPortTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_equipment_port_type(equipment_port_type_fragment=node)


def edit_equipment_port_type(
    client: SymphonyClient,
    port_type: EquipmentPortType,
    new_name: Optional[str] = None,
    new_properties: Optional[Dict[str, PropertyValue]] = None,
    new_link_properties: Optional[Dict[str, PropertyValue]] = None,
) -> EquipmentPortType:
    """This function edits an existing equipment port type.

    :param port_type: Existing eqipment port type object
    :type port_type: :class:`~psym.common.data_class.EquipmentPortType`
    :param new_name: New name
    :type new_name: str
    :param new_properties: Dictionary of property name to property value

        * str - property name
        * PropertyValue - new value of the same type for this property

    :type new_properties: Dict[str, PropertyValue], optional
    :param new_link_properties: Dictionary of property name to property value

        * str - property name
        * PropertyValue - new value of the same type for this property

    :type new_link_properties: Dict[str, PropertyValue], optional

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentPortType object
    :rtype: :class:`~psym.common.data_class.EquipmentPortType`

    **Example**

    .. code-block:: python

        port_type1 = client.edit_equipment_port_type(
            port_type=equipment_port_type,
            new_name="new port type name",
            new_properties={"existing property name": "new value"},
            new_link_properties={"existing link property name": "new value"},
        )
    """
    new_name = port_type.name if new_name is None else new_name

    new_property_type_inputs = []
    if new_properties:
        property_types = PORT_TYPES[port_type.name].property_types
        new_property_type_inputs = get_graphql_property_type_inputs(
            property_types, new_properties
        )

    new_link_property_type_inputs = []
    if new_link_properties:
        link_property_types = PORT_TYPES[port_type.name].link_property_types
        new_link_property_type_inputs = get_graphql_property_type_inputs(
            link_property_types, new_link_properties
        )

    result = EditEquipmentPortTypeMutation.execute(
        client,
        EditEquipmentPortTypeInput(
            id=port_type.id,
            name=new_name,
            properties=new_property_type_inputs,
            linkProperties=new_link_property_type_inputs,
        ),
    )
    edited = format_to_equipment_port_type(equipment_port_type_fragment=result)
    PORT_TYPES.pop(port_type.name)
    PORT_TYPES[edited.name] = edited
    return edited


def delete_equipment_port_type(
    client: SymphonyClient, equipment_port_type_id: str
) -> None:
    """This function deletes an equipment port type.
    It gets the requested equipment port type ID

    :param equipment_port_type_id: Equipment port type ID
    :type equipment_port_type_id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Equipment port type does not exist

    **Example**

    .. code-block:: python

        client.delete_equipment_port_type(
            equipment_port_type_id="12345678"
        )
    """
    port_type = get_equipment_port_type(
        client=client, equipment_port_type_id=equipment_port_type_id
    )
    if port_type is None:
        raise EntityNotFoundError(
            entity=Entity.EquipmentPortType, entity_id=equipment_port_type_id
        )
    RemoveEquipmentPortTypeMutation.execute(client, id=equipment_port_type_id)
    del PORT_TYPES[port_type.name]

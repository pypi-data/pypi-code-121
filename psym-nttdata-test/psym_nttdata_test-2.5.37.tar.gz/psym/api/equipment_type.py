#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Iterator, List, Mapping, Optional

from psym.client import SymphonyClient
from psym.common.cache import EQUIPMENT_TYPES, PORT_TYPES
from psym.common.data_class import (
    EquipmentPortDefinition,
    EquipmentType,
    PropertyDefinition,
    PropertyValue,
)
from psym.common.data_enum import Entity
from psym.common.data_format import (
    format_to_equipment,
    format_to_equipment_type,
    format_to_property_type_input,
    format_to_property_type_inputs,
)

from .._utils import (
    get_graphql_property_type_inputs,
    get_port_definition_input,
    get_position_definition_input,
)
from ..exceptions import EntityNotFoundError
from ..graphql.input.add_equipment_type_input import AddEquipmentTypeInput
from ..graphql.input.edit_equipment_type_input import EditEquipmentTypeInput
from ..graphql.input.equipment_port_input import EquipmentPortInput
from ..graphql.input.equipment_position_input import EquipmentPositionInput
from ..graphql.input.property_type_input import PropertyTypeInput
from ..graphql.mutation.add_equipment_type import AddEquipmentTypeMutation
from ..graphql.mutation.edit_equipment_type import EditEquipmentTypeMutation
from ..graphql.mutation.remove_equipment_type import RemoveEquipmentTypeMutation
from ..graphql.query.equipment_type_details import EquipmentTypeDetailsQuery
from ..graphql.query.equipment_type_equipments import EquipmentTypeEquipmentQuery
from ..graphql.query.equipment_types import EquipmentTypesQuery
from ..graphql.input.equipment_port_connection_input import EquipmentPortConnectionInput
from .equipment import delete_equipment
from .property_type import (
    edit_property_type,
    get_property_type,
    get_property_type_by_external_id,
)


def _populate_equipment_types(client: SymphonyClient) -> None:
    edges = EquipmentTypesQuery.execute(client).edges

    for edge in edges:
        node = edge.node
        if node:
            EQUIPMENT_TYPES[node.name] = format_to_equipment_type(
                equipment_type_fragment=node
            )


def _add_equipment_type(
    client: SymphonyClient,
    name: str,
    category: Optional[str],
    properties: List[PropertyTypeInput],
    position_definitions: List[EquipmentPositionInput],
    port_definitions: List[EquipmentPortInput],
) -> AddEquipmentTypeMutation.AddEquipmentTypeMutationData.EquipmentType:
    return AddEquipmentTypeMutation.execute(
        client,
        AddEquipmentTypeInput(
            name=name,
            category=category,
            positions=position_definitions,
            ports=port_definitions,
            properties=properties,
        ),
    )


def get_or_create_equipment_type(
    client: SymphonyClient,
    name: str,
    category: str,
    properties: List[PropertyDefinition],
    port_definitions: List[EquipmentPortDefinition],
    position_list: List[str],
) -> EquipmentType:
    """This function checks equipment type existence,
    in case it is not found, creates one.

    :param name: Equipment type name
    :type name: str
    :param category: Category name
    :type category: str
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param port_definitions: EquipmentPortDefinitions list
    :type port_definitions: List[ :class:`~psym.common.data_class.EquipmentPortDefinition` ]
    :param position_list: List of positions names
    :type position_list: List[str]

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        e_type = client.get_or_create_equipment_type(
            name="Tp-Link T1600G",
            category="Router",
            properties=[
                PropertyDefinition(
                    property_name="IP",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=True
                )
            ],
            port_definitions=[
                EquipmentPortDefinition(
                    name="tp_link_port",
                    visible_label="TP-Link port",
                    port_definition_index=0,
                    port_type_name="port type 1",
                )
            ],
            position_list=[],
        )
    """
    if name in EQUIPMENT_TYPES:
        return EQUIPMENT_TYPES[name]
    return add_equipment_type(
        client, name, category, properties, port_definitions, position_list
    )


def _edit_equipment_type(
    client: SymphonyClient,
    equipment_type_id: str,
    name: str,
    category: Optional[str],
    properties: List[PropertyTypeInput],
    position_definitions: List[EquipmentPositionInput],
    port_definitions: List[EquipmentPortInput],
) -> EditEquipmentTypeMutation.EditEquipmentTypeMutationData.EquipmentType:
    return EditEquipmentTypeMutation.execute(
        client,
        EditEquipmentTypeInput(
            id=equipment_type_id,
            name=name,
            category=category,
            positions=position_definitions,
            ports=port_definitions,
            properties=properties,
        ),
    )


def _update_equipment_type(
    client: SymphonyClient,
    equipment_type_id: str,
    name: str,
    category: Optional[str],
    properties: List[PropertyTypeInput],
    position_definitions: List[EquipmentPositionInput],
    port_definitions: List[EquipmentPortInput],
) -> EquipmentType:

    equipment_type_result = _edit_equipment_type(
        client=client,
        equipment_type_id=equipment_type_id,
        name=name,
        category=category,
        properties=properties,
        position_definitions=position_definitions,
        port_definitions=port_definitions,
    )
    equipment_type = format_to_equipment_type(
        equipment_type_fragment=equipment_type_result
    )
    EQUIPMENT_TYPES[name] = equipment_type
    return equipment_type


def add_equipment_type(
    client: SymphonyClient,
    name: str,
    category: str,
    properties: List[PropertyDefinition],
    port_definitions: List[EquipmentPortDefinition],
    position_list: List[str],
) -> EquipmentType:
    """This function creates new equipment type.

    :param name: Equipment type name
    :type name: str
    :param category: Category name
    :type category: str
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param port_definitions: EquipmentPortDefinitions list
    :type port_definitions: List[ :class:`~psym.common.data_class.EquipmentPortDefinition` ]
    :param position_list: List of positions names
    :type position_list: List[str]

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        e_type = client.add_equipment_type(
            name="Tp-Link T1600G",
            category="Router",
            properties=[
                PropertyDefinition(
                    property_name="IP",
                    property_kind=PropertyKind.string,
                    default_raw_value=None,
                    is_fixed=True
                )
            ],
            port_definitions=[
                EquipmentPortDefinition(
                    name="tp_link_port",
                    visible_label="TP-Link port",
                    port_definition_index=0,
                    port_type_name="port type 1",
                )
            ],
            position_list=[],
        )
    """
    new_property_types = format_to_property_type_inputs(data=properties)
    new_port_definitions = [
        EquipmentPortInput(
            name=pd.name,
            index=pd.port_definition_index,
            visibleLabel=pd.visible_label,
            portTypeID=PORT_TYPES[pd.port_type_name].id if pd.port_type_name else None,
            connectedPorts=[
                EquipmentPortConnectionInput(id=cp.id, name=cp.name)
                for cp in pd.connected_ports
            ],
        )
        for pd in port_definitions
    ]
    position_definitions = [
        EquipmentPositionInput(name=position) for position in position_list
    ]
    equipment_type_result = _add_equipment_type(
        client,
        name,
        category,
        new_property_types,
        position_definitions,
        new_port_definitions,
    )
    equipment_type = format_to_equipment_type(
        equipment_type_fragment=equipment_type_result
    )
    EQUIPMENT_TYPES[name] = equipment_type
    return equipment_type


def add_property_types_to_equipment_type(
    client: SymphonyClient,
    equipment_type_id: str,
    new_properties: List[PropertyDefinition],
) -> EquipmentType:
    """This function adds new property types to existing equipment type.

    :param equipment_type_id: Existing equipment type ID
    :type equipment_type_id: str
    :param new_properties: List of property definitions
    :type new_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        equipment_type = client.add_property_types_to_equipment_type(
            equipment_type_id="12345678",
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
    equipment_type = get_equipment_type_by_id(
        client=client, equipment_type_id=equipment_type_id
    )
    new_property_type_inputs = format_to_property_type_inputs(data=new_properties)

    position_definitions = [
        get_position_definition_input(position_definition, is_new=False)
        for position_definition in equipment_type.position_definitions
    ]
    port_definitions = [
        get_port_definition_input(port_definition, is_new=False)
        for port_definition in equipment_type.port_definitions
    ]

    return _update_equipment_type(
        client=client,
        equipment_type_id=equipment_type.id,
        name=equipment_type.name,
        category=equipment_type.category,
        properties=new_property_type_inputs,
        position_definitions=position_definitions,
        port_definitions=port_definitions,
    )


def edit_equipment_type(
    client: SymphonyClient,
    name: str,
    new_positions_list: List[str],
    new_port_definitions: List[EquipmentPortDefinition],
    new_properties: Optional[Mapping[str, PropertyValue]] = None,
) -> EquipmentType:
    """Edit existing equipment type.

    :param name: Equipment type name
    :type name: str
    :param new_positions_list: List of new positions
    :type new_positions_list: List[str]
    :param new_port_definitions: EquipmentPortDefinitions list
    :type new_port_definitions: List[ :class:`~psym.common.data_class.EquipmentPortDefinition` ]
    :param new_properties: Property definitions list
    :type new_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ], optional

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        edited_equipment = client.edit_equipment_type(
            name="Card",
            new_positions_list=[],
            new_port_definitions=[
                EquipmentPortDefinition(
                    name="tp_link_port",
                    visible_label="TP-Link port",
                    port_definition_index=0,
                    port_type_name="port type 1",
                )
            ],
        )
    """
    equipment_type = EQUIPMENT_TYPES[name]
    position_definitions = [
        get_position_definition_input(position_definition, is_new=False)
        for position_definition in equipment_type.position_definitions
    ] + [EquipmentPositionInput(name=position) for position in new_positions_list]
    port_definitions = [
        get_port_definition_input(port_definition, is_new=False)
        for port_definition in equipment_type.port_definitions
    ] + [
        EquipmentPortInput(
            name=pd.name,
            index=pd.port_definition_index,
            visibleLabel=pd.visible_label,
            portTypeID=PORT_TYPES[pd.port_type_name].id if pd.port_type_name else None,
            connectedPorts=[
                EquipmentPortConnectionInput(id=cp.id, name=cp.name)
                for cp in pd.connected_ports
            ],
        )
        for pd in new_port_definitions
    ]
    new_property_type_inputs = []
    if new_properties:
        property_types = PORT_TYPES[equipment_type.name].property_types
        new_property_type_inputs = get_graphql_property_type_inputs(
            property_types, new_properties
        )

    return _update_equipment_type(
        client=client,
        equipment_type_id=equipment_type.id,
        name=equipment_type.name,
        category=equipment_type.category,
        properties=new_property_type_inputs,
        position_definitions=position_definitions,
        port_definitions=port_definitions,
    )


def get_equipment_type_by_id(
    client: SymphonyClient, equipment_type_id: str
) -> EquipmentType:
    """This function returns an equipment type.
    It gets the requested equipment type ID

    :param equipment_type_id: Equipment type ID
    :type equipment_type_id: str

    :raises:
        :class:`~psym.exceptions.EntityNotFoundError`: Equipment type does not found

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        equipment_type = client.get_equipment_type_by_id(equipment_type_id="12345678)
    """
    result = EquipmentTypeDetailsQuery.execute(client, id=equipment_type_id)
    if not result:
        raise EntityNotFoundError(
            entity=Entity.EquipmentType, entity_id=equipment_type_id
        )

    return format_to_equipment_type(equipment_type_fragment=result)


def get_equipment_types(client: SymphonyClient) -> Iterator[EquipmentType]:
    """Get the iterator of equipment types

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.EquipmentType` ]

    **Example**

    .. code-block:: python

        equipment_types = client.get_equipment_types()
        for equipment_type in equipment_types:
            print(equipment_type.name)
    """
    result = EquipmentTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_equipment_type(equipment_type_fragment=node)


def copy_equipment_type(
    client: SymphonyClient, curr_equipment_type_name: str, new_equipment_type_name: str
) -> EquipmentType:
    """Copy existing equipment type.

    :param curr_equipment_type_name: Existing equipment type name
    :type curr_equipment_type_name: str
    :param new_equipment_type_name: New equipment type name
    :type new_equipment_type_name: str

    :raises:
        FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        e_type = client.copy_equipment_type(
            curr_equipment_type_name="Card",
            new_equipment_type_name="External_Card",
        )
    """
    equipment_type = EQUIPMENT_TYPES[curr_equipment_type_name]

    new_property_types = [
        format_to_property_type_input(property_type)
        for property_type in equipment_type.property_types
    ]

    new_position_definitions = [
        get_position_definition_input(position_definition)
        for position_definition in equipment_type.position_definitions
    ]

    new_port_definitions = [
        get_port_definition_input(port_definition)
        for port_definition in equipment_type.port_definitions
    ]

    equipment_type_result = _add_equipment_type(
        client,
        new_equipment_type_name,
        equipment_type.category,
        new_property_types,
        new_position_definitions,
        new_port_definitions,
    )

    new_equipment_type = format_to_equipment_type(
        equipment_type_fragment=equipment_type_result
    )

    EQUIPMENT_TYPES[new_equipment_type_name] = new_equipment_type
    return new_equipment_type


def get_equipment_type_property_type(
    client: SymphonyClient, equipment_type_name: str, property_type_id: str
) -> PropertyDefinition:
    """Get property type by ID on specific equipment type.

    :param equipment_type_name: Existing equipment type name
    :type equipment_type_name: str
    :param property_type_id: Property type ID
    :type property_type_id: str

    :raises:
        :class:`~psym.exceptions.EntityNotFoundError`: property type with id=`property_type_id` is not found

    :return: PropertyDefinition object
    :rtype: :class:`~psym.common.data_class.PropertyDefinition`

    **Example**

    .. code-block:: python

        property_type = client.get_equipment_type_property_type(
            equipment_type_name="Card",
            property_type_id="12345",
        )
    """
    return get_property_type(
        client=client,
        entity_type=Entity.EquipmentType,
        entity_name=equipment_type_name,
        property_type_id=property_type_id,
    )


def get_equipment_type_property_type_by_external_id(
    client: SymphonyClient, equipment_type_name: str, property_type_external_id: str
) -> PropertyDefinition:
    """Get property type by external ID on specific equipment type.

    :param equipment_type_name: Existing equipment type name
    :type equipment_type_name: str
    :param property_type_external_id: Property type external ID
    :type property_type_external_id: str

    :raises:
        :class:`~psym.exceptions.EntityNotFoundError`: property type with external_id=`property_type_external_id` is not found

    :return: PropertyDefinition object
    :rtype: :class:`~psym.common.data_class.PropertyDefinition`

    **Example**

    .. code-block:: python

        property_type = client.get_equipment_type_property_type_by_external_id(
            equipment_type_name="Card",
            property_type_external_id="12345",
        )
    """
    return get_property_type_by_external_id(
        client=client,
        entity_type=Entity.EquipmentType,
        entity_name=equipment_type_name,
        property_type_external_id=property_type_external_id,
    )


def edit_equipment_type_property_type(
    client: SymphonyClient,
    equipment_type_name: str,
    property_type_id: str,
    new_property_definition: PropertyDefinition,
) -> EquipmentType:
    """Edit specific property type on specific equipment type.


    :param equipment_type_name: Existing equipment type name
    :type equipment_type_name: str
    :param property_type_id: Existing property type ID
    :type property_type_id: str
    :param new_property_definition: New property definition
    :type new_property_definition: :class:`~psym.common.data_class.PropertyDefinition`

    :raises:
        * :class:`~psym.exceptions.EntityNotFoundError`: if property type name is not found
        * FailedOperationException: Internal symphony error

    :return: EquipmentType object
    :rtype: :class:`~psym.common.data_class.EquipmentType`

    **Example**

    .. code-block:: python

        e_type = client.edit_equipment_type_property_type(
            equipment_type_name="Card",
            property_type_id="111669149698",
            new_property_definition=PropertyDefinition(
                property_name=property_type_name,
                property_kind=PropertyKind.string,
                default_raw_value=None,
                is_fixed=False,
                external_id="12345",
            ),
        )
    """
    equipment_type = EQUIPMENT_TYPES[equipment_type_name]
    edited_property_types = edit_property_type(
        client=client,
        entity_type=Entity.EquipmentType,
        entity_name=equipment_type_name,
        property_type_id=property_type_id,
        new_property_definition=new_property_definition,
    )
    position_definitions = [
        get_position_definition_input(position_definition, is_new=False)
        for position_definition in equipment_type.position_definitions
        if equipment_type.position_definitions
    ]
    port_definitions = [
        get_port_definition_input(port_definition, is_new=False)
        for port_definition in equipment_type.port_definitions
        if equipment_type.port_definitions
    ]

    return _update_equipment_type(
        client=client,
        equipment_type_id=equipment_type.id,
        name=equipment_type.name,
        category=equipment_type.category,
        properties=edited_property_types,
        position_definitions=position_definitions,
        port_definitions=port_definitions,
    )


def delete_equipment_type_with_equipments(
    client: SymphonyClient, equipment_type: EquipmentType
) -> None:
    """Delete equipment type with existing equipments.

    :param equipment_type: Existing equipment type name
    :type equipment_type: :class:`~psym.common.data_class.EquipmentType`

    :raises:
        :class:`~psym.exceptions.EntityNotFoundError`: if equipment_type does not exist

    :return: None

    **Example**

    .. code-block:: python

        equipment_type = client.get_or_create_equipment_type(
            name="Tp-Link T1600G",
            category="Router",
            properties=[
                ("IP", "string", None, True),
            ],
            ports_dict={
                "Port 1": "eth port",
                "port 2": "eth port",
            },
            position_list=[],
        )
        client.delete_equipment_type_with_equipments(equipment_type=equipment_type)
    """
    equipment_type_with_equipments = EquipmentTypeEquipmentQuery.execute(
        client, id=equipment_type.id
    )
    if not equipment_type_with_equipments:
        raise EntityNotFoundError(
            entity=Entity.EquipmentType, entity_id=equipment_type.id
        )
    for equipment in equipment_type_with_equipments.equipments:
        delete_equipment(client, format_to_equipment(equipment_fragment=equipment))

    delete_equipment_type(client=client, equipment_type_id=equipment_type.id)


def delete_equipment_type(client: SymphonyClient, equipment_type_id: str) -> None:
    """This function deletes an equipment type.
    It gets the requested equipment type ID

    :param equipment_type_id: Equipment type ID
    :type equipment_type_id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Equipment type does not exist

    **Example**

    .. code-block:: python

        client.delete_equipment_type(
            equipment_type_id="12345678"
        )
    """
    equipment_type = get_equipment_type_by_id(
        client=client, equipment_type_id=equipment_type_id
    )
    if equipment_type is None:
        raise EntityNotFoundError(
            entity=Entity.EquipmentType, entity_id=equipment_type_id
        )
    RemoveEquipmentTypeMutation.execute(client, id=equipment_type_id)
    del EQUIPMENT_TYPES[equipment_type.name]

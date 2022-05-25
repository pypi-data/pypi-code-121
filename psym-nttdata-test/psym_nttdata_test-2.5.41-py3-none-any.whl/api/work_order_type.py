#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Iterator, List, Mapping, Optional

from psym._utils import get_graphql_property_type_inputs
from psym.client import SymphonyClient
from psym.common.cache import WORK_ORDER_TYPES
from psym.common.data_class import PropertyDefinition, PropertyValue, WorkOrderType
from psym.common.data_enum import Entity
from psym.common.data_format import (
    format_to_property_type_inputs,
    format_to_work_order_type,
)
from psym.exceptions import EntityNotFoundError

from ..graphql.input.add_work_order_type_input import AddWorkOrderTypeInput
from ..graphql.input.edit_work_order_type_input import EditWorkOrderTypeInput
from ..graphql.mutation.add_work_order_type import AddWorkOrderTypeMutation
from ..graphql.mutation.edit_work_order_type import EditWorkOrderTypeMutation
from ..graphql.mutation.remove_work_order_type import RemoveWorkOrderTypeMutation
from ..graphql.query.work_order_type_details import WorkOrderTypeDetailsQuery
from ..graphql.query.work_order_types import WorkOrderTypesQuery


def _populate_work_order_types(client: SymphonyClient) -> None:
    edges = WorkOrderTypesQuery.execute(client).edges

    for edge in edges:
        node = edge.node
        if node:
            WORK_ORDER_TYPES[node.name] = format_to_work_order_type(
                work_order_type_fragment=node
            )


def add_work_order_type(
    client: SymphonyClient,
    name: str,
    description: Optional[str] = None,
    properties: List[PropertyDefinition] = None,
) -> WorkOrderType:
    """This function creates WorkOrderType.

    :param name: Work order type name
    :type name: str
    :param description: Work order type description
    :type description: str, optional
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :return: Work order type
    :rtype: :class:`~psym.common.data_class.WorkOrderType`

    **Example**

    .. code-block:: python

        client.add_work_order_type(
            name="Work order type",
            description="Work order type description",
            properties=[
                PropertyDefinition(
                    property_name="work order type property",
                    property_kind=PropertyKind.string,
                    default_raw_value="string value",
                    is_fixed=False,
                )
            ],
        )
    """
    property_type_inputs = []
    if properties is not None:
        property_type_inputs = format_to_property_type_inputs(data=properties)
    result = AddWorkOrderTypeMutation.execute(
        client,
        AddWorkOrderTypeInput(
            name=name,
            description=description,
            properties=property_type_inputs,
            checkListCategories=[],
            assigneeCanCompleteWorkOrder=True,
        ),
    )
    added = format_to_work_order_type(work_order_type_fragment=result)
    WORK_ORDER_TYPES[added.name] = added
    return added


def get_work_order_types(client: SymphonyClient) -> Iterator[WorkOrderType]:
    """Get the iterator of work order types

    :raises:
        FailedOperationException: Internal symphony error

    :return: WorkOrderType Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.WorkOrderType` ]

    **Example**

    .. code-block:: python

        work_order_types = client.get_work_order_types()
        for work_order_type in work_order_types:
            print(work_order_type.name, work_order_type.description)
    """
    result = WorkOrderTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_work_order_type(work_order_type_fragment=node)


def get_work_order_type_by_id(client: SymphonyClient, id: str) -> WorkOrderType:
    """This function gets existing WorkOrderType by its ID.

    :param id: Work order type ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order type does not exist

    :return: Work order type
    :rtype: :class:`~psym.common.data_class.WorkOrderType`

    **Example**

    .. code-block:: python

        client.get_work_order_type_by_id(id="12345678")
    """
    result = WorkOrderTypeDetailsQuery.execute(client, id=id)

    if result is None:
        raise EntityNotFoundError(entity=Entity.WorkOrderType, entity_id=id)

    return format_to_work_order_type(work_order_type_fragment=result)


def get_work_order_type_by_name(client: SymphonyClient, name: str) -> WorkOrderType:
    """This function gets existing WorkOrderType by its name.

    :param name: Work order type name
    :type name: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order type does not exist

    :return: Work order type
    :rtype: :class:`~psym.common.data_class.WorkOrderType`

    **Example**

    .. code-block:: python

        client.get_work_order_type_by_name(name="WorkOrderType Name")
    """

    work_order_types = get_work_order_types(client=client)
    for work_order_type in work_order_types:
        if work_order_type.name == name:
            return work_order_type
    raise EntityNotFoundError(entity=Entity.WorkOrderType, entity_name=name)


def add_property_types_to_work_order_type(
    client: SymphonyClient,
    work_order_type_id: str,
    new_properties: List[PropertyDefinition],
) -> WorkOrderType:
    """This function adds new property types to existing work order type.

    :param work_order_type_id: Existing work order type ID
    :type work_order_type_id: str
    :param new_properties: List of property definitions
    :type new_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :raises:
        FailedOperationException: Internal symphony error

    :return: WorkOrderType object
    :rtype: :class:`~psym.common.data_class.WorkOrderType`

    **Example**

    .. code-block:: python

        work_order_type = client.add_property_types_to_work_order_type(
            work_order_type_id="12345678",
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
    work_order_type = get_work_order_type_by_id(client=client, id=work_order_type_id)
    new_property_type_inputs = format_to_property_type_inputs(data=new_properties)
    result = EditWorkOrderTypeMutation.execute(
        client,
        EditWorkOrderTypeInput(
            id=work_order_type.id,
            name=work_order_type.name,
            description=work_order_type.description,
            properties=new_property_type_inputs,
            checkListCategories=[],
        ),
    )
    edited = format_to_work_order_type(work_order_type_fragment=result)
    WORK_ORDER_TYPES.pop(work_order_type.name)
    WORK_ORDER_TYPES[edited.name] = edited
    return edited


def edit_work_order_type(
    client: SymphonyClient,
    work_order_type_id: str,
    new_name: Optional[str] = None,
    new_description: Optional[str] = None,
    new_properties_defaults: Optional[Mapping[str, PropertyValue]] = None,
) -> WorkOrderType:
    """This function edits existing WorkOrderType.

    :param work_order_type_id: Existing work order type ID
    :type work_order_type_id: str
    :param new_name: Work order type new name
    :type new_name: str, optional
    :param new_description: Work order type new description
    :type new_description: str, optional
    :param new_properties_defaults: Mapping of property name to property default value

        * str - property name
        * PropertyValue - new default value of the same type for this property

    :type new_properties_defaults: Mapping[str, PropertyValue], optional

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order type does not exist

    :return: Work order type
    :rtype: :class:`~psym.common.data_class.WorkOrderType`

    **Example**

    .. code-block:: python

        edited_work_order_type = client.edit_work_order_type(
            work_order_type_id="12345678,
            new_name="New name",
            new_description="New description",
        )
    """
    work_order_type = get_work_order_type_by_id(client=client, id=work_order_type_id)
    new_name = work_order_type.name if new_name is None else new_name
    new_description = (
        work_order_type.description if new_description is None else new_description
    )

    new_property_type_inputs = []
    if new_properties_defaults:
        property_types = work_order_type.property_types
        new_property_type_inputs = get_graphql_property_type_inputs(
            property_types, new_properties_defaults
        )
    result = EditWorkOrderTypeMutation.execute(
        client,
        EditWorkOrderTypeInput(
            id=work_order_type.id,
            name=new_name,
            description=new_description,
            properties=new_property_type_inputs,
            checkListCategories=[],
        ),
    )
    edited = format_to_work_order_type(work_order_type_fragment=result)
    WORK_ORDER_TYPES.pop(work_order_type.name)
    WORK_ORDER_TYPES[edited.name] = edited
    return edited


def delete_work_order_type(client: SymphonyClient, work_order_type_id: str) -> None:
    """This function deletes WorkOrderType.

    :param work_order_type_id: Work order type ID
    :type work_order_type_id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order type does not exist

    **Example**

    .. code-block:: python

        client.delete_work_order_type("12345678")
    """
    work_order_type = get_work_order_type_by_id(client=client, id=work_order_type_id)
    if work_order_type is None:
        raise EntityNotFoundError(
            entity=Entity.WorkOrderType, entity_id=work_order_type_id
        )
    RemoveWorkOrderTypeMutation.execute(client, id=work_order_type_id)
    del WORK_ORDER_TYPES[work_order_type.name]

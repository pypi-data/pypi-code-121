#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from datetime import datetime
from typing import Dict, Iterator, Optional

from psym._utils import get_graphql_property_inputs
from psym.client import SymphonyClient
from psym.common.cache import WORK_ORDER_TYPES
from psym.common.data_class import PropertyValue, WorkOrder, WorkOrderType, organization
from psym.common.data_enum import Entity
from psym.common.data_format import format_to_work_order
from psym.exceptions import EntityNotFoundError
from psym.graphql.enum.work_order_priority import WorkOrderPriority
from psym.graphql.enum.work_order_status import WorkOrderStatus
from psym.graphql.input.add_work_order_input import AddWorkOrderInput
from psym.graphql.input.edit_work_order_input import EditWorkOrderInput
from psym.graphql.mutation.add_work_order import AddWorkOrderMutation
from psym.graphql.mutation.edit_work_order import EditWorkOrderMutation
from psym.graphql.mutation.remove_work_order import RemoveWorkOrderMutation
from psym.graphql.query.work_order_details import WorkOrderDetailsQuery
from psym.graphql.query.work_orders import WorkOrdersQuery


def add_work_order(
    client: SymphonyClient,
    name: str,
    work_order_type: WorkOrderType,
    organization: str,
    description: Optional[str] = None,
    location_id: Optional[str] = None,
    project_id: Optional[str] = None,
    properties_dict: Dict[str, PropertyValue] = {},
    owner_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[WorkOrderStatus] = None,
    priority: Optional[WorkOrderPriority] = None,

    
) -> WorkOrder:
    """This function creates work order of with the given name and type

    :param name: Work order name
    :type name: str
    :param description: Work order description
    :type description: str, optional
    :param work_order_type: Work order type object
    :type work_order_type: :class:`~psym.common.data_class.WorkOrderType`
    :param location_id: Existing location ID
    :type location_id: str, optional
    :param project_id: Existing project ID
    :type project_id: str, optional
    :param properties_dict: Dictionary of property name to property value

        * str - property name
        * PropertyValue - new value of the same type for this property

    :type properties_dict: Dict[str, PropertyValue]
    :param owner_id: Owner ID
    :type owner_id: str, optional
    :param assignee_id: Assignee ID
    :type assignee_id: str, optional
    :param status: Work order status
    :type status: :class:`~psym.common.data_enum.work_order_status.WorkOrderStatus`, optional
    :param priority: Work order priority
    :type priority: :class:`~psym.common.data_enum.work_order_priority.WorkOrderPriority`, optional

    :return: Work order
    :rtype: :class:`~psym.common.data_class.WorkOrder`

    **Example**

    .. code-block:: python

        work_order_type = client.add_work_order_type(
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
        client.add_work_order(
            name="new work order",
            work_order_type=work_order_type,
            description="Work order description",
            location_id="12345678",
            project_id="87654321",
            properties_dict={
                "Date Property": date.today(),
                "Lat/Lng Property": (-1.23,9.232),
                "E-mail Property": "user@fb.com",
                "Number Property": 11,
                "String Property": "aa",
                "Float Property": 1.23
            },
            owner_id="81726354",
            assignee_id="18273645",
            status="PLANNED",
            priority="MEDIUM",
        )
    """
    property_types = WORK_ORDER_TYPES[work_order_type.name].property_types
    properties = get_graphql_property_inputs(property_types, properties_dict)
    result = AddWorkOrderMutation.execute(
        client,
        AddWorkOrderInput(
            name=name,
            description=description,
            workOrderTypeId=work_order_type.id,
            locationId=location_id,
            projectId=project_id,
            properties=properties,
            ownerId=owner_id,
            assigneeId=assignee_id,
            status=WorkOrderStatus(status) if status else None,
            priority=WorkOrderPriority(priority) if priority else None,
            checkList=[],
            checkListCategories=[],
            organizationFk=organization,


        ),
    )
    return format_to_work_order(work_order_fragment=result), 


def get_work_orders(client: SymphonyClient) -> Iterator[WorkOrder]:
    """Get the iterator of work orders

    :raises:
        FailedOperationException: Internal symphony error

    :return: WorkOrder Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.WorkOrder` ]

    **Example**

    .. code-block:: python

        work_orders = client.get_work_orders()
        for work_order in work_orders:
            print(work_order.name, work_order.description)
    """
    result = WorkOrdersQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_work_order(work_order_fragment=node)


def get_work_order_by_id(client: SymphonyClient, id: str) -> WorkOrder:
    """Get work order by ID

    :param id: Work order ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order does not exist

    :return: WorkOrder
    :rtype: :class:`~psym.common.data_class.WorkOrder`

    **Example**

    .. code-block:: python

        work_order = client.get_work_order_by_id(
            id="12345678",
        )
    """
    result = WorkOrderDetailsQuery.execute(client, id=id)

    if result is None:
        raise EntityNotFoundError(entity=Entity.WorkOrder, entity_id=id)

    return format_to_work_order(work_order_fragment=result)

def get_work_order_by_name(client: SymphonyClient, name: str) -> WorkOrder:
    """This function gets existing WorkOrder by its name.

    :param name: Work order name
    :type name: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order type does not exist

    :return: Work order type
    :rtype: :class:`~psym.common.data_class.WorkOrder`

    **Example**

    .. code-block:: python

        client.get_work_order_type_by_name(name="WorkOrder Name")
    """

    work_orders = get_work_orders(client=client)
    for work_order in work_orders:
        if work_order.name == name:
            return work_order
    raise EntityNotFoundError(entity=Entity.WorkOrderType, entity_name=name)

def edit_work_order(
    client: SymphonyClient,
    work_order_id: str,
    new_name: Optional[str] = None,
    new_description: Optional[str] = None,
    new_location_id: Optional[str] = None,
    new_project_id: Optional[str] = None,
    new_properties_dict: Optional[Dict[str, PropertyValue]] = None,
    new_owner_id: Optional[str] = None,
    new_assignee_id: Optional[str] = None,
    new_status: Optional[WorkOrderStatus] = None,
    new_priority: Optional[WorkOrderPriority] = None,
    new_organization: Optional[str] = None,
) -> WorkOrder:
    """This function edits existing work order.

    :param work_order_id: Existing work order ID
    :type work_order_id: str
    :param new_name: Work order new name
    :type new_name: str, optional
    :param new_description: Work order new description
    :type new_description: str, optional
    :param new_location_id: Work order new existing location ID
    :type new_location_id: str, optional
    :param new_project_id: Work order new existing project ID
    :type new_project_id: str, optional
    :param new_properties_dict: Dictionary of property name to property default value

        * str - property name
        * PropertyValue - new default value of the same type for this property

    :type new_properties_dict: Dict[str, PropertyValue], optional
    :param new_owner_id: New owner ID
    :type new_owner_id: str, optional
    :param new_assignee_id: New assignee ID
    :type new_assignee_id: str, optional
    :param new_status: New work order status
    :type new_status: :class:`~psym.common.data_enum.work_order_status.WorkOrderStatus`, optional
    :param new_priority: New work order priority
    :type new_priority: :class:`~psym.common.data_enum.work_order_priority.WorkOrderPriority`, optional

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Work order does not exist

    :return: Work order
    :rtype: :class:`~psym.common.data_class.WorkOrder`

    **Example**

    .. code-block:: python

        edited_work_order = client.edit_work_order(
            work_order_id="12345678,
            new_name="New name",
            new_description="New description",
            new_location_id="12345678",
            new_project_id="87654321",
            new_properties_dict={
                "Date Property": date.today(),
                "Lat/Lng Property": (-1.23,9.232),
                "E-mail Property": "user@fb.com",
                "Number Property": 11,
                "String Property": "aa",
                "Float Property": 1.23
            },
            assignee_id="81726354",
            priority="MEDIUM",
        )
    """
    work_order = get_work_order_by_id(client=client, id=work_order_id)
    new_name = work_order.name if new_name is None else new_name
    new_description = (
        work_order.description if new_description is None else new_description
    )
    new_organization = (
        work_order.organization if new_organization is None else new_organization
    )
    new_properties = []
    if new_properties_dict:
        property_types = WORK_ORDER_TYPES[
            work_order.work_order_type_name
        ].property_types
        new_properties = get_graphql_property_inputs(
            property_types, new_properties_dict
        )
    edit_work_order_input = EditWorkOrderInput(
        id=work_order_id,
        name=new_name,
        description=new_description,
        locationId=new_location_id,
        projectId=new_project_id,
        properties=new_properties,
        ownerId=new_owner_id,
        assigneeId=new_assignee_id,
        status=new_status,
        priority=new_priority,
        checkList=[],
        checkListCategories=[],
        organizationFk=new_organization,
        

    )
    result = EditWorkOrderMutation.execute(client, edit_work_order_input)
    return format_to_work_order(work_order_fragment=result)


def delete_work_order(client: SymphonyClient, id: str) -> None:
    """This function deletes WorkOrder.

    :param id: Work order ID
    :type id: str

    :raises:
        FailedOperationException: Internal symphony error

    **Example**

    .. code-block:: python

        client.delete_work_order(id="12345678")
    """
    RemoveWorkOrderMutation.execute(client, id=id)

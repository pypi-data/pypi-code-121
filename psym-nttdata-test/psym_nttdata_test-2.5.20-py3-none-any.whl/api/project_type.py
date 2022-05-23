#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Iterator, List, Mapping, Optional

from psym._utils import get_graphql_property_type_inputs
from psym.client import SymphonyClient
from psym.common.cache import PROJECT_TYPES
from psym.common.data_class import (
    ProjectType,
    PropertyDefinition,
    PropertyValue,
    WorkOrderDefinition,
)
from psym.common.data_enum import Entity
from psym.common.data_format import (
    format_to_project_type,
    format_to_property_type_inputs,
)
from psym.exceptions import EntityNotFoundError
from psym.graphql.input.add_project_type_input import AddProjectTypeInput
from psym.graphql.input.work_order_definition_input import WorkOrderDefinitionInput
from psym.graphql.mutation.add_project_type import AddProjectTypeMutation
from psym.graphql.mutation.edit_project_type import (
    EditProjectTypeInput,
    EditProjectTypeMutation,
)
from psym.graphql.mutation.remove_project_type import RemoveProjectTypeMutation
from psym.graphql.query.project_type_details import ProjectTypeDetailsQuery
from psym.graphql.query.project_types import ProjectTypesQuery


def _populate_project_types(client: SymphonyClient) -> None:
    result = ProjectTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node:
            PROJECT_TYPES[node.name] = format_to_project_type(
                project_type_fragment=node
            )


def add_project_type(
    client: SymphonyClient,
    name: str,
    description: Optional[str] = None,
    properties: List[PropertyDefinition] = None,
    work_order_definitions: List[WorkOrderDefinition] = [],
) -> ProjectType:
    """This function creates ProjectType.

    :param name: Project type name
    :type name: str
    :param description: Project type description
    :type description: str, optional
    :param properties: List of property definitions
    :type properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param work_order_definitions: List of work order definitions
    :type work_order_definitions: List[ :class:`~psym.common.data_class.WorkOrderDefinition` ]

    :return: Project type
    :rtype: :class:`~psym.common.data_class.ProjectType`

    **Example**

    .. code-block:: python

        client.add_project_type(
            name="Project type",
            description="Project type description",
            properties=[
                PropertyDefinition(
                    property_name="project type property",
                    property_kind=PropertyKind.string,
                    default_raw_value="string value",
                    is_fixed=False,
                )
            ],
            work_order_definitions=[
                WorkOrderDefinition(
                    id="12345678",
                    definition_index="1",
                    work_order_type_id="87654321",
                ),
            ],
        )
    """
    property_type_inputs = []
    if properties is not None:
        property_type_inputs = format_to_property_type_inputs(data=properties)
    result = AddProjectTypeMutation.execute(
        client,
        AddProjectTypeInput(
            name=name,
            description=description,
            properties=property_type_inputs,
            workOrders=[
                WorkOrderDefinitionInput(
                    index=wod.definition_index, type=wod.work_order_type_id
                )
                for wod in work_order_definitions
            ],
        ),
    )
    added = format_to_project_type(project_type_fragment=result)
    PROJECT_TYPES[added.name] = added
    return added


def get_project_types(client: SymphonyClient) -> Iterator[ProjectType]:
    """Get the iterator of project types

    :raises:
        FailedOperationException: Internal symphony error

    :return: ProjectType Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.ProjectType` ]

    **Example**

    .. code-block:: python

        project_types = client.get_project_types()
        for project_type in project_types:
            print(project_type.name, project_type.description)
    """
    result = ProjectTypesQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_project_type(project_type_fragment=node)


def get_project_type_by_id(client: SymphonyClient, id: str) -> ProjectType:
    """This function gets existing ProjectType by its ID.

    :param id: Project type ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Project type does not exist

    :return: Project type
    :rtype: :class:`~psym.common.data_class.ProjectType`

    **Example**

    .. code-block:: python

        client.get_project_type_by_id(id="12345678")
    """
    result = ProjectTypeDetailsQuery.execute(client, id=id)

    if result is None:
        raise EntityNotFoundError(entity=Entity.ProjectType, entity_id=id)

    return format_to_project_type(project_type_fragment=result)


def add_property_types_to_project_type(
    client: SymphonyClient,
    project_type_id: str,
    new_properties: List[PropertyDefinition],
) -> ProjectType:
    """This function adds new property types to existing project type.

    :param project_type_id: Existing project type ID
    :type project_type_id: str
    :param new_properties: List of property definitions
    :type new_properties: List[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :raises:
        FailedOperationException: Internal symphony error

    :return: LocationType object
    :rtype: :class:`~psym.common.data_class.LocationType`

    **Example**

    .. code-block:: python

        project_type = client.add_property_types_to_project_type(
            project_type_id="12345678",
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
    project_type = get_project_type_by_id(client=client, id=project_type_id)
    new_property_type_inputs = format_to_property_type_inputs(data=new_properties)
    result = EditProjectTypeMutation.execute(
        client,
        EditProjectTypeInput(
            id=project_type.id,
            name=project_type.name,
            description=project_type.description,
            properties=new_property_type_inputs,
            workOrders=[
                WorkOrderDefinitionInput(
                    index=wod.definition_index, type=wod.work_order_type_id
                )
                for wod in project_type.work_order_definitions
            ],
        ),
    )
    edited = format_to_project_type(project_type_fragment=result)
    PROJECT_TYPES.pop(project_type.name)
    PROJECT_TYPES[edited.name] = edited
    return edited


def edit_project_type(
    client: SymphonyClient,
    project_type_id: str,
    new_name: Optional[str] = None,
    new_description: Optional[str] = None,
    new_properties_defaults: Optional[Mapping[str, PropertyValue]] = None,
    new_work_order_definitions: Optional[List[WorkOrderDefinition]] = [],
) -> ProjectType:
    """This function edits existing ProjectType.

    :param project_type_id: Existing project type ID
    :type project_type_id: str
    :param new_name: Project type new name
    :type new_name: str, optional
    :param new_description: Project type new description
    :type new_description: str, optional
    :param new_properties_defaults: Mapping of property name to property default value

        * str - property name
        * PropertyValue - new default value of the same type for this property

    :type new_properties_defaults: Mapping[str, PropertyValue], optional
    :param new_work_order_definitions: List of new work order definitions
    :type new_work_order_definitions: List[ :class:`~psym.common.data_class.WorkOrderDefinition` ], optional

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Project type does not exist

    :return: Project type
    :rtype: :class:`~psym.common.data_class.ProjectType`

    **Example**

    .. code-block:: python

        edited_project_type = client.edit_project_type(
            project_type_id="12345678,
            new_name="New name",
            new_description="New description",
        )
    """
    project_type = get_project_type_by_id(client=client, id=project_type_id)
    new_name = project_type.name if new_name is None else new_name
    new_description = (
        project_type.description if new_description is None else new_description
    )

    new_property_type_inputs = []
    if new_properties_defaults:
        property_types = project_type.property_types
        new_property_type_inputs = get_graphql_property_type_inputs(
            property_types, new_properties_defaults
        )
    work_order_definitions = (
        project_type.work_order_definitions
        if project_type.work_order_definitions
        else []
    )
    if new_work_order_definitions:
        work_order_definitions = new_work_order_definitions

    result = EditProjectTypeMutation.execute(
        client,
        EditProjectTypeInput(
            id=project_type.id,
            name=new_name,
            description=new_description,
            properties=new_property_type_inputs,
            workOrders=[
                WorkOrderDefinitionInput(
                    index=wod.definition_index, type=wod.work_order_type_id
                )
                for wod in work_order_definitions
            ],
        ),
    )
    edited = format_to_project_type(project_type_fragment=result)
    PROJECT_TYPES.pop(project_type.name)
    PROJECT_TYPES[edited.name] = edited
    return edited


def delete_project_type(client: SymphonyClient, id: str) -> None:
    """This function deletes ProjectType.

    :param id: Project type ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Project type does not exist

    **Example**

    .. code-block:: python

        client.delete_project_type(id="12345678")
    """
    project_type = get_project_type_by_id(client=client, id=id)
    if project_type is None:
        raise EntityNotFoundError(entity=Entity.ProjectType, entity_id=id)
    RemoveProjectTypeMutation.execute(client, id=id)
    del PROJECT_TYPES[project_type.name]

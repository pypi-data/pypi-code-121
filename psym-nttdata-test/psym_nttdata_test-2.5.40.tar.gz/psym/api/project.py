#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Dict, Iterator, Optional

from psym._utils import get_graphql_property_inputs
from psym.client import SymphonyClient
from psym.common.cache import PROJECT_TYPES
from psym.common.data_class import Project, ProjectType, PropertyValue
from psym.common.data_enum import Entity
from psym.common.data_format import format_to_project
from psym.exceptions import EntityNotFoundError
from psym.graphql.enum.project_priority import ProjectPriority
from psym.graphql.input.add_project_input import AddProjectInput
from psym.graphql.input.edit_project_input import EditProjectInput
from psym.graphql.mutation.add_project import AddProjectMutation
from psym.graphql.mutation.edit_project import EditProjectMutation
from psym.graphql.mutation.remove_project import RemoveProjectMutation
from psym.graphql.query.project_details import ProjectDetailsQuery
from psym.graphql.query.projects import ProjectsQuery


def add_project(
    client: SymphonyClient,
    name: str,
    project_type: ProjectType,
    description: Optional[str] = None,
    priority: Optional[ProjectPriority] = None,
    creator_id: Optional[str] = None,
    location_id: Optional[str] = None,
    properties_dict: Dict[str, PropertyValue] = {},
) -> Project:
    """This function creates Project.

    :param name: Project name
    :type name: str
    :param project_type: Project type object
    :type project_type: :class:`~psym.common.data_class.ProjectType`
    :param description: Project description
    :type description: str, optional
    :param priority: Project priority
    :type priority: :class:`~psym.common.data_enum.project_priority.ProjectPriority`, optional
    :param creator_id: Creator ID
    :type creator_id: str, optional
    :param location_id: Existing location ID
    :type location_id: str, optional
    :param properties_dict: Dictionary of property name to property value

        * str - property name
        * PropertyValue - new value of the same type for this property

    :type properties_dict: Dict[str, PropertyValue]

    :return: Project
    :rtype: :class:`~psym.common.data_class.Project`

    **Example**

    .. code-block:: python

        project_type = client.add_project_type(
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
        client.add_project(
            name="new project",
            project_type=project_type,
            description="Project description",
            priority="MEDIUM",
            creator_id="81726354",
            location_id="12345678",
            properties_dict={
                "Date Property": date.today(),
                "Lat/Lng Property": (-1.23,9.232),
                "E-mail Property": "user@fb.com",
                "Number Property": 11,
                "String Property": "aa",
                "Float Property": 1.23
            },
        )
    """
    property_types = PROJECT_TYPES[project_type.name].property_types
    properties = get_graphql_property_inputs(property_types, properties_dict)
    result = AddProjectMutation.execute(
        client,
        AddProjectInput(
            name=name,
            description=description,
            priority=priority,
            creatorId=creator_id,
            type=project_type.id,
            location=location_id,
            properties=properties,
        ),
    )
    return format_to_project(project_fragment=result)


def edit_project(
    client: SymphonyClient,
    project_id: str,
    new_name: Optional[str] = None,
    new_description: Optional[str] = None,
    new_priority: Optional[ProjectPriority] = None,
    new_creator_id: Optional[str] = None,
    new_location_id: Optional[str] = None,
    new_properties_dict: Optional[Dict[str, PropertyValue]] = None,
) -> Project:
    """This function edits existing project.

    :param project_id: Existing project ID
    :type project_id: str
    :param new_name: Project new name
    :type new_name: str, optional
    :param new_description: Project new description
    :type new_description: str, optional
    :param new_priority: New project priority
    :type new_priority: :class:`~psym.common.data_enum.project_priority.ProjectPriority`, optional
    :param new_creator_id: New creator ID
    :type new_creator_id: str, optional
    :param new_location_id: Project new existing location ID
    :type new_location_id: str, optional
    :param new_properties_dict: Dictionary of property name to property default value

        * str - property name
        * PropertyValue - new default value of the same type for this property

    :type new_properties_dict: Dict[str, PropertyValue], optional

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Project does not exist

    :return: Project
    :rtype: :class:`~psym.common.data_class.Project`

    **Example**

    .. code-block:: python

        edited_project = client.edit_project(
            project_id="12345678,
            new_name="New name",
            new_description="New description",
            new_properties_dict={
                "Date Property": date.today(),
                "Lat/Lng Property": (-1.23,9.232),
                "E-mail Property": "user@fb.com",
                "Number Property": 11,
                "String Property": "aa",
                "Float Property": 1.23
            },
            new_work_order_definitions=[
                WorkOrderDefinition(
                    id="12345678",
                    definition_index="1",
                    work_order_type_id="87654321",
                ),
            ],
        )
    """
    project = get_project_by_id(client=client, id=project_id)
    new_name = project.name if new_name is None else new_name
    new_description = (
        project.description if new_description is None else new_description
    )
    new_properties = []
    if new_properties_dict:
        property_types = PROJECT_TYPES[project.project_type_name].property_types
        new_properties = get_graphql_property_inputs(
            property_types, new_properties_dict
        )
    edit_project_input = EditProjectInput(
        id=project_id,
        name=new_name,
        description=new_description,
        priority=new_priority,
        creatorId=new_creator_id,
        type=project.project_type_id,
        location=new_location_id,
        properties=new_properties,
    )
    result = EditProjectMutation.execute(client, edit_project_input)
    return format_to_project(project_fragment=result)


def get_projects(client: SymphonyClient) -> Iterator[Project]:
    """Get the iterator of projects

    :raises:
        FailedOperationException: Internal symphony error

    :return: Project Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.Project` ]

    **Example**

    .. code-block:: python

        projects = client.get_projects()
        for project in projects:
            print(project.name, project.description)
    """
    result = ProjectsQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield format_to_project(project_fragment=node)


def get_project_by_id(client: SymphonyClient, id: str) -> Project:
    """Get project by ID

    :param id: Project ID
    :type id: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Project does not exist

    :return: Project
    :rtype: :class:`~psym.common.data_class.Project`

    **Example**

    .. code-block:: python

        project = client.get_project_by_id(
            id="12345678",
        )
    """
    result = ProjectDetailsQuery.execute(client, id=id)

    if result is None:
        raise EntityNotFoundError(entity=Entity.Project, entity_id=id)

    return format_to_project(project_fragment=result)


def delete_project(client: SymphonyClient, id: str) -> None:
    """This function deletes Project.

    :param id: Project ID
    :type id: str

    :raises:
        FailedOperationException: Internal symphony error

    **Example**

    .. code-block:: python

        client.delete_project(id="12345678")
    """
    RemoveProjectMutation.execute(client, id=id)

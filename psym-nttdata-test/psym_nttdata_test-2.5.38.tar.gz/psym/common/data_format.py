#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from numbers import Number
from typing import List, Sequence, cast
from psym.graphql.fragment.document_category import DocumentCategoryFragment

from psym.graphql.fragment.equipment import EquipmentFragment
from psym.graphql.fragment.equipment_port_type import EquipmentPortTypeFragment
from psym.graphql.fragment.equipment_type import EquipmentTypeFragment
from psym.graphql.fragment.location import LocationFragment
from psym.graphql.fragment.location_type import LocationTypeFragment
from psym.graphql.fragment.project import ProjectFragment
from psym.graphql.fragment.project_type import ProjectTypeFragment
from psym.graphql.fragment.property_type import PropertyTypeFragment
from psym.graphql.fragment.service_type import ServiceTypeFragment
from psym.graphql.fragment.work_order import WorkOrderFragment
from psym.graphql.fragment.work_order_type import WorkOrderTypeFragment
from psym.graphql.input.document_category_input import DocumentCategoryInput
from psym.graphql.input.property_type_input import PropertyTypeInput

from .data_class import (
    DocumentCategory,
    Equipment,
    EquipmentPortType,
    EquipmentType,
    Location,
    LocationType,
    Project,
    ProjectType,
    PropertyDefinition,
    ServiceEndpointDefinition,
    ServiceType,
    WorkOrder,
    WorkOrderDefinition,
    WorkOrderType,
)


def format_to_property_definition(
    property_type_fragment: PropertyTypeFragment,
) -> PropertyDefinition:
    """This function gets `psym.graphql.fragment.property_type.PropertyTypeFragment` object as argument
    and formats it to `psym.common.data_class.PropertyDefinition` object

        :param property_type_fragment: Existing property type fragment object
        :type property_type_fragment: :class:`~psym.graphql.fragment.property_type.PropertyTypeFragment`

        :return: PropertyDefinition object
        :rtype: :class:`~psym.common.data_class.PropertyDefinition`

        **Example**

        .. code-block:: python

            property_definition = format_to_property_definition(
                property_type_fragment=property_type_fragment,
            )
    """
    return PropertyDefinition(
        id=property_type_fragment.id,
        property_name=property_type_fragment.name,
        property_kind=property_type_fragment.type,
        default_raw_value=property_type_fragment.rawValue,
        is_fixed=not property_type_fragment.isInstanceProperty,
        external_id=property_type_fragment.externalId,
        is_mandatory=property_type_fragment.isMandatory,
        is_deleted=property_type_fragment.isDeleted,
    )


def format_to_document_category(
    document_category_fragment: DocumentCategoryFragment,
) -> DocumentCategory:
    """This function gets `psym.graphql.fragment.property_type.DocumentCategoryFragment` object as argument
    and formats it to `psym.common.data_class.DocumentCategory` object

        :param document_category_fragment: Existing document category fragment object
        :type document_category_fragment: :class:`~psym.graphql.fragment.document_category.DocumentCategoryFragment`

        :return: DocumentCategory object
        :rtype: :class:`~psym.common.data_class.DocumentCategory`

        **Example**

        .. code-block:: python

            property_definition = format_to_document_category(
                document_category_fragment=document_category_fragment,
            )
    """
    return DocumentCategory(
        id=document_category_fragment.id,
        name=document_category_fragment.name,
        index=document_category_fragment.index,
    )


def format_to_property_definitions(
    data: Sequence[PropertyTypeFragment],
) -> Sequence[PropertyDefinition]:
    """This function gets Sequence[ `PropertyTypeFragment` ] as argument and formats it to Sequence[ `PropertyDefinition` ]

    :param data: Existing property type fragments sequence
    :type data: Sequence[ :class:`~psym.graphql.fragment.property_type.PropertyTypeFragment` ]

    :return: PropertyDefinitions sequence
    :rtype: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]

    **Example**

    .. code-block:: python

        property_definitions = format_to_property_definitions(
            data=property_type_fragments,
        )
    """
    return [
        format_to_property_definition(property_type_fragment)
        for property_type_fragment in data
    ]


def format_to_document_categories(
    data: Sequence[DocumentCategoryFragment],
) -> Sequence[DocumentCategory]:
    """This function gets Sequence[ `DocumentCategoryFragment` ] as argument and formats it to Sequence[ `DocumentCategory` ]

    :param data: Existing document category fragments sequence
    :type data: Sequence[ :class:`~psym.graphql.fragment.document_category.DocumentCategoryFragment` ]

    :return: DocumentCategories sequence
    :rtype: Sequence[ :class:`~psym.common.data_class.DocumentCategory` ]

    **Example**

    .. code-block:: python

        document_categories = format_to_document_categories(
            data=document_category_fragments,
        )
    """
    if data is None:
        return []
        
    return [
        format_to_document_category(document_category_fragment)
        for document_category_fragment in data
    ]


def format_to_property_type_input(
    property_definition: PropertyDefinition,
    is_new: bool = True,
    property_type_id=None,
) -> PropertyTypeInput:
    """This function gets `PropertyDefinition` object as argument and formats it to `PropertyTypeInput` object

    :param property_definition: Existing property definition object
    :type property_definition: :class:`~psym.common.data_class.PropertyDefinition`
    :param is_new: Is new flag
    :type is_new: bool

    :return: PropertyTypeInput object
    :rtype: :class:`~psym.graphql.input.property_type.PropertyTypeInput`

    **Example**

    .. code-block:: python

        property_type_input = format_to_property_type_input(
            property_definition=property_definition,
        )
    """
    string_value = None
    int_value = None
    boolean_value = None
    float_value = None
    latitude_value = None
    longitude_value = None
    range_from_value = None
    range_to_value = None

    kind = property_definition.property_kind.value

    if property_definition.default_raw_value is not None:
        default_raw_value = property_definition.default_raw_value
        if kind == "int":
            int_value = int(default_raw_value, base=10)
        elif kind == "bool":
            boolean_value = True if default_raw_value.lower() == "true" else False
        elif kind == "float":
            float_value = cast(Number, float(default_raw_value))
        elif kind == "range":
            string_range = default_raw_value.split(" - ")
            range_from_value = cast(Number, float(string_range[0]))
            range_to_value = cast(Number, float(string_range[1]))
        elif kind == "gps_location":
            string_coordinates = default_raw_value.split(", ")
            latitude_value = cast(Number, float(string_coordinates[0]))
            longitude_value = cast(Number, float(string_coordinates[1]))
        else:
            string_value = default_raw_value

    new_property_type_id = property_definition.id
    if is_new:
        new_property_type_id = None
    elif property_type_id is not None:
        new_property_type_id = property_type_id

    return PropertyTypeInput(
        id=new_property_type_id,
        name=property_definition.property_name,
        type=property_definition.property_kind,
        externalId=property_definition.external_id
        if not is_new and property_definition.external_id
        else None,
        stringValue=string_value,
        intValue=int_value,
        booleanValue=boolean_value,
        floatValue=float_value,
        latitudeValue=latitude_value,
        longitudeValue=longitude_value,
        rangeFromValue=range_from_value,
        rangeToValue=range_to_value,
        isInstanceProperty=not property_definition.is_fixed,
        isMandatory=property_definition.is_mandatory,
        isDeleted=property_definition.is_deleted,
    )


def format_to_document_category_input(
    document_category: DocumentCategory,
) -> DocumentCategoryInput:
    """This function gets `DocumentCategory` object as argument and formats it to `DocumentCategoryInput` object

    :param document_category: Document category object
    :type document_category: :class:`~psym.common.data_class.DocumentCategory`

    :return: DocumentCategoryInput object
    :rtype: :class:`~psym.graphql.input.document_category.DocumentCategoryInput`

    **Example**

    .. code-block:: python

        property_type_input = format_to_document_category_input(
            document_category=document_category,
        )
    """

    return DocumentCategoryInput(
        id=document_category.id,
        name=document_category.name,
        index=document_category.index,
    )


def format_to_property_type_inputs(
    data: Sequence[PropertyDefinition],
) -> List[PropertyTypeInput]:
    """This function gets Sequence[ `PropertyDefinition` ] as argument and formats it to Sequence[ `PropertyTypeInput` ]

    :param data: Existing property definitions sequence
    :type data: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]

    :return: PropertyTypeInputs list
    :rtype: List[ :class:`~psym.graphql.input.property_type.PropertyTypeInput` ]

    **Example**

    .. code-block:: python

        property_type_inputs = format_to_property_type_inputs(
            data=property_type_definitions,
        )
    """
    return [
        format_to_property_type_input(property_definition)
        for property_definition in data
    ]


def format_to_document_category_inputs(
    document_category_list: Sequence[DocumentCategory],
) -> List[DocumentCategoryInput]:
    """This function gets Sequence[ `DocumentCategory` ] as argument and formats it to Sequence[ `DocumentCategoryInput` ]

    :param data: Existing documents categories sequence
    :type data: Sequence[ :class:`~psym.common.data_class.DocumentCategory` ]

    :return: DocumentCategoryInput list
    :rtype: List[ :class:`~psym.graphql.input.document_category.DocumentCategoryInput` ]

    **Example**

    .. code-block:: python

        document_category_input = format_to_document_category_inputs(
            data=documents_categories,
        )
    """
    if document_category_list is None:
        return []

    return [
        format_to_document_category_input(document_category)
        for document_category in document_category_list
    ]


def format_to_project_type(project_type_fragment: ProjectTypeFragment) -> ProjectType:
    """This function gets `psym.graphql.fragment.project_type.ProjectTypeFragment` object as argument
    and formats it to `psym.common.data_class.ProjectType` object

        :param project_type_fragment: Existing project type fragment object
        :type project_type_fragment: :class:`~psym.graphql.fragment.project_type.ProjectTypeFragment`

        :return: ProjectType object
        :rtype: :class:`~psym.common.data_class.ProjectType`

        **Example**

        .. code-block:: python

            project_type = format_to_project_type(
                project_type_fragment=project_type_fragment,
            )
    """
    return ProjectType(
        id=project_type_fragment.id,
        name=project_type_fragment.name,
        description=project_type_fragment.description,
        property_types=format_to_property_definitions(project_type_fragment.properties),
        work_order_definitions=[
            WorkOrderDefinition(
                id=wod.id if wod.id else None,
                definition_index=wod.index if wod.index else None,
                work_order_type_id=wod.type.id,
            )
            for wod in project_type_fragment.workOrders
        ],
    )


def format_to_project(project_fragment: ProjectFragment) -> Project:
    """This function gets `psym.graphql.fragment.project.ProjectFragment` object as argument
    and formats it to `psym.common.data_class.Project` object

        :param project_fragment: Existing project fragment object
        :type project_fragment: :class:`~psym.graphql.fragment.project_type.ProjectFragment`

        :return: Project object
        :rtype: :class:`~psym.common.data_class.Project`

        **Example**

        .. code-block:: python

            project = format_to_project(
                project_fragment=project_fragment,
            )
    """
    work_orders = []
    if project_fragment.workOrders:
        work_orders = [format_to_work_order(wo) for wo in project_fragment.workOrders]
    return Project(
        id=project_fragment.id,
        name=project_fragment.name,
        description=project_fragment.description,
        priority=project_fragment.priority,
        created_by=project_fragment.createdBy.id
        if project_fragment.createdBy
        else None,
        project_type_name=project_fragment.type.name,
        project_type_id=project_fragment.type.id,
        location_id=project_fragment.location.id if project_fragment.location else None,
        work_orders=work_orders,
        properties=project_fragment.properties,
    )


def format_to_equipment_port_type(
    equipment_port_type_fragment: EquipmentPortTypeFragment,
) -> EquipmentPortType:
    """This function gets `psym.graphql.fragment.equipment_port_type.EquipmentPortTypeFragment` object as argument
    and formats it to `psym.common.data_class.EquipmentPortType` object

        :param project_type_fragment: Existing equipment port type fragment object
        :type project_type_fragment: :class:`~psym.graphql.fragment.equipment_port_type.EquipmentPortTypeFragment`

        :return: EquipmentPortType object
        :rtype: :class:`~psym.common.data_class.EquipmentPortType`

        **Example**

        .. code-block:: python

            equipment_port_type = format_to_equipment_port_type(
                equipment_port_type_fragment=equipment_port_type_fragment,
            )
    """
    return EquipmentPortType(
        id=equipment_port_type_fragment.id,
        name=equipment_port_type_fragment.name,
        property_types=format_to_property_definitions(
            equipment_port_type_fragment.propertyTypes
        ),
        link_property_types=format_to_property_definitions(
            equipment_port_type_fragment.linkPropertyTypes
        ),
    )


def format_to_work_order_type(
    work_order_type_fragment: WorkOrderTypeFragment,
) -> WorkOrderType:
    """This function gets `psym.graphql.fragment.work_order_type.WorkOrderTypeFragment` object as argument
    and formats it to `psym.common.data_class.WorkOrderType` object

        :param work_order_type_fragment: Existing work order type fragment object
        :type work_order_type_fragment: :class:`~psym.graphql.fragment.work_order_type.WorkOrderTypeFragment`

        :return: WorkOrderType object
        :rtype: :class:`~psym.common.data_class.WorkOrderType`

        **Example**

        .. code-block:: python

            work_order_type = format_to_work_order_type(
                work_order_type_fragment=work_order_type_fragment,
            )
    """
    return WorkOrderType(
        id=work_order_type_fragment.id,
        name=work_order_type_fragment.name,
        description=work_order_type_fragment.description,
        property_types=format_to_property_definitions(
            work_order_type_fragment.propertyTypes
        ),
    )


def format_to_work_order(work_order_fragment: WorkOrderFragment) -> WorkOrder:
    """This function gets `psym.graphql.fragment.work_order.WorkOrderFragment` object as argument
    and formats it to `psym.common.data_class.WorkOrder` object

        :param work_order_fragment: Existing work order fragment object
        :type work_order_fragment: :class:`~psym.graphql.fragment.work_order.WorkOrderFragment`

        :return: WorkOrder object
        :rtype: :class:`~psym.common.data_class.WorkOrder`

        **Example**

        .. code-block:: python

            work_order = format_to_work_order(
                work_order_fragment=work_order_fragment,
            )
    """
    return WorkOrder(
        id=work_order_fragment.id,
        name=work_order_fragment.name,
        description=work_order_fragment.description,
        work_order_type_name=work_order_fragment.workOrderType.name,
        location_id=work_order_fragment.location.id
        if work_order_fragment.location
        else None,
        project_id=work_order_fragment.project.id
        if work_order_fragment.project
        else None,
        properties=work_order_fragment.properties,
        owner_id=work_order_fragment.owner.id,
        assignee_id=work_order_fragment.assignedTo.id
        if work_order_fragment.assignedTo
        else None,
        status=work_order_fragment.status,
        priority=work_order_fragment.priority,
        organization=work_order_fragment.organizationFk
    )


def format_to_location_type(
    location_type_fragment: LocationTypeFragment,
) -> LocationType:
    """This function gets `psym.graphql.fragment.location_type.LocationTypeFragment` object as argument
    and formats it to `psym.common.data_class.LocationType` object

        :param location_type_fragment: Existing location type fragment object
        :type location_type_fragment: :class:`~psym.graphql.fragment.location_type.LocationTypeFragment`

        :return: LocationType object
        :rtype: :class:`~psym.common.data_class.LocationType`

        **Example**

        .. code-block:: python

            location_type = format_to_location_type(
                location_type_fragment=location_type_fragment,
            )
    """
    return LocationType(
        name=location_type_fragment.name,
        id=location_type_fragment.id,
        property_types=format_to_property_definitions(
            location_type_fragment.propertyTypes
        ),
        document_categories=format_to_document_categories(
            location_type_fragment.documentCategories
        ),
        map_type=location_type_fragment.mapType,
        map_zoom_level=location_type_fragment.mapZoomLevel,
        is_site=location_type_fragment.isSite,
    )


def format_to_location(location_fragment: LocationFragment) -> Location:
    """This function gets `psym.graphql.fragment.location.LocationFragment` object as argument
    and formats it to `psym.common.data_class.Location` object

        :param location_fragment: Existing location fragment object
        :type location_fragment: :class:`~psym.graphql.fragment.location.LocationFragment`

        :return: Location object
        :rtype: :class:`~psym.common.data_class.Location`

        **Example**

        .. code-block:: python

            location = format_to_location(
                location_fragment=location_fragment,
            )
    """
    return Location(
        id=location_fragment.id,
        name=location_fragment.name,
        latitude=location_fragment.latitude,
        longitude=location_fragment.longitude,
        external_id=location_fragment.externalId,
        location_type_name=location_fragment.locationType.name,
        properties=location_fragment.properties,
    )


def format_to_equipment_type(
    equipment_type_fragment: EquipmentTypeFragment,
) -> EquipmentType:
    """This function gets `psym.graphql.fragment.equipment_type.EquipmentTypeFragment` object as argument
    and formats it to `psym.common.data_class.EquipmentType` object

        :param equipment_type_fragment: Existing equipment type fragment object
        :type equipment_type_fragment: :class:`~psym.graphql.fragment.equipment_type.EquipmentTypeFragment`

        :return: EquipmentType object
        :rtype: :class:`~psym.common.data_class.EquipmentType`

        **Example**

        .. code-block:: python

            equipment_type = format_to_equipment_type(
                equipment_type_fragment=equipment_type_fragment,
            )
    """
    return EquipmentType(
        name=equipment_type_fragment.name,
        category=equipment_type_fragment.category,
        id=equipment_type_fragment.id,
        property_types=format_to_property_definitions(
            equipment_type_fragment.propertyTypes
        ),
        position_definitions=equipment_type_fragment.positionDefinitions,
        port_definitions=equipment_type_fragment.portDefinitions,
    )


def format_to_equipment(equipment_fragment: EquipmentFragment) -> Equipment:
    """This function gets `psym.graphql.fragment.equipment.EquipmentFragment` object as argument
    and formats it to `psym.common.data_class.Equipment` object

        :param equipment_fragment: Existing equipment type fragment object
        :type equipment_fragment: :class:`~psym.graphql.fragment.equipment.EquipmentFragment`

        :return: Equipment object
        :rtype: :class:`~psym.common.data_class.Equipment`

        **Example**

        .. code-block:: python

            equipment = format_to_equipment(
                equipment_fragment=equipment_fragment,
            )
    """
    return Equipment(
        id=equipment_fragment.id,
        external_id=equipment_fragment.externalId,
        name=equipment_fragment.name,
        equipment_type_name=equipment_fragment.equipmentType.name,
        properties=equipment_fragment.properties,
    )


def format_to_service_type(service_type_fragment: ServiceTypeFragment) -> ServiceType:
    """This function gets `psym.graphql.fragment.equipment_type.ServiceTypeFragment` object as argument
    and formats it to `psym.common.data_class.ServiceType` object

        :param service_type_fragment: Existing service type fragment object
        :type service_type_fragment: :class:`~psym.graphql.fragment.equipment_type.ServiceTypeFragment`

        :return: ServiceType object
        :rtype: :class:`~psym.common.data_class.ServiceType`

        **Example**

        .. code-block:: python

            service_type = format_to_service_type(
                service_type_fragment=service_type_fragment,
            )
    """
    definitions = []
    if service_type_fragment.endpointDefinitions:
        definitions = [
            ServiceEndpointDefinition(
                id=definition.id,
                name=definition.name,
                endpoint_definition_index=definition.index,
                role=definition.role,
                equipment_type_id=definition.equipmentType.id,
            )
            for definition in service_type_fragment.endpointDefinitions
        ]
    return ServiceType(
        id=service_type_fragment.id,
        name=service_type_fragment.name,
        has_customer=service_type_fragment.hasCustomer,
        property_types=format_to_property_definitions(
            service_type_fragment.propertyTypes
        ),
        endpoint_definitions=definitions,
    )

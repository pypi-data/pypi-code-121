#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from datetime import date, datetime, time
from numbers import Number
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from psym.graphql.enum.project_priority import ProjectPriority
from psym.graphql.enum.property_kind import PropertyKind
from psym.graphql.enum.user_role import UserRole
from psym.graphql.enum.user_status import UserStatus
from psym.graphql.enum.flow_instance_status import FlowInstanceStatus
from psym.graphql.enum.work_order_priority import WorkOrderPriority
from psym.graphql.enum.work_order_status import WorkOrderStatus
from psym.graphql.fragment import document_category
from psym.graphql.fragment.equipment_port_definition import (
    EquipmentPortDefinitionFragment,
)
from psym.graphql.fragment.equipment_position_definition import (
    EquipmentPositionDefinitionFragment,
)
from psym.graphql.fragment.property import PropertyFragment

from ..graphql.enum.image_entity import ImageEntity

ReturnType = TypeVar("ReturnType")
PropertyValue = Union[date, datetime, float, int, str, bool, Tuple[float, float]]
PropertyValueType = Union[
    Type[date],
    Type[datetime],
    Type[float],
    Type[int],
    Type[str],
    Type[bool],
    Type[Tuple[float, float]],
]


class PropertyDefinition(NamedTuple):
    """
    :param property_name: Type name
    :type property_name: str
    :param property_kind: Property kind
    :type property_kind: class:`~psym.graphql.enum.property_kind.PropertyKind`
    :param default_raw_value: Default property value as a string

        * string - "string"
        * int - "123"
        * bool - "true" / "True" / "TRUE"
        * float - "0.123456"
        * date - "24/10/2020"
        * range - "0.123456 - 0.2345" / "1 - 2"
        * email - "email@some.domain"
        * gps_location - "0.1234, 0.2345"

    :type default_raw_value: str, optional
    :param id: ID
    :type id: str, optional
    :param is_fixed: Fixed value flag
    :type is_fixed: bool, optional
    :param external_id: Property type external ID
    :type external_id: str, optional
    :param is_mandatory: Mandatory value flag
    :type is_mandatory: bool, optional
    :param is_deleted: Is delete flag
    :type is_deleted: bool, optional
    """

    property_name: str
    property_kind: PropertyKind
    default_raw_value: Optional[str]
    id: Optional[str] = None
    is_fixed: Optional[bool] = False
    external_id: Optional[str] = None
    is_mandatory: Optional[bool] = False
    is_deleted: Optional[bool] = False


class DataTypeName(NamedTuple):
    """
    :param data_type: Data type
    :type data_type: :attr:`~psym.graphql.data_class.PropertyValueType`
    :param graphql_field_name: GraphQL field name, in case of `gps_location` it is Tuple[`latitudeValue`, `longitudeValue`]
    :type graphql_field_name: Tuple[str, ...]
    """

    data_type: PropertyValueType
    graphql_field_name: Tuple[str, ...]


TYPE_AND_FIELD_NAME = {
    "date": DataTypeName(data_type=date, graphql_field_name=("stringValue",)),
    "datetime_local": DataTypeName(
        data_type=datetime, graphql_field_name=("stringValue",)
    ),
    "float": DataTypeName(data_type=float, graphql_field_name=("floatValue",)),
    "int": DataTypeName(data_type=int, graphql_field_name=("intValue",)),
    "email": DataTypeName(data_type=str, graphql_field_name=("stringValue",)),
    "string": DataTypeName(data_type=str, graphql_field_name=("stringValue",)),
    "bool": DataTypeName(data_type=bool, graphql_field_name=("booleanValue",)),
    "gps_location": DataTypeName(
        data_type=tuple,  # type: ignore
        graphql_field_name=("latitudeValue", "longitudeValue"),
    ),
    "enum": DataTypeName(data_type=str, graphql_field_name=("stringValue",)),
}


class DocumentCategory(NamedTuple):
    """
    :param name: Category name
    :type name: str
    :param dc_index: Category name index
    :type dc_index: int, optional
    :param id: ID
    :type id: str, optional
    """

    name: str
    index: Optional[int] = None
    id: Optional[str] = None


class LocationType(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param property_types: PropertyTypes sequence
    :type property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param map_type: Map type
    :type map_type: str, optional
    :param map_zoom_level: Map zoom level
    :type map_zoom_level: int, optional
    :param is_site: Is site flag for location
    :type is_site: bool
    """

    name: str
    id: str
    property_types: Sequence[PropertyDefinition]
    document_categories: Sequence[DocumentCategory]
    map_type: Optional[str]
    map_zoom_level: Optional[int]
    is_site: bool


class Location(NamedTuple):
    """
    :param name: name
    :type name: str
    :param id: ID
    :type id: str
    :param latitude: latitude
    :type latitude: Number
    :param longitude: longitude
    :type longitude: Number
    :param external_id: external ID
    :type external_id: str, optional
    :param location_type_name: Location type name
    :type location_type_name: str
    :param properties: PropertyFragment sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ])
    """

    name: str
    id: str
    latitude: Number
    longitude: Number
    external_id: Optional[str]
    location_type_name: str
    properties: Sequence[PropertyFragment]


class EquipmentType(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param category: Category
    :type category: str, optional
    :param id: ID
    :type id: str
    :param property_types: PropertyDefinitions sequence
    :type property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param position_definitions: EquipmentPositionDefinitionFragments sequence
    :type position_definitions: Sequence[ :class:`~psym.graphql.fragment.equipment_position_definition.EquipmentPositionDefinitionFragment` ]
    :param port_definitions: EquipmentPortDefinitionFragments sequence
    :type port_definitions: Sequence[ :class:`~psym.graphql.fragment.equipment_port_definition.EquipmentPortDefinitionFragment` ]
    """

    name: str
    category: Optional[str]
    id: str
    property_types: Sequence[PropertyDefinition]
    position_definitions: Sequence[EquipmentPositionDefinitionFragment]
    port_definitions: Sequence[EquipmentPortDefinitionFragment]


class EquipmentPortType(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Name
    :type name: str
    :param property_types: Property types sequence
    :type property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param link_property_types: Link property types sequence
    :type link_property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    """

    id: str
    name: str
    property_types: Sequence[PropertyDefinition]
    link_property_types: Sequence[PropertyDefinition]


class Equipment(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param external_id: External ID
    :type external_id: str, optional
    :param name: Name
    :type name: str
    :param equipment_type_name: Equipment type name
    :type equipment_type_name: str
    :param properties: PropertyFragment sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ])
    """

    id: str
    external_id: Optional[str]
    name: str
    equipment_type_name: str
    properties: Sequence[PropertyFragment]


class Link(NamedTuple):
    """
    :param id: Link ID
    :type id: str
    :param properties: Properties sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ]
    :param service_ids: Service IDs list
    :type service_ids: List[str]
    """

    id: str
    properties: Sequence[PropertyFragment]
    service_ids: List[str]


class EquipmentPortDefinitionAlias(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str, optional
    """

    name: str
    id: Optional[str] = None


class EquipmentPortDefinition(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str, optional
    :param visible_label: Visible label
    :type visible_label: str, optional
    :param port_definition_index: Index
    :type port_definition_index: int, optional
    :param port_type_name: Port type name
    :type port_type_name: str, optional
    :param connected_ports: ConnectedPorts list
    :type connected_ports: List [ :class:`~psym.common.data_class.EquipmentPortDefinitionAlias] , optional
    """

    name: str
    connected_ports: List[EquipmentPortDefinitionAlias]
    id: Optional[str] = None
    visible_label: Optional[str] = None
    port_definition_index: Optional[int] = None
    port_type_name: Optional[str] = None


class EquipmentPort(NamedTuple):
    """
    :param id: Equipment port ID
    :type id: str
    :param properties: Properties sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ]
    :param definition: EquipmentPortDefinition object
    :type definition: :class:`~psym.common.data_class.EquipmentPortDefinition`
    :param link: Link object
    :type link: :class:`~psym.common.data_class.Link`
    """

    id: str
    properties: Sequence[PropertyFragment]
    definition: EquipmentPortDefinition
    link: Optional[Link]


class Customer(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Name
    :type name: str
    :param external_id: External ID
    :type external_id: str, optional
    """

    id: str
    name: str
    external_id: Optional[str]

class KqiCategory(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class KqiPerspective(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class KqiTemporalFrecuency(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str
    
class KqiSource(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class Kqi (NamedTuple):
    """This function cannot be used because the mandatory parameters StarDatetime and EndDatetime are not allowed in the format required in the Api.
    
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param description: description
    :type description: str
    :param formula: formula
    :type formula: str
    :param startDatetime: startDatetime
    :type startDatetime: datetime
    :param EndDateTime: EndDateTime
    :type EndDateTime: datetime
    :param kqiSource: kqiSource Object
    :type kqiSource: `~psym.common.data_class.kqi_cource`
    :param kqiCategory: kqiCategory
    :type kqiCategory: `~psym.common.data_class.kqi_category`
    :param KqiPerspective: KqiPerspective
    :type KqiPerspective: `~psym.common.data_class.kqi_perspective`
    :param KqiTemporalFrecuency: KqiTemporalFrecuency
    :type KqiTemporalFrecuency: `~psym.common.data_class.kqi_temporal_frecuency`
    """

    id: str
    name: str
    description: str
    formula: str
    startDatetime: datetime
    EndDateTime: datetime
    kqiSource: str
    kqiCategory: str
    KqiPerspective: str
    KqiTemporalFrecuency: str

class KqiTarget (NamedTuple):
    """This function cannot be used because the mandatory parameters Starttime and Endtime are not allowed in the format required in the Apiand need the kqi entity.
    
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param frame: Frame
    :type frame: int
    :param allowed variation: Allowed variation
    :type allowed variation: int
    :param starttime: starttime
    :type starttime: time
    :param EndTime: EndTime
    :type EndTime: time
    :param impact: impact
    :type impact: str
    :param status: status
    :type status: str
    :param period: period
    :type period: str
    :param kqi: kqi Object
    :type kqi: `~psym.common.data_class.kqi`

    """

    id: str
    name: str
    frame: int
    allowedVariation: float
    starttime: time
    EndTime: time
    impact: str
    status: bool
    period: int
    kqi: str

class KqiComparator (NamedTuple):
    """This function cannot be used because it requires the kqiTarget entity, and this entity cannot be used because of a bug in the time parameters.he
    
    :param number: Number
    :type number: int
    :param id: ID
    :type id: str
    :param type comparator: type comparator
    :type type comparator: str
    :param kqiTraget: kqiTraget Object
    :type kqiTraget: `~psym.common.data_class.kqi_traget`
    :param comparator: comparator Object
    :type comparator: `~psym.common.data_class.comparator`
    """
    id: str
    number: int
    typeComparator:str
    kqiTraget: str
    comparator: str


class AlarmFiltering (NamedTuple):
    """This function cannot be used because it requires the kqiTarget entity, and this entity cannot be used because of a bug in the time parameters.he
    
    :param number: Number
    :type number: int
    :param id: ID
    :type id: str
    :param beginTime: beginTime
    :type beginTime: time
    :param endTime: endTime
    :type endTime: time
    :param reason: reason
    :type reason: str
    :param user: user
    :type user: str
    :param creationTime: creationTime
    :type creationTime: datetime
    :param alarmStatus: alarm status
    :type alarmStatus: `~psym.common.data_class.alarm_status`
    """
    id: str
    name: int
    beginTime: time
    endTime: time
    reason: str
    user: str
    creationTime: datetime
    alarmStatus: int



class domain (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class tech (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param domainFk: domain Object
    :type domainFk: psym.common.data_class.domain
    """

    id: str
    name: str
    domainFK: str

class KpiCategory(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class NetworkType (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class Kpi (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param domainFk: domain Object
    :type domainFk: psym.common.data_class.domain
    :param kpiCategoryFK: str
    :type kpiCategoryFK: psym.common.data_class.kpi_category
    """

    id: str
    name: str
    description: str
    status: bool
    domain: str
    kpiCategory: str

class CounterFamily(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class Vendor (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class formula (NamedTuple):
    """
    :param textFormula: textFormula
    :type textFormula: str
    :param id: ID
    :type id: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param techFk: domain Object
    :type techFk: psym.common.data_class.tech
    :param networkTypeFk: str
    :type networkTypeFk: psym.common.data_class.network_type
    :param kpiFk: str
    :type kpiFk: psym.common.data_class.kpi
    """

    id: str
    textFormula: str
    status: bool
    techFk: str
    networkTypeFk: str
    kpiFk: str

class counter (NamedTuple):
    """
    :param name: name
    :type name: str
    :param id: ID
    :type id: str
    :param externalID: externalID
    :type externalID: str
    :param networkManagerSystem: networkManagerSystem
    :type networkManagerSystem: str
    :param counterFamilyFk: domain Object
    :type counterFamilyFk: psym.common.data_class.counter_family
    :param vendorFk: str
    :type vendorFk: psym.common.data_class.vendor
    """

    id: str
    name: str
    externalID: str
    networkManagerSystem: str
    counterFamilyFk: str
    vendorFk: str
    
class counterFormula (NamedTuple):
    """
    :param mandatory: mandatory
    :type mandatory: str
    :param id: ID
    :type id: str
    ;param counterFk: str
    :type counterFk: psym.common.data_class.counter
    :param formulaFk: str
    :type formulaFk: psym.common.data_class.formula
    """

    id: str
    mandatory: bool
    counterFk: str
    formulaFk: str

class eventSeverity (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class ruleType (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class comparator (NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class threshold (NamedTuple):
    """
    :param name: name
    :type name: str
    :param id: ID
    :type id: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param kpi: str
    :type kpi: `~psym.common.data_class.kpi`
    """

    id: str
    name: str
    description: str
    status: bool
    kpi: str

class rule (NamedTuple):
    """
    :param name: name
    :type name: str
    :param id: ID
    :type id: str
    :param gracePeriod: gracePeriod
    :type gracePeriod: str
    :param eventTypeName: eventTypeName
    :type eventTypeName: str
    :param specificProblem: specificProblem
    :type specificProblem: str
    :param additionalInfo: additionalInfo
    :type additionalInfo: str
    :param status: status
    :type status: bool
    :param ruleType: str
    :type ruleType: `~psym.common.data_class.rule_type`
    :param eventSeverity: str
    :type eventSeverity: `~psym.common.data_class.event_severity`
    :param threshold: str
    :type threshold: `~psym.common.data_class.threshold`
    """

    id: str
    name: str
    gracePeriod: int
    ruleType: str
    eventTypeName: str
    specificProblem: str
    additionalInfo: str
    status: bool
    eventSeverity: str
    threshold: str

class ruleLimit (NamedTuple):
    """
    :param number: number
    :type number: str
    :param id: ID
    :type id: str
    :param limitType: limitType
    :type limitType: str
    :param rule: rule
    :type rule: `~psym.common.data_class.rule`
    :param comparator: comparator
    :type comparator: `~psym.common.data_class.comparator`
    """

    id: int
    number: str
    limitType: str
    rule: str
    comparator: str
    

class alarmStatus(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str


class organization(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param description: Description
    :type description: str
    """

    id: str
    name: str
    description: str 

class Service(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param external_id: External ID
    :type external_id: str, optional
    :param service_type_name: Existing service type name
    :type service_type_name: str
    :param customer: Customer object
    :type customer: :class:`~psym.common.data_class.Customer`, optional
    :param properties: Properties sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property..PropertyFragment` ]
    """

    id: str
    name: str
    external_id: Optional[str]
    service_type_name: str
    customer: Optional[Customer]
    properties: Sequence[PropertyFragment]


class ServiceEndpointDefinition(NamedTuple):
    """
    :param id: ID
    :type id: str, optional
    :param name: Name
    :type name: str
    :param endpoint_definition_index: Index
    :type endpoint_definition_index: int
    :param role: Role
    :type role: str, optional
    :param equipment_type_id: Equipment type ID
    :type equipment_type_id: str
    """

    id: Optional[str]
    name: str
    endpoint_definition_index: int
    role: Optional[str]
    equipment_type_id: str


class ServiceEndpoint(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param equipment_id: Existing equipment ID
    :type equipment_id: str
    :param service_id: Existing service ID
    :type service_id: str
    :param definition_id: Existing service endpoint definition ID
    :type definition_id: str
    """

    id: str
    equipment_id: str
    service_id: str
    definition_id: str


class ServiceType(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    :param has_customer: Customer existence flag
    :type has_customer: bool
    :param property_types: PropertyDefinitions sequence
    :type property_types: Sequence[ :c;ass:`~psym.common.data_class.PropertyDefinition` ]
    :param endpoint_definitions: ServiceEndpointDefinitions list
    :type endpoint_definitions: List[ :class:`~psym.common.data_class.ServiceEndpointDefinition` ]
    """

    name: str
    id: str
    has_customer: bool
    property_types: Sequence[PropertyDefinition]
    endpoint_definitions: List[ServiceEndpointDefinition]


class Document(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Name
    :type name: str
    :param parent_id: Parent ID
    :type parent_id: str
    :param parent_entity: Parent entity
    :type parent_entity: :class:`~psym.graphql.enum.image_entity.ImageEntity`
    :param category: Category
    :type category: str, optional
    """

    id: str
    name: str
    parent_id: str
    parent_entity: ImageEntity
    category: Optional[str]
    document_category: Optional[DocumentCategory]


class User(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param auth_id: auth ID
    :type auth_id: str
    :param email: email
    :type email: str
    :param status: status
    :type status: :class:`~psym.graphql.enum.user_role.UserStatus`
    :param role: role
    :type role: :class:`~psym.graphql.enum.user_status.UserRole`
    :param organization: organization
    :type organization: :class:`~psym.graphql.data_class.organization.organization`
    """

    id: str
    auth_id: str
    email: str
    firstName: str
    lastName: str
    status: UserStatus
    role: UserRole
    organization: Optional[organization]

class RecommendationSources(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class RecommendationsCategory(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param id: ID
    :type id: str
    """

    id: str
    name: str

class recommendations (NamedTuple):
    """
    :param externalID: externalID
    :type externalID: str
    :param id: ID
    :type id: str
    :param resource: resource
    :type resource: str
    :param shortDescription: shortDescription
    :type shortDescription: str
    :param LongDescription: LongDescription
    :type LongDescription: str
    :param command: command
    :type command: str
    :param runbook: runbook
    :type runbook: str
    :param priority: priority
    :type priority: str
    :param status: status
    :type status: bool
    :param used: used
    :type used: int
    :param vendor: vendor
    :type vendor: str
    :param RecomendationSources: RecomendationSources
    :type RecomendationSources::`~psym.graphql.enum.RecomendationSources
    :param RecomendationsCategory: RecomendationsCategory
    :type RecomendationsCategory: `~psym.graphql.enum.RecomendationsCategory
    :param userCreated: userCreated
    :type userCreated:`~psym.graphql.enum.user`
    :param userApproved: userApproved
    :type userApproved:`~psym.graphql.enum.user`

    """

    id: int
    externalID: str
    resource: str
    alarmType: str
    shortDescription: str
    LongDescription: str
    command: str
    runbook: str
    priority: str
    status: bool
    used: int
    vendor: str
    RecomendationSources: str
    RecomendationsCategory: str
    userCreated: int
    userApproved: int


class SiteSurvey(NamedTuple):
    """
    :param name: Name
    :type name: str
    :param survey_id: ID
    :type survey_id: str
    :param completion_time: Complition time
    :type completion_time: datetime
    :param source_file_id: Source file ID
    :type source_file_id: str, optional
    :param source_file_name: Source file name
    :type source_file_name: str, optional
    :param source_file_key: Source file key
    :type source_file_key: str, optional
    :param forms: Forms
    :type forms: Dict[str, Dict[str, Any]]
    """

    name: str
    survey_id: str
    completion_time: datetime
    source_file_id: Optional[str]
    source_file_name: Optional[str]
    source_file_key: Optional[str]
    forms: Dict[str, Dict[str, Any]]


class WorkOrderType(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Work order type name
    :type name: str
    :param description: Work order type description
    :type description: str, optional
    :param property_types: PropertyTypes list
    :type property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    """

    id: str
    name: str
    description: Optional[str]
    property_types: Sequence[PropertyDefinition]


class WorkOrderDefinition(NamedTuple):
    """
    :param definition_index: Work order definition index
    :type definition_index: int, optional
    :param work_order_type_id: Work order type ID
    :type work_order_type_id: str
    :param id: ID
    :type id: str, optional
    """

    definition_index: Optional[int]
    work_order_type_id: str
    id: Optional[str] = None


class WorkOrder(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Name
    :type name: str
    :param description: Description
    :type description: str, optional
    :param work_order_type_name: Existing work order type name
    :type work_order_type_name: str
    :param location_id: Existing location ID
    :type location_id: str, optional
    :param project_id: Existing project ID
    :type project_id: str, optional
    :param properties: PropertyFragment sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ])
    :param owner_id: Existing user ID, work order owner
    :type owner_id: str, optional
    :param assignee_id: Existing user ID, assigned to work order
    :type assignee_id: str, optional
    :param status: Work order status
    :type status: :class:`~psym.graphql.enum.work_order_status.WorkOrderStatus`, optional
    :param priority: Work order priority
    :type priority: :class:`~psym.graphql.enum.work_order_priority.WorkOrderPriority`, optional
    :param organization: organization
    :type organization: :class:`~psym.graphql.data_class.organization`
    """

    id: str
    name: str
    description: Optional[str]
    work_order_type_name: str
    location_id: Optional[str]
    project_id: Optional[str]
    properties: Sequence[PropertyFragment]
    owner_id: Optional[str]
    assignee_id: Optional[str]
    status: Optional[WorkOrderStatus]
    priority: Optional[WorkOrderPriority]
    organization:Optional[str]


class ProjectType(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Project type name
    :type name: str
    :param description: Project type description
    :type description: str, optional
    :param property_types: PropertyTypes sequence
    :type property_types: Sequence[ :class:`~psym.common.data_class.PropertyDefinition` ]
    :param work_order_definitions: WorkOrderDefinitions list
    :type work_order_definitions: List[ :class:`~psym.common.data_class.WorkOrderDefinition` ]
    """

    id: str
    name: str
    description: Optional[str]
    property_types: Sequence[PropertyDefinition]
    work_order_definitions: List[WorkOrderDefinition]


class Project(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Project name
    :type name: str
    :param description: Project description
    :type description: str, optional
    :param priority: Project priority
    :type priority: :class:`~psym.graphql.enum.project_priority.ProjectPriority`
    :param created_by: Existing user ID, project creator
    :type created_by: str, optional
    :param project_type_name: Existing project type name
    :type project_type_name: str
    :param project_type_id: Existing project type ID
    :type project_type_id: str
    :param location_id: Existing location ID
    :type location_id: str, optional
    :param work_orders: WorkOrders list
    :type work_orders: List[ :class:`~psym.common.data_class.WorkOrder` ]
    :param properties: PropertyFragment sequence
    :type properties: Sequence[ :class:`~psym.graphql.fragment.property.PropertyFragment` ]
    """

    id: str
    name: str
    description: Optional[str]
    priority: ProjectPriority
    created_by: Optional[str]
    project_type_name: str
    project_type_id: str
    location_id: Optional[str]
    work_orders: List[WorkOrder]
    properties: Sequence[PropertyFragment]


class FlowDraft(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Flow draft name
    :type name: str
    """

    id: str
    name: str


class Flow(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param name: Flow name
    :type name: str
    """

    id: str
    name: str


class FlowInstance(NamedTuple):
    """
    :param id: ID
    :type id: str
    :param status: status
    :type status: class:`~psym.graphql.enum.flow_instance_status.FlowInstanceStatus`
    """

    id: str
    status: FlowInstanceStatus

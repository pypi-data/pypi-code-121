#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import datetime
import json
import warnings
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union, cast

from dacite import Config, from_dict

from psym.common.data_class import (
    TYPE_AND_FIELD_NAME,
    DataTypeName,
    DocumentCategory,
    PropertyDefinition,
    PropertyValue,
    ReturnType,
)
from psym.common.data_enum import Entity
from psym.graphql.input.document_category_input import DocumentCategoryInput

from .exceptions import EntityNotFoundError
from .graphql.enum.property_kind import PropertyKind
from .graphql.fragment.equipment_port_definition import EquipmentPortDefinitionFragment
from .graphql.fragment.equipment_position_definition import (
    EquipmentPositionDefinitionFragment,
)
from .graphql.fragment.property import PropertyFragment
from .graphql.input.equipment_port_input import EquipmentPortInput
from .graphql.input.equipment_position_input import EquipmentPositionInput
from .graphql.input.property_input import PropertyInput
from .graphql.input.property_type_input import PropertyTypeInput
from .graphql.input.equipment_port_connection_input import EquipmentPortConnectionInput


def format_to_type_and_field_name(type_key: str) -> Optional[DataTypeName]:
    formated = TYPE_AND_FIELD_NAME.get(type_key, None)
    return formated


def get_graphql_input_field(
    property_type_name: str, type_key: str, value: PropertyValue
) -> Dict[str, PropertyValue]:
    formated_type = format_to_type_and_field_name(type_key)
    if formated_type is None:
        raise Exception(
            f"property type {property_type_name} has not supported type {type_key}"
        )
    if type_key in ["string", "enum"]:
        assert isinstance(value, str) or isinstance(
            value, bytes
        ), f"property {property_type_name} is not of type {type_key}"
    elif type_key == "date":
        assert isinstance(
            value, datetime.date
        ), f"property {property_type_name} is not of type {type_key}"
        value = datetime.datetime.strftime(
            datetime.datetime.combine(value, datetime.datetime.min.time()), "%Y-%m-%d"
        )
    elif type_key == "datetime_local":
        assert isinstance(
            value, datetime.datetime
        ), f"property {property_type_name} is not of type {type_key}"
        value = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
    elif type_key == "gps_location":
        assert isinstance(
            value, tuple
        ), f"property {property_type_name} is not of type {type_key}"
        gps_value = value
        assert (
            len(gps_value) == 2
            and isinstance(gps_value[0], float)
            and isinstance(gps_value[1], float)
        ), f"property {property_type_name} is not of type tuple(float, float)"
        return {
            formated_type.graphql_field_name[0]: gps_value[0],
            formated_type.graphql_field_name[1]: gps_value[1],
        }
    else:
        assert isinstance(
            value, formated_type.data_type
        ), f"property {property_type_name} is not of type {type_key}"

    return {formated_type.graphql_field_name[0]: cast(PropertyValue, value)}


def update_property_input_ids(
    existing_properties: Dict[str, PropertyFragment],
    property_inputs: List[PropertyInput],
) -> List[PropertyInput]:
    new_property_inputs = []
    for p in property_inputs:
        input_id = p.id
        if p.propertyTypeID in existing_properties:
            input_id = existing_properties[p.propertyTypeID].id
        new_property_inputs.append(
            PropertyInput(
                propertyTypeID=p.propertyTypeID,
                id=input_id,
                stringValue=p.stringValue,
                intValue=p.intValue,
                booleanValue=p.booleanValue,
                floatValue=p.floatValue,
                latitudeValue=p.latitudeValue,
                longitudeValue=p.longitudeValue,
                rangeFromValue=p.rangeFromValue,
                rangeToValue=p.rangeToValue,
                nodeIDValue=p.nodeIDValue,
                isEditable=p.isEditable,
                isInstanceProperty=p.isInstanceProperty,
            )
        )
    return new_property_inputs


def get_graphql_property_type_inputs(
    property_types: Sequence[PropertyDefinition],
    properties_dict: Mapping[str, PropertyValue],
) -> List[PropertyTypeInput]:
    """This function gets existing property types and dictionary, where key - are type names, and keys - new values
    formats data, validates existence of keys from `properties_dict` in `property_types` and returns list of PropertyTypeInput

        Args:
            property_types (List[ `psym.common.data_class.PropertyDefinition` ]): list of existing property types
            properties_dict (Dict[str, PropertyValue]): dictionary of properties, where
            - str - name of existing property
            - PropertyValue - new value of existing type for this property

        Returns:
            List[ `psym.graphql.input.property_type.PropertyTypeInput` ]

        Raises:
            `psym.exceptions.EntityNotFoundError`: if there any unknown property name in `properties_dict` keys
    """
    properties = []
    property_type_names = {}
    for property_type in property_types:
        property_type_names[property_type.property_name] = property_type
    for name, value in properties_dict.items():
        if name not in property_type_names:
            raise EntityNotFoundError(entity=Entity.PropertyType, entity_name=name)
        property_type_id = property_type_names[name].id
        assert property_type_id is not None, f"property {name} has no id"
        assert not property_type_names[name].is_fixed, f"property {name} is fixed"
        result: Dict[str, Union[PropertyValue, PropertyKind]] = {
            "id": property_type_id,
            "name": name,
            "type": PropertyKind(property_type_names[name].property_kind),
        }
        result.update(
            get_graphql_input_field(
                property_type_name=name,
                type_key=property_type_names[name].property_kind.value,
                value=value,
            )
        )
        properties.append(
            from_dict(
                data_class=PropertyTypeInput, data=result, config=Config(strict=True)
            )
        )

    return properties


def get_graphql_document_category_inputs(
    document_categories: Sequence[DocumentCategory],
    categories_name_dict: Mapping[str, str],
) -> List[DocumentCategoryInput]:
    """This function gets existing document categories and dictionary, where key - are current names, and keys - new name,
    validates existence of keys from `categories_name_dict` in `document_categories` and returns list of DocumentCategoryInput

        Args:
            document_categories (List[ `psym.common.data_class.DocumentCategory` ]): list of existing document categories
            categories_name_dict (Dict[str, str]): dictionary of categories name, where
            - str - name of existing category
            - str - new document category name

        Returns:
            List[ `psym.graphql.input.document_category.DocumentCategoryInput` ]

        Raises:
            `psym.exceptions.EntityNotFoundError`: if there any unknown category name in `categories_name_dict` keys
    """
    document_categories_list = []
    document_category_names = {}
    for doc_category in document_categories:
        document_category_names[doc_category.name] = doc_category
    for name, value in categories_name_dict.items():
        if name not in document_category_names:
            raise EntityNotFoundError(entity=Entity.DocumentCategory, entity_name=name)
        document_category_id = document_category_names[name].id
        document_category_index = document_category_names[name].dc_index
        assert document_category_id is not None, f"document category {name} has no id"
        result: Dict[str, str] = {
            "id": document_category_id,
            "index": document_category_index,
            "name": value,
        }

        document_categories_list.append(
            from_dict(
                data_class=DocumentCategoryInput,
                data=result,
                config=Config(strict=True),
            )
        )

    return document_categories_list


def get_graphql_property_inputs(
    property_types: Sequence[PropertyDefinition],
    properties_dict: Mapping[str, PropertyValue],
) -> List[PropertyInput]:
    """This function gets existing property types and dictionary, where key - are type names, and keys - new values
    formats data, validates existence of keys from `properties_dict` in `property_types` and returns list of PropertyInput

        Args:
            property_types (Sequence[ `psym.common.data_class.PropertyDefinition` ]): list of existing property types
            properties_dict (Mapping[str, PropertyValue]): dictionary of properties, where
                str: name of existing property
                PropertyValue: new value of existing type for this property

        Returns:
            List[ `psym.graphql.input.property.PropertyInput` ]

        Raises:
            `psym.exceptions.EntityNotFoundError`: if there any unknown property name in properties_dict keys

        Example:
            ```
            property_types = LOCATION_TYPES[location_type].property_types
            properties = get_graphql_property_inputs(property_types, properties_dict)
            ```
    """
    properties = []
    property_type_names = {}

    for property_type in property_types:
        property_type_names[property_type.property_name] = property_type

    for name, value in properties_dict.items():
        if name not in property_type_names:
            raise EntityNotFoundError(entity=Entity.PropertyType, entity_name=name)
        property_type_id = property_type_names[name].id
        assert property_type_id is not None, f"property {name} has no id"
        assert not property_type_names[name].is_fixed, f"property {name} is fixed"
        pk = property_type_names[name].property_kind
        if pk == PropertyKind.enum:
            def_raw_val = property_type_names[name].default_raw_value
            if def_raw_val is None:
                def_raw_val = ""
            values = json.loads(def_raw_val)
            assert value in values, f"{value} is not in {values}"
        result: Dict[str, PropertyValue] = {"propertyTypeID": property_type_id}
        result.update(
            get_graphql_input_field(
                property_type_name=name,
                type_key=property_type_names[name].property_kind.value,
                value=value,
            )
        )
        properties.append(
            from_dict(data_class=PropertyInput, data=result, config=Config(strict=True))
        )

    return properties


def _get_property_value(
    property_type: str, property: PropertyFragment
) -> Tuple[PropertyValue, ...]:
    formated_name = format_to_type_and_field_name(property_type)
    if formated_name is None:
        raise AssertionError(f"Unknown property type - {property_type}")

    str_fields = formated_name.graphql_field_name
    values = []
    for str_field in str_fields:
        field_data = property.__dict__[str_field]
        if property_type == "date":
            values.append(
                datetime.datetime.strptime(cast(str, field_data), "%Y-%m-%d").date()
            )
        elif property_type == "datetime_local":
            values.append(
                datetime.datetime.strptime(cast(str, field_data), "%Y-%m-%d %H:%M:%S")
            )
        else:
            values.append(field_data)
    return tuple(value for value in values)


def get_position_definition_input(
    position_definition: EquipmentPositionDefinitionFragment, is_new: bool = True
) -> EquipmentPositionInput:
    return EquipmentPositionInput(
        name=position_definition.name,
        id=position_definition.id if not is_new else None,
        index=position_definition.index,
        visibleLabel=position_definition.visibleLabel,
    )


def get_port_definition_input(
    port_definition: EquipmentPortDefinitionFragment, is_new: bool = True
) -> EquipmentPortInput:
    return EquipmentPortInput(
        name=port_definition.name,
        id=port_definition.id if not is_new else None,
        index=port_definition.index,
        visibleLabel=port_definition.visibleLabel,
        portTypeID=port_definition.portType.id if port_definition.portType else None,
        connectedPorts=[
            EquipmentPortConnectionInput(id=port.id, name=port.name)
            for port in port_definition.connectedPorts
        ],
    )


def deprecated(
    deprecated_in: str,
    deprecated_by: str
    # pyre-fixme[34]: `Variable[ReturnType]` isn't present in the function's parameters.
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    def wrapped(func: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        def wrapper(*args: str, **kwargs: int) -> Callable[..., ReturnType]:
            func_name = func.__name__
            message = f"{func_name} is deprecated in {deprecated_in}. Use the {deprecated_by} function instead."
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return cast(Callable[..., ReturnType], func(*args, **kwargs))

        return cast(Callable[..., ReturnType], wrapper)

    return wrapped

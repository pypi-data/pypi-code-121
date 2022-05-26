from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING, Dict, Optional, Type, Union

from sila2.framework.abc.named_node import NamedNode
from sila2.framework.command.command import Command
from sila2.framework.command.observable_command import ObservableCommand
from sila2.framework.command.unobservable_command import UnobservableCommand
from sila2.framework.data_types.data_type_definition import DataTypeDefinition
from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedFeatureIdentifier, FullyQualifiedIdentifier
from sila2.framework.metadata import Metadata
from sila2.framework.pb2.custom_protocols import FeatureProtobufModule
from sila2.framework.property.observable_property import ObservableProperty
from sila2.framework.property.property import Property
from sila2.framework.property.unobservable_property import UnobservableProperty
from sila2.framework.utils import (
    feature_definition_to_modules,
    parse_feature_definition,
    xml_node_to_normalized_string,
    xpath_sila,
)

if TYPE_CHECKING:
    from sila2.framework.abc.binary_transfer_handler import BinaryTransferHandler
    from sila2.framework.utils import HasFullyQualifiedIdentifier


class Feature(NamedNode):
    _feature_definition: str
    fully_qualified_identifier: FullyQualifiedFeatureIdentifier
    """Fully qualified feature identifier"""
    _sila2_version: str
    _feature_version: str
    _maturity_level: str
    _locale: str
    _originator: str
    _category: str
    _pb2_module: FeatureProtobufModule
    _grpc_module: ModuleType
    _servicer_cls: Type
    _observable_properties: Dict[str, ObservableProperty]
    _unobservable_properties: Dict[str, UnobservableProperty]
    _observable_commands: Dict[str, ObservableCommand]
    _unobservable_commands: Dict[str, UnobservableCommand]
    _data_type_definitions: Dict[str, DataTypeDefinition]
    defined_execution_errors: Dict[str, DefinedExecutionErrorNode]
    metadata_definitions: Dict[str, Metadata]
    _binary_transfer_handler: Optional[BinaryTransferHandler]
    children_by_fully_qualified_identifier: Dict[
        FullyQualifiedIdentifier,
        HasFullyQualifiedIdentifier,
    ]
    """All child elements, accessible by their fully qualified identifier"""

    def __init__(self, feature_definition: str) -> None:
        """
        Represents a SiLA feature

        Parameters
        ----------
        feature_definition
            Feature definition (XML) as string, or path to a feature definition file
        """
        self._fdl_node = parse_feature_definition(feature_definition)
        super().__init__(self._fdl_node)

        self._feature_definition = xml_node_to_normalized_string(self._fdl_node)

        self._sila2_version = self._fdl_node.attrib["SiLA2Version"]
        self._feature_version = self._fdl_node.attrib["FeatureVersion"]
        self._originator = self._fdl_node.attrib["Originator"]
        self._maturity_level = self._fdl_node.attrib.get("MaturityLevel", default="Draft")
        self._locale = self._fdl_node.attrib.get("Locale", default="en-us")
        self._category = self._fdl_node.attrib.get("Category", default="none")
        self.fully_qualified_identifier = FullyQualifiedFeatureIdentifier(
            f"{self._originator}/{self._category}/{self._identifier}/v{self._feature_version.split('.')[0]}"
        )

        self._pb2_module, self._grpc_module = feature_definition_to_modules(self._fdl_node)
        self._servicer_cls = getattr(self._grpc_module, f"{self._identifier}Servicer")

        self.children_by_fully_qualified_identifier = {}

        self.defined_execution_errors = {}
        for err_node in xpath_sila(self._fdl_node, "sila:DefinedExecutionError"):
            err = DefinedExecutionErrorNode(err_node, self)
            self.defined_execution_errors[err._identifier] = err
            self.children_by_fully_qualified_identifier[err.fully_qualified_identifier] = err

        self._data_type_definitions = {}
        data_type_definition_nodes = list(xpath_sila(self._fdl_node, "sila:DataTypeDefinition"))
        failed_nodes = []
        while data_type_definition_nodes:
            num_nodes = len(data_type_definition_nodes)

            for dtype_node in data_type_definition_nodes:
                try:
                    dtype = DataTypeDefinition(dtype_node, self)
                    self._data_type_definitions[dtype._identifier] = dtype
                    self.children_by_fully_qualified_identifier[dtype.fully_qualified_identifier] = dtype
                except KeyError:
                    failed_nodes.append(dtype_node)

            if num_nodes == len(failed_nodes):  # pragma: no cover
                identifiers = [NamedNode(node)._identifier for node in failed_nodes]
                raise ValueError(
                    f"Feature definition contains cyclic dependencies between data type definitions {identifiers}"
                )

            data_type_definition_nodes = failed_nodes
            failed_nodes = []

        self._observable_properties = {}
        self._unobservable_properties = {}
        for prop_node in xpath_sila(self._fdl_node, "sila:Property"):
            prop = Property.from_fdl_node(prop_node, self)
            self.children_by_fully_qualified_identifier[prop.fully_qualified_identifier] = prop
            if isinstance(prop, ObservableProperty):
                self._observable_properties[prop._identifier] = prop
            elif isinstance(prop, UnobservableProperty):
                self._unobservable_properties[prop._identifier] = prop
            else:
                raise NotImplementedError  # pragma: no cover

        self._observable_commands = {}
        self._unobservable_commands = {}
        for command_node in xpath_sila(self._fdl_node, "sila:Command"):
            cmd = Command.from_fdl_node(command_node, self)
            self.children_by_fully_qualified_identifier[cmd.fully_qualified_identifier] = cmd
            for param in cmd.parameters:
                self.children_by_fully_qualified_identifier[param.fully_qualified_identifier] = param
            for resp in cmd.responses:
                self.children_by_fully_qualified_identifier[resp.fully_qualified_identifier] = resp
            if isinstance(cmd, ObservableCommand):
                self._observable_commands[cmd._identifier] = cmd
                if cmd.intermediate_responses is not None:
                    for int_resp in cmd.intermediate_responses:
                        self.children_by_fully_qualified_identifier[int_resp.fully_qualified_identifier] = int_resp
            elif isinstance(cmd, UnobservableCommand):
                self._unobservable_commands[cmd._identifier] = cmd
            else:
                raise NotImplementedError  # pragma: no cover

        self.metadata_definitions = {}
        for meta_node in xpath_sila(self._fdl_node, "sila:Metadata"):
            meta = Metadata(meta_node, self)
            self.metadata_definitions[meta._identifier] = meta
            self.children_by_fully_qualified_identifier[meta.fully_qualified_identifier] = meta

        self._binary_transfer_handler = None

    def __getitem__(self, identifier: str) -> Union[Property, Command, Metadata]:
        """
        Get a property, command or metadata child element by its identifier

        Parameters
        ----------
        identifier
            Property, command, or metadata identifier
        Returns
        -------
        child_element
            Child element with the given identifier

        Raises
        ------
        KeyError
            If no such child element exists
        """
        if identifier in self._unobservable_properties:
            return self._unobservable_properties[identifier]
        if identifier in self._observable_properties:
            return self._observable_properties[identifier]
        if identifier in self._unobservable_commands:
            return self._unobservable_commands[identifier]
        if identifier in self._observable_commands:
            return self._observable_commands[identifier]
        if identifier in self.metadata_definitions:
            return self.metadata_definitions[identifier]
        raise KeyError(f"Feature '{self._identifier}' has no child command, property or metadata '{identifier}'")

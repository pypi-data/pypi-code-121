from __future__ import annotations

import itertools as it
import os
from os.path import join
from typing import List

from sila2.code_generator.code_generator_base import CodeGeneratorBase
from sila2.code_generator.template_objects.base import (
    ServerMetadata,
    ServerObservableCommand,
    ServerObservableProperty,
    ServerUnobservableCommand,
    ServerUnobservableProperty,
)
from sila2.code_generator.template_objects.basics import Field, Type
from sila2.code_generator.template_objects.client import (
    ClientMetadata,
    ClientObservableCommand,
    ClientObservableProperty,
    ClientUnobservableCommand,
    ClientUnobservableProperty,
)
from sila2.code_generator.template_objects.types import CompositeType, CompositeTypeField, TypeDefinition
from sila2.framework.data_types.data_type_definition import DataTypeDefinition
from sila2.framework.feature import Feature
from sila2.framework.utils import feature_definition_to_proto_string, prettify_xml_string


class FeatureGenerator(CodeGeneratorBase):
    feature: Feature

    def __init__(self, feature: Feature, overwrite: bool) -> None:
        super().__init__(overwrite=overwrite)
        self.feature = feature
        self.feature_id_lowercase = feature._identifier.lower()

    def generate_feature_files(self, out_dir: str) -> None:
        os.makedirs(out_dir, exist_ok=True)

        self.generate_file(
            out_filename=join(out_dir, f"{self.feature._identifier}.sila.xml"),
            content=prettify_xml_string(self.feature._feature_definition),
        )
        self.generate_file(
            out_filename=join(out_dir, f"{self.feature._identifier}.proto"),
            content=feature_definition_to_proto_string(self.feature._fdl_node),
        )
        self.generate_feature(out_dir)
        self.generate_client(out_dir)
        self.generate_base(out_dir)
        self.generate_init(out_dir)
        self.generate_errors(out_dir)
        self.generate_types(out_dir)

    def generate_errors(self, out_dir: str) -> None:
        content = self.template_env.get_template("feature/errors").render(
            feature=self.feature, errors=self.feature.defined_execution_errors.values()
        )
        self.generate_file(join(out_dir, f"{self.feature_id_lowercase}_errors.py"), content, allow_overwrite=True)

    def generate_init(self, out_dir: str) -> None:
        content = self.template_env.get_template("feature/init").render(feature=self.feature)
        self.generate_file(join(out_dir, "__init__.py"), content, allow_overwrite=True)

    def generate_feature(self, out_dir: str) -> None:
        content = self.template_env.get_template("feature/feature").render(feature=self.feature)
        self.generate_file(join(out_dir, f"{self.feature_id_lowercase}_feature.py"), content, allow_overwrite=True)

    def generate_types(self, out_dir: str) -> None:
        message_types: List[CompositeType] = []
        for cmd in it.chain(
            self.feature._unobservable_commands.values(),
            self.feature._observable_commands.values(),
        ):
            message_types.append(
                CompositeType(
                    f"{cmd._identifier}_Responses", [CompositeTypeField.from_field(f) for f in cmd.responses.fields]
                )
            )
        for cmd in self.feature._observable_commands.values():
            if cmd.intermediate_responses:
                message_types.append(
                    CompositeType(
                        f"{cmd._identifier}_IntermediateResponses",
                        [CompositeTypeField.from_field(f) for f in cmd.intermediate_responses.fields],
                    )
                )

        definitions = [
            TypeDefinition(t._identifier, Type.from_data_type(t.data_type))
            for t in self.feature._data_type_definitions.values()
        ]

        content = self.template_env.get_template("feature/types").render(
            named_tuples=message_types,
            data_type_definitions=definitions,
        )
        self.generate_file(join(out_dir, f"{self.feature_id_lowercase}_types.py"), content, allow_overwrite=True)

    def __generate_base_or_impl_str(self, generate_impl: bool) -> str:
        metadata = [ServerMetadata(m._identifier, m._description) for m in self.feature.metadata_definitions.values()]
        unobservable_properties = [
            ServerUnobservableProperty(p._identifier, Type.from_data_type(p.data_type), p._description)
            for p in self.feature._unobservable_properties.values()
        ]
        observable_properties = [
            ServerObservableProperty(p._identifier, Type.from_data_type(p.data_type), p._description)
            for p in self.feature._observable_properties.values()
        ]
        unobservable_commands = [
            ServerUnobservableCommand(
                cmd._identifier,
                [Field(p._identifier, Type.from_data_type(p.data_type), p._description) for p in cmd.parameters],
                [Field(r._identifier, Type.from_data_type(r.data_type), r._description) for r in cmd.responses],
                cmd._description,
            )
            for cmd in self.feature._unobservable_commands.values()
        ]
        observable_commands = [
            ServerObservableCommand(
                cmd._identifier,
                [Field(p._identifier, Type.from_data_type(p.data_type), p._description) for p in cmd.parameters],
                [
                    Field(i._identifier, Type.from_data_type(i.data_type), i._description)
                    for i in cmd.intermediate_responses
                ]
                if cmd.intermediate_responses is not None
                else [],
                [Field(r._identifier, Type.from_data_type(r.data_type), r._description) for r in cmd.responses],
                cmd._description,
            )
            for cmd in self.feature._observable_commands.values()
        ]
        imports = []
        for obj in it.chain(unobservable_properties, observable_properties, unobservable_commands, observable_commands):
            if isinstance(obj, ServerObservableProperty) and generate_impl:
                continue
            imports.extend(obj.imports)

        definition_imports = []
        for cmd in it.chain(self.feature._unobservable_commands.values(), self.feature._observable_commands.values()):
            for param in cmd.parameters:
                if isinstance(param.data_type, DataTypeDefinition):
                    definition_imports.append(param.data_type._identifier)

        return self.template_env.get_template("feature/impl" if generate_impl else "feature/base").render(
            feature=self.feature,
            imports=imports,
            metadata=metadata,
            unobservable_properties=unobservable_properties,
            observable_properties=observable_properties,
            unobservable_commands=unobservable_commands,
            observable_commands=observable_commands,
            definition_imports=definition_imports,
        )

    def generate_base(self, out_dir: str) -> None:
        content = self.__generate_base_or_impl_str(generate_impl=False)
        self.generate_file(join(out_dir, f"{self.feature_id_lowercase}_base.py"), content, allow_overwrite=True)

    def generate_impl(self, out_dir: str, *, prefix: str = "") -> None:
        content = self.__generate_base_or_impl_str(generate_impl=True)
        self.generate_file(join(out_dir, f"{prefix}{self.feature_id_lowercase}_impl.py"), content)

    def generate_client(self, out_dir: str) -> None:
        metadata = [
            ClientMetadata(m._identifier, m._description, Type.from_data_type(m.data_type))
            for m in self.feature.metadata_definitions.values()
        ]

        unobservable_properties = [
            ClientUnobservableProperty(prop._identifier, Type.from_data_type(prop.data_type), prop._description)
            for prop in self.feature._unobservable_properties.values()
        ]
        observable_properties = [
            ClientObservableProperty(prop._identifier, Type.from_data_type(prop.data_type), prop._description)
            for prop in self.feature._observable_properties.values()
        ]
        unobservable_commands = [
            ClientUnobservableCommand(
                cmd._identifier,
                [
                    Field(par._identifier, Type.from_data_type(par.data_type), par._description)
                    for par in cmd.parameters
                ],
                cmd._description,
            )
            for cmd in self.feature._unobservable_commands.values()
        ]
        observable_commands = [
            ClientObservableCommand(
                cmd._identifier,
                [
                    Field(par._identifier, Type.from_data_type(par.data_type), par._description)
                    for par in cmd.parameters
                ],
                cmd._description,
                bool(cmd.intermediate_responses),
            )
            for cmd in self.feature._observable_commands.values()
        ]

        imports = []
        for obj in it.chain(
            unobservable_properties, observable_properties, unobservable_commands, observable_commands, metadata
        ):
            imports.extend(obj.imports)

        definition_imports = []
        for cmd in it.chain(self.feature._unobservable_commands.values(), self.feature._observable_commands.values()):
            for param in cmd.parameters:
                if isinstance(param.data_type, DataTypeDefinition):
                    definition_imports.append(param.data_type._identifier)

        content = self.template_env.get_template("feature/client").render(
            feature=self.feature,
            imports=imports,
            metadata=metadata,
            unobservable_properties=unobservable_properties,
            observable_properties=observable_properties,
            unobservable_commands=unobservable_commands,
            observable_commands=observable_commands,
            definition_imports=definition_imports,
        )
        self.generate_file(join(out_dir, f"{self.feature_id_lowercase}_client.py"), content, allow_overwrite=True)

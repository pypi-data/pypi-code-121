from __future__ import annotations

from typing import List, NamedTuple, Union

from sila2.code_generator.template_objects.basics import Import, Type
from sila2.framework.command.intermediate_response import IntermediateResponse
from sila2.framework.command.response import Response
from sila2.framework.data_types.structure import StructureElement


class CompositeType(NamedTuple):
    name: str
    fields: List[CompositeTypeField]

    @property
    def imports(self) -> List[Import]:
        ret = []
        for field in self.fields:
            ret.extend(field.imports)
        return ret


class CompositeTypeField(NamedTuple):
    name: str
    description: str
    type: Type

    @classmethod
    def from_field(cls, field: Union[Response, IntermediateResponse, StructureElement]) -> CompositeTypeField:
        return cls(field._identifier, field._description, Type.from_data_type(field.data_type))

    @property
    def imports(self) -> List[Import]:
        return self.type.imports


class TypeDefinition(NamedTuple):
    name: str
    type: Type

    @property
    def imports(self) -> List[Import]:
        return self.type.imports

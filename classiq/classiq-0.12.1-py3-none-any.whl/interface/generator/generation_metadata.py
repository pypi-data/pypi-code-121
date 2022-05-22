from typing import Any, Dict, List, Optional, Type

import pydantic
from typing_extensions import Literal

from classiq.interface.generator.function_param_list import get_param_metadata_list
from classiq.interface.generator.function_params import ParamMetadata

from classiq.exceptions import ClassiqInvalidMetadataError

_INVALID_METADATA_ERROR_MSG = "Invalid metadata file."


class FunctionMetadata(pydantic.BaseModel):
    metadata_type: Literal["function"] = "function"
    name: str
    parent: Optional[str]
    children: List[str]
    hierarchy_level: int
    _parents: Dict[int, str] = pydantic.PrivateAttr(default={})

    def add_parents(self, parents: Dict[int, str]):
        for parent_hierarchy_level in parents.keys():
            if parent_hierarchy_level >= self.hierarchy_level:
                raise ValueError("Parent's hierarchy level must be lower than child's")
        self._parents.update(parents)

    @property
    def parents(self):
        return self._parents


class GenerationMetadata(pydantic.BaseModel):
    # Ideally, we would use a "__root__" attribute, but the typescript transpilation
    # does weird things when we use it.
    metadata_type: str = ""
    metadata: ParamMetadata

    @pydantic.validator("metadata", pre=True)
    def parse_metadata(
        cls, metadata: Dict[str, Any], values: Dict[str, Any]
    ) -> ParamMetadata:
        if isinstance(metadata, ParamMetadata):
            values["metadata_type"] = type(metadata).__name__
            return metadata

        type_name = values.get("metadata_type")
        metadata_list: List[Type[ParamMetadata]] = [
            metadata_type
            for metadata_type in get_param_metadata_list()
            if metadata_type.__name__ == type_name
        ]

        if len(metadata_list) != 1:
            raise ClassiqInvalidMetadataError(_INVALID_METADATA_ERROR_MSG)

        return metadata_list[0].parse_obj(metadata)

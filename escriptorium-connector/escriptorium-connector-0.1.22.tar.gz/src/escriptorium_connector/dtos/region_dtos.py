from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from dataclasses import field
from typing import List, Union


@dataclass(init=True, frozen=True)
class PostRegionType:
    name: str


@dataclass(init=True, frozen=True)
class GetRegionType:
    pk: int
    name: str


@dataclass
class GetRegionTypes(PagenatedResponse):
    results: List[GetRegionType] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class PostRegion:
    document_part: int
    external_id: str
    box: List[List[int]]
    typology: int


@dataclass(init=True, frozen=True)
class GetRegion:
    pk: int
    document_part: int
    external_id: str
    order: int
    box: List[List[int]]
    typology: Union[int, None]


@dataclass
class GetRegions(PagenatedResponse):
    results: List[GetRegion] = field(default_factory=list)

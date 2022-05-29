from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from dataclasses import field
from datetime import datetime
from typing import List, Union, Any

from escriptorium_connector.dtos.super_dtos import PagenatedResponse


@dataclass(init=True, frozen=True)
class PostProject:
    name: str
    shared_with_users: List[int] = field(default_factory=list)
    shared_with_groups: List[int] = field(default_factory=list)


# @dataclass(init=True, frozen=True)
# class PostProject:
#     csrfmiddlewaretoken: str
#     name: str


@dataclass(init=True, frozen=True)
class PutProject:
    name: str
    shared_with_users: List[int] = field(default_factory=list)
    shared_with_groups: List[int] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class GetProject:
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime
    owner: Union[str, int, None]
    shared_with_users: List[int] = field(default_factory=list)
    shared_with_groups: List[int] = field(default_factory=list)


@dataclass
class GetProjects(PagenatedResponse):
    results: List[GetProject] = field(default_factory=list)

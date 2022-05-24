from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from typing import Union, List
from datetime import datetime
from dataclasses import field


@dataclass(init=True, frozen=True)
class CharacterGraph:
    c: str
    poly: List[List[int]]
    confidence: float


@dataclass(init=True, frozen=True)
class PostAbbreviatedTranscription:
    name: str


@dataclass(init=True, frozen=True)
class GetAbbreviatedTranscription:
    pk: int
    name: str
    archived: bool = False


@dataclass(init=True, frozen=True)
class PostTranscription:
    line: int
    transcription: int
    content: str
    graphs: List[CharacterGraph] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class GetVersionData:
    graphs: Union[None, List[List[int]]]
    content: str


@dataclass(init=True, frozen=True)
class GetVersion:
    data: GetVersionData
    author: str
    source: str
    revision: str
    created_at: datetime
    updated_at: datetime


@dataclass(init=True, frozen=True)
class GetTranscription:
    pk: int
    line: int
    transcription: int
    content: str
    versions: List[GetVersion]
    version_author: str
    version_source: str
    version_updated_at: datetime
    graphs: List[CharacterGraph] = field(default_factory=list)


@dataclass
class GetTranscriptions(PagenatedResponse):
    results: List[GetTranscription] = field(default_factory=list)

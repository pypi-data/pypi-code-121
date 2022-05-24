from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from escriptorium_connector.dtos.transcription_dtos import GetTranscription
from typing import List, Union
from dataclasses import field


@dataclass(init=True, frozen=True)
class PostLine:
    document_part: int
    external_id: Union[str, None] = None
    region: Union[int, None] = None
    baseline: Union[List[List[int]], None] = None
    mask: Union[List[List[int]], None] = None
    typology: Union[int, None] = None

@dataclass(init=True, frozen=True)
class PutLine:
    document_part: int
    external_id: Union[str, None] = None
    region: Union[int, None] = None
    baseline: Union[List[List[int]], None] = None
    mask: Union[List[List[int]], None] = None
    typology: Union[int, None] = None


@dataclass(init=True, frozen=True)
class GetLine:
    pk: int
    document_part: int
    external_id: str
    order: int
    region: Union[int, None]
    baseline: List[List[int]]
    mask: Union[List[List[int]], None]
    typology: Union[int, None] = None
    transcriptions: Union[List[GetTranscription], None] = None


@dataclass
class GetLines(PagenatedResponse):
    results: List[GetLine] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class PostLineType:
    name: str


@dataclass(init=True, frozen=True)
class GetLineType:
    pk: int
    name: str


@dataclass
class GetLineTypes(PagenatedResponse):
    results: List[GetLineType] = field(default_factory=list)

@dataclass(init=True, frozen=True)
class PostMoveLine:
    pk: int
    order: int

@dataclass(init=True, frozen=True)
class PostMoveLines:
    lines: List[PostMoveLine] = field(default_factory=list)

@dataclass(init=True, frozen=True)
class PutBulkUpdateLines:
    status: str
    lines: list[GetLine] = field(default_factory=list)

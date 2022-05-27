from dataclasses import field
from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from enum import Enum
from typing import List, Union
from datetime import datetime

from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from escriptorium_connector.dtos.transcription_dtos import GetAbbreviatedTranscription
from escriptorium_connector.dtos.region_dtos import GetRegionType
from escriptorium_connector.dtos.line_dtos import GetLineType


class ReadDirection(str, Enum):
    LTR = "ltr"
    RTL = "rtl"


class LineOffset(int, Enum):
    BASELINE = 0
    TOPLINE = 1
    CENTERED = 2


@dataclass(init=True, frozen=True)
class PostDocument:
    name: str
    project: str
    main_script: Union[str, None]
    read_direction: ReadDirection
    line_offset: LineOffset
    tags: List[str] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class PutDocument:
    name: str
    project: str
    main_script: Union[str, None]
    read_direction: ReadDirection
    line_offset: LineOffset
    tags: List[str] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class GetDocument:
    pk: int
    name: str
    project: str
    main_script: Union[str, None]
    read_direction: ReadDirection
    line_offset: LineOffset
    parts_count: int
    created_at: datetime
    updated_at: datetime
    transcriptions: List[GetAbbreviatedTranscription] = field(default_factory=list)
    valid_block_types: List[GetRegionType] = field(default_factory=list)
    valid_line_types: List[GetLineType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class GetDocuments(PagenatedResponse):
    results: List[GetDocument] = field(default_factory=list)

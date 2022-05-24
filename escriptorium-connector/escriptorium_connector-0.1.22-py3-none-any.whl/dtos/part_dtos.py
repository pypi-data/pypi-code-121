from dataclasses import field
from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from typing import List, Union, Dict

from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from escriptorium_connector.dtos.region_dtos import GetRegion
from escriptorium_connector.dtos.line_dtos import GetLine


@dataclass(init=True, frozen=True)
class Thumbnail:
    card: Union[str, None] = None
    large: Union[str, None] = None


@dataclass(init=True, frozen=True)
class Image:
    uri: str
    size: List[int]
    thumbnails: Thumbnail


@dataclass(init=True, frozen=True)
class Workflow:
    convert: Union[str, None] = None
    segment: Union[str, None] = None
    transcribe: Union[str, None] = None


@dataclass(init=True, frozen=True)
class PostPart:
    name: str
    typology: Union[int, None]
    source: str


@dataclass(init=True, frozen=True)
class PutPart:
    name: str
    typology: Union[int, None]
    source: str

@dataclass(init=True, frozen=True)
class GetPart:
    pk: int
    name: str
    filename: str
    title: str
    typology: Union[int, None]
    image: Image
    image_file_size: int
    bw_image: Union[Image, None]
    order: int
    recoverable: bool
    transcription_progress: int
    source: str
    workflow: Union[Workflow, None] = None
    regions: Union[List[GetRegion], None] = None
    lines: Union[List[GetLine], None] = None
    previous: Union[int, None] = None
    next: Union[int, None] = None


@dataclass
class GetParts(PagenatedResponse):
    results: List[GetPart] = field(default_factory=list)

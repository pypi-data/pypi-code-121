from __future__ import annotations
import json
import uuid
import base64
import pathlib
import os.path
import textwrap
import datetime
from typing import Optional, Any
from pydantic import BaseModel, validator, constr
from .utils import get_mimetype


class FileDefinitionModel(BaseModel):
    name: str
    mimeType: str
    contents: Optional[constr(max_length=1431655765)] = None  # type: ignore
    userId: Optional[str] = None
    metadata: Optional[dict] = None
    fileSize: Optional[int] = None
    id: Optional[uuid.UUID] = None
    created: Optional[datetime.datetime] = None
    updated: Optional[datetime.datetime] = None

    @validator("name")
    def _shorten_name_len(cls, value: Any) -> str:
        if value and len(value) > 100:
            name, ext = os.path.splitext(value)
            name = textwrap.shorten(name, width=(100 - len(ext)), placeholder="")
            return f"{name}{ext}"
        return value

    @validator("id")
    def _uuid_as_str(cls, value: Any) -> Optional[str]:
        if value:
            return str(value)
        return value

    def dump(self) -> dict:
        return json.loads(self.json(by_alias=True))

    @classmethod
    def from_file(
        cls, file_path: pathlib.Path, mime_type: str = None, **kwargs: Any
    ) -> FileDefinitionModel:
        return cls(
            name=file_path.name,
            mimeType=(mime_type or get_mimetype(file_path)),
            contents=base64.b64encode(file_path.read_bytes()).decode(),
            **kwargs,
        )

    def get_bytes(self) -> bytes:
        if not self.contents:
            return b""
        return base64.b64decode(self.contents)


class FileResourceModel(BaseModel):
    id: Optional[str] = None
    fileName: Optional[str] = None
    friendlyFileName: Optional[str] = None
    fileLength: int = 0
    hash: Optional[str] = None
    location: Optional[str] = None
    created: Optional[datetime.datetime] = None
    updated: Optional[datetime.datetime] = None

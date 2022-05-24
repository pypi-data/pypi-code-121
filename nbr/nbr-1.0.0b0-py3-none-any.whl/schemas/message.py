from datetime import datetime
from typing import Union
from uuid import uuid4

from pydantic import BaseModel


class Metadata(BaseModel):
    cellId: str = uuid4().hex
    deletedCells: list = []
    recordTiming: bool = False


class Content(BaseModel):
    allow_stdin: bool = False
    code: str = ""
    silent: bool = False
    stop_on_error: bool = True
    store_history: bool = True
    user_expressions: dict = {}


class Header(BaseModel):
    date: str = str(datetime.utcnow())
    msg_id: str = uuid4().hex
    msg_type: str
    session: str
    username: str = ""
    version: str = "5.2"


class Message(BaseModel):
    buffers: list = []
    channel: str
    content: Union[Content, dict]
    header: Header
    metadata: Union[Metadata, dict]
    parent_header: dict = {}

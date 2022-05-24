from typing import List

from pydantic import BaseModel

from .record_from_server import RecordFromServer


class RecordsList(BaseModel):
    records: List[RecordFromServer]


class HttpRecordBatchWrite(BaseModel):
    body: RecordsList

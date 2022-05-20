import json
from pathlib import Path
from typing import Dict, Optional

from requests_toolbelt import MultipartEncoder

from fiddler.v2.constants import FiddlerTimestamp, FileType
from fiddler.v2.schema.base import BaseDataSchema


class EventsIngest(BaseDataSchema):
    events_path: Path
    batch_id: Optional[str] = None
    events_schema: Optional[dict] = None
    id_field: Optional[str] = None
    is_update: Optional[bool] = None
    timestamp_field: Optional[str] = None
    timestamp_format: Optional[FiddlerTimestamp] = None
    group_by: Optional[str] = None
    file_type: Optional[FileType] = None

    class Config:
        use_enum_values = True

    def multipart_form_request(self) -> Dict[dict, bytes]:
        request_body_json = self.dict(exclude={'events_path'})
        request_body = {
            'json': (None, json.dumps(request_body_json), 'application/json'),
            self.events_path.name: (
                self.events_path.name,
                open(self.events_path, 'rb'),
            ),
        }
        m = MultipartEncoder(fields=request_body)
        return m.content_type, m


class EventIngest(BaseDataSchema):
    event: dict
    event_id: Optional[str] = None
    id_field: Optional[str] = None
    is_update: Optional[bool] = None
    event_timestamp: Optional[str] = None
    timestamp_format: Optional[FiddlerTimestamp] = None

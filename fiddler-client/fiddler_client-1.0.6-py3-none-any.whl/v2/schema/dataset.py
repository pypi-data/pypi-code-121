import json
from pathlib import Path
from typing import Dict, Optional

from pydantic import validator
from requests_toolbelt import MultipartEncoder

from fiddler.v2.constants import FileType
from fiddler.v2.schema.base import BaseDataSchema
from fiddler.v2.schema.common import DatasetInfo


class Dataset(BaseDataSchema):

    id: int
    name: str
    version: str
    file_list: dict
    info: DatasetInfo
    organization_name: str
    project_name: str


class DatasetIngest(BaseDataSchema):
    name: str
    file_paths: Dict[str, Path]
    info: Optional[DatasetInfo] = None
    file_type: Optional[FileType] = None
    file_schema: Optional[dict] = None

    class Config:
        use_enum_values = True

    @validator('file_paths')
    def valid_file_path_dict(cls, file_path):
        if not file_path:
            raise ValueError('file_path can not be empty dictionary')
        return file_path

    def multipart_form_request(self) -> Dict[dict, bytes]:
        request_body_json = self.dict(exclude={'file_paths', 'info'})
        request_body_json['info'] = self.info.dict(
            by_alias=True
        )  # setting by_alias bc Columns fiels are aliased
        request_body = {
            name: (file_path.name, open(file_path, 'rb'))
            for name, file_path in self.file_paths.items()
        }
        # https://stackoverflow.com/a/19105672/13201804
        request_body.update(
            {'json': (None, json.dumps(request_body_json), 'application/json')}
        )
        m = MultipartEncoder(fields=request_body)
        return m.content_type, m

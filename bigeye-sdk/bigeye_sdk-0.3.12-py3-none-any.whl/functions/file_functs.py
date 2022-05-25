from __future__ import annotations

import dataclasses
import enum
import json
import os
from dataclasses import dataclass
from typing import List

import smart_open

from bigeye_sdk.log import get_logger

# create logger
log = get_logger(__file__)


# Right now only works with snowflake.
class FileType(str, enum.Enum):
    JSON = "file_format = (type = 'JSON', field_delimiter = '|')"
    PSV = "file_format = (type = 'CSV', field_delimiter = '|', SKIP_HEADER = 1)"


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def create_subdir_if_not_exists(path, includes_file: bool = False, *args, **kwargs):
    subdir = path if not includes_file else os.path.dirname(path)
    if not os.path.exists(subdir):
        log.info(f'Creating path: {subdir}')
        os.makedirs(subdir)


@dataclass
class WriteDataResult:
    fq_table: str
    url: str
    format: FileType


def _write_to_file(url: str, serialized_data: List[str]) -> str:
    log.info(f'Persisting file: {url}')
    with smart_open.smart_open(url, 'wb') as fout:
        for s in serialized_data:
            fout.write(s.encode())

    return url


def serialize_dataclass_to_json_file(url: str, datum: dataclass) -> str:
    return _write_to_file(url, [json.dumps(datum, cls=EnhancedJSONEncoder)])


def serialize_list_to_json_file(url: str, data: list) -> str:
    log.info(f'writing file: {url}')
    return _write_to_file(url, [json.dumps(datum, cls=EnhancedJSONEncoder) for datum in data])


# TODO Replace with serialize_list_to_json_file
def serialize_listdict_to_json_file(url: str, data: List[dict]) -> str:
    string_list = [f'{json.dumps(datum, default=str)}\n' for datum in data]
    return _write_to_file(url, string_list)

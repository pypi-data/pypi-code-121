"""This module contains logic to parse flaks multipart requests.
"""
import json as _json
import typing as t

import cg_maybe

from ._base import Parser as _Parser
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from .exceptions import SimpleParseError as _SimpleParseError
from ._swagger_utils import Schema as _Schema
from ._swagger_utils import OpenAPISchema as _OpenAPISchema
from ._swagger_utils import maybe_raise_schema as _maybe_raise_schema

try:
    import flask
except ImportError:  # pragma: no cover
    pass

if t.TYPE_CHECKING:  # pragma: no cover
    # pylint: disable=unused-import
    from werkzeug.datastructures import FileStorage

    from ._base import LogReplacer as _LogReplacer


def _generate_files_schema() -> t.Mapping[str, t.Any]:
    return {
        'type': 'array',
        'items': {
            'type': 'string',
            'format': 'binary',
        },
    }


class MultipartUploadWithoutData:
    """This class helps you parse JSON and files from the same request.
    """
    if _USE_SLOTS:
        __slots__ = ('file_key', )

    def __init__(
        self,
        file_key: str,
    ) -> None:
        self.file_key: t.Final = file_key

    def __generate_schema(self, _: _OpenAPISchema) -> _Schema:
        return _Schema(
            typ='multipart/form-data',
            schema={
                'type': 'object',
                'properties': {self.file_key: _generate_files_schema()},
            },
        )

    def from_flask(self) -> t.Sequence['FileStorage']:
        """Parse a multipart request from the current flask request.

        :param log_replacer: If passed this function should remove any
            sensitive data from the logs.

        :returns: A tuple, where the first item is the parsed JSON (according
                  to the given parser), and the second argument is a list of
                  the parsed files.
        """
        _maybe_raise_schema(self.__generate_schema)

        if not flask.request.files:
            files = []
        else:
            files = flask.request.files.getlist(self.file_key)
            for key, f in flask.request.files.items():
                if key != self.file_key and key.startswith(self.file_key):
                    files.append(f)

        files = [f for f in files if f.filename]
        return files


class MultipartUploadWithData(t.Generic[_T]):
    """This class helps you parse JSON and files from the same request.
    """
    if _USE_SLOTS:
        __slots__ = ('__parser', '__multipart')

    def __init__(
        self,
        parser: _Parser[_T],
        file_key: str,
    ) -> None:
        self.__parser = parser
        self.__multipart = MultipartUploadWithoutData(file_key)

    def __generate_schema(self, open_api: _OpenAPISchema) -> _Schema:
        json_schema = self.__parser.to_open_api(open_api)
        props = {
            'json': json_schema,
            self.__multipart.file_key: _generate_files_schema(),
        }
        return _Schema(
            typ='multipart/form-data',
            schema={
                'type': 'object',
                'properties': props,
                'required': ['json'],
            },
        )

    def from_flask(
        self,
        *,
        log_replacer: '_LogReplacer' = None,
    ) -> t.Tuple[_T, t.Sequence['FileStorage']]:
        """Parse a multipart request from the current flask request.

        :param log_replacer: If passed this function should remove any
            sensitive data from the logs.

        :returns: A tuple, where the first item is the parsed JSON (according
                  to the given parser), and the second argument is a list of
                  the parsed files.
        """
        _maybe_raise_schema(self.__generate_schema)

        body = None
        if 'json' in flask.request.files:
            body = _json.load(flask.request.files['json'])
        if not body:
            body = flask.request.get_json()

        result = self.__parser.try_parse_and_log(
            body, log_replacer=log_replacer
        )
        return result, self.__multipart.from_flask()


class ExactMultipartUploadWithData(t.Generic[_T]):
    """This class helps you parse JSON and files from the same request.
    """
    if _USE_SLOTS:
        __slots__ = ('__parser', '__file_keys')

    def __init__(
        self,
        parser: _Parser[_T],
        file_keys: t.Sequence[str],
    ) -> None:
        self.__parser = parser
        self.__file_keys = file_keys

    def describe(self) -> str:
        return 'Request[{{"json": {json} as file, {other}}}]'.format(
            json=self.__parser.describe(),
            other=', '.join(f'"{key}": File' for key in self.__file_keys),
        )

    def __generate_schema(self, open_api: _OpenAPISchema) -> _Schema:
        json_schema = self.__parser.to_open_api(open_api)
        file_type: t.Mapping[str, t.Any] = {
            'type': 'string',
            'format': 'binary',
        }
        return _Schema(
            typ='multipart/form-data',
            schema={
                'type': 'object',
                'properties': {
                    'json': json_schema,
                    **{key: file_type
                       for key in self.__file_keys},
                },
                'required': ['json'],
            },
        )

    def from_flask(
        self,
        *,
        log_replacer: '_LogReplacer' = None,
    ) -> t.Tuple[_T, t.Mapping[str, 'FileStorage']]:
        """Parse a multipart request from the current flask request.

        :param log_replacer: If passed this function should remove any
            sensitive data from the logs.

        :returns: A tuple, where the first item is the parsed JSON (according
                  to the given parser), and the second argument is a list of
                  the parsed files.
        """
        _maybe_raise_schema(self.__generate_schema)

        body = None
        if 'json' in flask.request.files:
            body = _json.load(flask.request.files['json'])
        else:
            body = cg_maybe.Nothing

        result = self.__parser.try_parse_and_log(
            body, log_replacer=log_replacer
        )

        files = flask.request.files
        if not files:
            raise _SimpleParseError(self, cg_maybe.Nothing)

        file_map = {
            key: files[key]
            for key in self.__file_keys if key in files and files[key].filename
        }
        if any(key not in file_map for key in self.__file_keys):
            raise _SimpleParseError(
                self,
                {
                    key: 'File'
                    for key, value in files.items() if value.filename
                },
            )

        return result, file_map

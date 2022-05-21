import io
import mimetypes
from io import IOBase
from typing import List, Optional, Iterator, Union, IO
from uuid import uuid4

from pkm.utils.io_streams import chunks

_FORM_FIELD_SORTED_HEADERS = ["Content-Disposition", "Content-Type", "Content-Location"]


class FormField:

    def __init__(self, name: str, payload: Union[IO, str, bytes], filename: Optional[str] = None):
        self.name: str = name
        self.payload = payload
        self.filename = filename or name
        filename_header_part = f'; filename="{filename}"' if filename else ""
        self.headers = {
            "Content-Disposition": f'form-data; name="{name}"{filename_header_part}',
            "Content-Type": _guess_content_type(filename)
        }

    def set_content_type(self, content_type: str) -> "FormField":
        self.headers["Content-Type"] = content_type
        return self

    # credits: this method is adapted from urllib3.fields.RequestField.render_headers
    def render(self) -> str:
        lines = [f"{k}: {self.headers[k]}" for k in _FORM_FIELD_SORTED_HEADERS if k in self.headers]
        lines.extend(f"{k}: {v}" for k, v in self.headers.items() if v and k not in _FORM_FIELD_SORTED_HEADERS)
        lines.append("\r\n")
        return "\r\n".join(lines)


class MultipartFormDataPayload:
    def __init__(self, fields: List[FormField], chunk_size: int = io.DEFAULT_BUFFER_SIZE,
                 boundary: Optional[str] = None):
        self._fields = fields
        self._chunk_size = chunk_size
        self._boundary = boundary or uuid4().hex

    def content_type(self):
        return f"multipart/form-data; boundary={self._boundary}"

    def __iter__(self) -> Iterator[bytes]:
        boundary = f"--{self._boundary}\r\n".encode()
        newline = b"\r\n"
        chunk_size = self._chunk_size

        for field in self._fields:
            yield boundary
            yield field.render().encode()

            payload = field.payload
            if isinstance(payload, IOBase):
                yield from chunks(payload, chunk_size)
            elif isinstance(payload, str):
                yield payload.encode()
            elif isinstance(payload, bytes):
                yield payload
            else:
                raise ValueError(f'unsupported payload type for field: {field.name}: {type(field.payload)}')

            yield newline


def _guess_content_type(filename: Optional[str], default="application/octet-stream"):
    if filename:
        return mimetypes.guess_type(filename)[0] or default
    return default

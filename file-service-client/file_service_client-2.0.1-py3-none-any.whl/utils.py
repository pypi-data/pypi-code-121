import pathlib
import mimetypes

mimetypes.init()

DEFAULT_MIME = "application/octet-stream"


def get_mimetype(file_path: pathlib.Path) -> str:
    mime_struct = mimetypes.guess_type(file_path.name)
    if mime_struct[0]:
        return str(mime_struct[0])
    return DEFAULT_MIME

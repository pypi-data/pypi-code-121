import pathlib
from os.path import join, splitext
from typing import BinaryIO, Optional, TextIO


def file_extension_from_url(image_url: str) -> str:
    """
    Returns the extensions of the file in an url including the do in the beginning.
    E.g. www.test.de/file.jpeg?whatever=what would return .jpg
    """

    url_part = image_url.split("?")
    return splitext(url_part[0])[1]


def file_extension_from_path(path: str) -> str:
    """
    The final component's last suffix, if any.

    This includes the leading period. For example: '.txt'
    """

    return pathlib.Path(path).suffix


def get_file_object(file_path: str) -> Optional[TextIO]:
    with open(file_path, encoding="utf-8") as opened_file:
        return opened_file


def get_file_as_binary(file_path: str) -> Optional[BinaryIO]:
    with open(file_path, "rb") as opened_file:
        return opened_file


def read_file_as_binary(file_path: str) -> Optional[bytes]:
    with open(file_path, "rb") as opened_file:
        return opened_file.read()


def read_file_content(file_path: str) -> Optional[str]:
    with open(file_path, "r", encoding="utf-8") as opened_file:
        return opened_file.read()


def handle_uploaded_file(file, destination_path) -> str:
    destination_path = join(destination_path, file.name)

    with open(destination_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return destination_path

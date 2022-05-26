from typing import BinaryIO

from nwon_baseline.file_helper import get_file_as_binary
from PIL import Image

from nwon_django_toolbox.tests.helper.random_temporary_file import (
    get_random_tempfile_path,
)


def get_random_image(width: int = 100, height: int = 100) -> BinaryIO:
    """
    Returns a randomly created image with the given dimensions as a binary
    """

    random_image_path = __path_to_created_random_image(width, height)
    binary = get_file_as_binary(random_image_path)

    if binary is None:
        raise Exception(f"Could not read image at {random_image_path}")

    return binary


def get_path_to_random_image(width: int = 100, height: int = 100) -> str:
    """
    Get a path to a randomly created image with the given dimensions.
    """

    return __path_to_created_random_image(width, height)


def __path_to_created_random_image(width: int, height: int) -> str:
    tempfile_path = get_random_tempfile_path(suffix="jpg")

    image = Image.new("RGB", size=(width, height))
    image.save(tempfile_path)

    return tempfile_path


__all__ = ["get_random_image", "get_path_to_random_image"]

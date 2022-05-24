import functools
from typing import Any, Callable, Dict, Iterable, Optional, Union

from PIL import Image

from ._parallel import execute_parallel
from ._typing import FilePath

__all__ = [
    "convert_binary_to_image",
    "convert_binary_to_image_parallel",
    "resize_image",
    "resize_image_parallel",
]

WidthFunction = Callable[[int], int]


def _get_image(binary: bytes, *, width: int, drop: bool = False, padding: bytes = b"\x00") -> Image.Image:
    nbytes = len(binary)
    height, rem = divmod(nbytes, width)
    if rem != 0:
        # The image height must be at least 1.
        if drop and height > 0:
            nbytes = width * height
            binary = binary[:nbytes]
        else:
            height += 1
            nbytes = width * height
            binary = binary.ljust(nbytes, padding)
    return Image.frombuffer("L", (width, height), binary, "raw", "L", 0, 1)


def get_image(
    binary: bytes, *, width: Union[int, str, WidthFunction], drop: bool = False, padding: bytes = b"\x00"
) -> Image.Image:
    if isinstance(width, str):
        try:
            width = _registry[width](len(binary))
        except KeyError:
            keys = "{" + ", ".join(_registry.keys()) + "}"
            raise ValueError(f"unknown width, expected {keys}")
    elif callable(width):
        width = width(len(binary))
    return _get_image(binary, width=width, drop=drop, padding=padding)


def convert_binary_to_image(
    binary_file: FilePath, image_file: FilePath, *, width: Union[int, str], drop: bool = False, padding: bytes = b"\x00"
) -> None:
    """Convert binary file to image file."""

    with open(binary_file, "rb") as f:
        binary = f.read()
    image = get_image(binary, width=width, drop=drop, padding=padding)
    image.save(image_file)


def convert_binary_to_image_parallel(
    binary_files: Iterable[FilePath],
    image_files: Iterable[FilePath],
    *,
    width: Union[int, str],
    drop: bool = False,
    padding: bytes = b"\x00",
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Convert binary file to image file in parallel."""

    function = functools.partial(convert_binary_to_image, width=width, drop=drop, padding=padding)
    execute_parallel(function, binary_files, image_files, n_jobs=n_jobs, **kwargs)


def resize_image(src: FilePath, dst: FilePath, *, width: int, height: int) -> None:
    """Resize image file."""

    image = Image.open(src)
    image = image.resize((width, height), Image.BILINEAR)
    image.save(dst)


def resize_image_parallel(
    srcs: Iterable[FilePath],
    dsts: Iterable[FilePath],
    *,
    width: int,
    height: int,
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Resize image file in parallel."""

    function = functools.partial(resize_image, width=width, height=height)
    execute_parallel(function, srcs, dsts, n_jobs=n_jobs, **kwargs)


def width_function_nataraj(filesize: int) -> int:
    """Set width depending on filesize.

    References:
        - Nataraj et al. 2011. Malware images: visualization and automatic classification.
          https://doi.org/10.1145/2016904.2016908
    """

    k = filesize // 1024
    if k < 10:
        width = 32
    elif k < 30:
        width = 64
    elif k < 60:
        width = 128
    elif k < 100:
        width = 256
    elif k < 200:
        width = 384
    elif k < 500:
        width = 512
    elif k < 1000:
        width = 768
    else:
        width = 1024
    return width


_registry: Dict[str, WidthFunction] = {"nataraj": width_function_nataraj}

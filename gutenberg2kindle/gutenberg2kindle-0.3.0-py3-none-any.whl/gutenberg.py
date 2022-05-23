"""Auxiliary functions to connect to Project Gutenberg's library"""

from io import BytesIO
from typing import Final, Optional

import requests

from gutenberg2kindle.config import (
    FORMAT_AUTO,
    FORMAT_IMAGES,
    FORMAT_NO_IMAGES,
    SETTINGS_FORMAT,
    get_config,
)

GUTENBERG_BOOK_WITH_IMAGES_BASE_URL: Final[str] = (
    "https://www.gutenberg.org/ebooks/{book_id}.epub.images"
)
GUTENBERG_BOOK_BASE_URL: Final[str] = (
    "https://www.gutenberg.org/ebooks/{book_id}.epub"
)


def download_book(book_id: int) -> Optional[BytesIO]:
    """
    Given a Gutenberg book ID as an integer, and the expected format,
    fetches the content of the book into memory and returns it wrapped
    in a Bytes IO instance.
    """

    fmt = get_config(SETTINGS_FORMAT)
    assert isinstance(fmt, str)

    book_url = GUTENBERG_BOOK_BASE_URL.format(book_id=book_id)
    if fmt == FORMAT_NO_IMAGES:
        return fetch_book_from_url(book_url)

    book_with_images_url = GUTENBERG_BOOK_WITH_IMAGES_BASE_URL.format(
        book_id=book_id
    )
    if fmt == FORMAT_IMAGES:
        return fetch_book_from_url(book_with_images_url)

    if fmt == FORMAT_AUTO:
        book_or_none = fetch_book_from_url(book_with_images_url)

        if book_or_none is not None:
            return book_or_none

        return fetch_book_from_url(book_url)

    raise ValueError(f"{fmt} is an invalid format")


def fetch_book_from_url(book_url: str) -> Optional[BytesIO]:
    """
    Given a Gutenberg book URL, fetches the content
    of the book into memory and returns it wrapped in a BytesIO
    instance
    """

    response = requests.get(book_url)
    if response.status_code != 200:
        return None
    book_content = response.content

    memory_bytes = BytesIO()
    memory_bytes.write(book_content)
    memory_bytes.seek(0)
    return memory_bytes

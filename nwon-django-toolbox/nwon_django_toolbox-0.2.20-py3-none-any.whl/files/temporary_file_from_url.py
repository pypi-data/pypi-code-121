import tempfile
from typing import Optional

from django.core.files import File
from requests import get


def temporary_file_from_url(
    url: str, suffix: str, delete: bool = False
) -> Optional[File]:
    """
    Retrieves a file from an url, saves it in a temporary file and returns an Django File object.
    """

    request = get(url)

    if request.status_code != 200:
        return None

    temporary_file = tempfile.NamedTemporaryFile(delete=delete, suffix=suffix)

    with open(temporary_file.name, "wb") as opened_file:
        opened_file.write(request.content)

    opened_file.close()

    with open(temporary_file.name, "rb") as opened_file:
        django_file = File(opened_file)

    opened_file.close()

    return django_file

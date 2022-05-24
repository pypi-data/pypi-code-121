from pathlib import (
    Path,
)
from typing import (
    Optional,
)

from botoolkit.settings import (
    DEFAULT_RSA_PRIVATE_KEY_PATH,
)


def get_rsa_private_key_as_string(
    rsa_private_key_path: Optional[Path] = None,
):
    """
    Получение приватного ключа с заменой символа \n на строку \n
    """
    if not rsa_private_key_path:
        rsa_private_key_path = DEFAULT_RSA_PRIVATE_KEY_PATH

    with open(str(rsa_private_key_path), 'r') as id_rsa_file:
        rsa_private_key = id_rsa_file.read()

    return rsa_private_key.replace('\n', '\\n')

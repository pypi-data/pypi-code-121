from functools import lru_cache
from pathlib import Path

import black

from globality_black.constants import DEFAULT_BLACK_LINE_LENGTH


@lru_cache(maxsize=1)
def get_black_mode(src: Path) -> black.Mode:
    """Read the black configuration from pyproject.toml"""

    value = black.find_pyproject_toml((str(src),))

    if not value:
        return black.Mode(line_length=DEFAULT_BLACK_LINE_LENGTH)

    config = black.parse_pyproject_toml(value)

    return black.Mode(**{
        key: value
        for key, value in config.items()
    })

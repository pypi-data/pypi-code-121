from typing import Dict

from .decorators import collect, metadata

__version__ = "0.1.6"
__author__ = "The PyUsage Team"
__copyright__ = f"Copyright 2022 {__author__}"


collect = collect(collect)
metadata = collect(metadata)


@metadata
def _get_metadata() -> Dict[str, str]:
    # We're importing `datetime` and `platform` here so they can't be imported from
    # `usage` (e.g., `from usage import datetime`).
    import datetime  # pylint: disable=import-outside-toplevel
    import platform  # pylint: disable=import-outside-toplevel

    return {
        "python": platform.python_version(),
        "os": platform.system(),
        "version": __version__,
        "time": str(datetime.datetime.now()),
    }


del _get_metadata

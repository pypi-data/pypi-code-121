from .version import __version__
from . import core
from . import exceptions
from . import models
from .client import Client
from .settings import settings

import sys

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources
data = resources.files("itkdb") / "data"


def listInstitutions():
    return models.institution.make_institution_list(
        core.Session().get("listInstitutions").json()["pageItemList"]
    )


__all__ = [
    "__version__",
    "Client",
    "core",
    "data",
    "exceptions",
    "models",
    "settings",
    "listInstitutions",
]

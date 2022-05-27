from typing import Any
from typing_extensions import Protocol

from ..models.bibdata import BibliographicItem


class Serializer(Protocol):
    """Serializer functions are supposed to conform to this callable interface."""

    def __call__(self, bibitem: BibliographicItem, **kwargs: Any) -> Any: ...

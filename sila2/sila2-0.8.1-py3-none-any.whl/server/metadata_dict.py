from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Mapping, Optional, TypeVar

from sila2.framework import DefinedExecutionErrorNode, FullyQualifiedMetadataIdentifier, Metadata

if TYPE_CHECKING:
    from sila2.server import SilaServer

T = TypeVar("T")


class MetadataDict(Mapping[Metadata, Any]):
    """
    :py:class:`dict`-like class that maps :py:class:`~sila2.framework.Metadata` objects to the received data objects

    Examples
    --------
    >>> metadata[LockControllerFeature["LockIdentifier"]]
    'my-lock-token'
    """

    def __init__(
        self, parent_server: SilaServer, base_dict: Optional[Dict[FullyQualifiedMetadataIdentifier, Any]] = None
    ):
        self.__parent_server = parent_server
        self.__base_dict = base_dict if base_dict is not None else {}

    def __getitem__(self, k: Metadata[T]) -> T:
        return self.__base_dict[k.fully_qualified_identifier]

    def __len__(self) -> int:
        return len(self.__base_dict)

    def __iter__(self) -> Iterator[Metadata]:
        return (self.__parent_server.children_by_fully_qualified_identifier[fqi] for fqi in self.__base_dict)

    @property
    def defined_execution_errors(self) -> List[DefinedExecutionErrorNode]:
        ret = []
        for m in self:
            ret.extend(m.defined_execution_errors)
        return ret

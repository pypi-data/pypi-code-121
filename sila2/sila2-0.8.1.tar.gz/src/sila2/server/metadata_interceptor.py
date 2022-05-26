from abc import ABC, abstractmethod
from typing import Any, Iterable

from sila2.framework import Metadata
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier
from sila2.server.metadata_dict import MetadataDict


class MetadataInterceptor(ABC):
    def __init__(self, affected_metadata: Iterable[Metadata]) -> None:
        """
        Intercepts SiLA Client Metadata

        Parameters
        ----------
        affected_metadata
            SiLA Client Metadata to intercept

        Notes
        -----
        When a SiLA Client sends SiLA Client Metadata along with a command execution or property access request,
        the ``intercept()`` method of all affected metadata interceptors are called.
        """
        self.affected_metadata = frozenset(m.fully_qualified_identifier for m in affected_metadata)

    @abstractmethod
    def intercept(
        self,
        parameters: Any,
        metadata: MetadataDict,
        target_call: FullyQualifiedIdentifier,
    ) -> None:
        """
        Called by the SiLA Server when receiving SiLA Client Metadata that is affected by this interceptor

        Parameters
        ----------
        parameters
            Original call parameters as a named tuple
        metadata
            All SiLA Client Metadata received along with the call
        target_call
            Fully qualified identifier of the requested command or property
        """
        pass

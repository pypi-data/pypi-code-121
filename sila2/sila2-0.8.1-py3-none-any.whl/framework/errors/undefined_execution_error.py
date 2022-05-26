from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.sila_error import SilaError

if TYPE_CHECKING:
    from sila2.client.sila_client import SilaClient
    from sila2.framework.pb2.SiLAFramework_pb2 import SiLAError
    from sila2.framework.pb2.SiLAFramework_pb2 import UndefinedExecutionError as SilaUndefinedExecutionError


class UndefinedExecutionError(SilaError):
    """
    Any error issued by a SiLA Server during command execution, property access, or related to SiLA Client Metadata,
    that is not a :py:class:`sila2.framework.DefinedExecutionError` (i.e. not specified in the feature definition)

    Notes
    -----
    When any exception occurs on the server-side that is no :py:class:`sila2.framework.DefinedExecutionError`
    or another SiLA error, the SDK will automatically raise it to the SiLA Client as an instance of this class
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    @classmethod
    def from_exception(cls, exception: Exception) -> UndefinedExecutionError:
        return cls(f"{exception.__class__.__name__} - {exception}")

    def to_message(self) -> SiLAError:
        return self._pb2_module.SiLAError(
            undefinedExecutionError=self._pb2_module.UndefinedExecutionError(message=self.message)
        )

    @classmethod
    def from_message(cls, message: SilaUndefinedExecutionError, client: SilaClient) -> UndefinedExecutionError:
        return cls(message.message)

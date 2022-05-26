from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sila2.framework.abc.sila_error import SilaError

if TYPE_CHECKING:
    from sila2.client.sila_client import SilaClient
    from sila2.framework.pb2.SiLAFramework_pb2 import FrameworkError as SilaFrameworkError
    from sila2.framework.pb2.SiLAFramework_pb2 import SiLAError


class FrameworkError(SilaError):
    """
    Base class for all SiLA Framework Errors. Don't use this class directly. Instead, use one of its subclasses:

    - :py:class:`sila2.framework.InvalidCommandExecutionUUID`
    - :py:class:`sila2.framework.CommandExecutionNotFinished`
    - :py:class:`sila2.framework.InvalidMetadata`
    - :py:class:`sila2.framework.NoMetadataAllowed`
    - :py:class:`sila2.framework.CommandExecutionNotAccepted`
    """

    error_type: FrameworkErrorType
    message: str

    def __init__(self, error_type: FrameworkErrorType, message: str):
        self.error_type = error_type
        self.message = message

    def to_message(self) -> SiLAError:
        return self._pb2_module.SiLAError(
            frameworkError=self._pb2_module.FrameworkError(
                errorType=getattr(self._pb2_module.FrameworkError, self.error_type.name),
                message=self.message,
            )
        )

    @classmethod
    def from_message(cls, message: SilaFrameworkError, client: SilaClient) -> FrameworkError:
        if message.errorType == message.COMMAND_EXECUTION_NOT_ACCEPTED:
            from sila2.framework.errors.command_execution_not_accepted import CommandExecutionNotAccepted

            return CommandExecutionNotAccepted(message.message)
        if message.errorType == message.INVALID_COMMAND_EXECUTION_UUID:
            from sila2.framework.errors.invalid_command_execution_uuid import InvalidCommandExecutionUUID

            return InvalidCommandExecutionUUID(message.message)
        if message.errorType == message.COMMAND_EXECUTION_NOT_FINISHED:
            from sila2.framework.errors.command_execution_not_finished import CommandExecutionNotFinished

            return CommandExecutionNotFinished(message.message)
        if message.errorType == message.INVALID_METADATA:
            from sila2.framework.errors.invalid_metadata import InvalidMetadata

            return InvalidMetadata(message.message)
        if message.errorType == message.NO_METADATA_ALLOWED:
            from sila2.framework.errors.no_metadata_allowed import NoMetadataAllowed

            return NoMetadataAllowed(message.message)

        raise NotImplementedError(f"FrameworkError type not supported: {message.errorType}")  # should not happen


class FrameworkErrorType(Enum):
    COMMAND_EXECUTION_NOT_ACCEPTED = 0
    INVALID_COMMAND_EXECUTION_UUID = 1
    COMMAND_EXECUTION_NOT_FINISHED = 2
    INVALID_METADATA = 3
    NO_METADATA_ALLOWED = 4

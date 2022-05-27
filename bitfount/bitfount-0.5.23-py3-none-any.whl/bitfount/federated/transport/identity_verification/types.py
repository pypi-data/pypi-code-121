"""Types related to identity verification flow."""
from __future__ import annotations

from asyncio import Task
from typing import Protocol, runtime_checkable

from bitfount.federated.transport.modeller_transport import _ModellerMailbox


class _ResponseHandler(Protocol):
    """Protocol describing a verification response handler."""

    async def handle(self, modeller_mailbox: _ModellerMailbox) -> None:
        """Handle identity verification response messages."""
        ...


@runtime_checkable
class _HasWebServer(Protocol):
    """Protocol describing identity verification methods that need a web server."""

    def start_server(self) -> Task:
        """Start the identity verification process web server.

        To avoid blocking the main thread, this should be run as a background
        asyncio.Task.

        This is particularly important for identity verification methods that require
        a webserver connection as part of the _flow_, as this can take some time to
        start up.
        """
        ...

    async def stop_server(self) -> None:
        """Stop the identity verification process web server.

        It must be possible to call this method multiple times, simply doing nothing
        on subsequent calls.
        """
        ...

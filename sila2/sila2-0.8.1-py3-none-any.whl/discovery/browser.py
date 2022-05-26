from __future__ import annotations

import time
from datetime import datetime
from typing import List, Optional, Type, Union
from uuid import UUID

from zeroconf import ServiceBrowser, Zeroconf

from sila2.client.sila_client import SilaClient
from sila2.discovery.listener import SilaServiceListener


class SilaDiscoveryBrowser(ServiceBrowser):
    def __init__(
        self,
        *,
        root_certs: Optional[bytes] = None,
        private_key: Optional[bytes] = None,
        cert_chain: Optional[bytes] = None,
        insecure: bool = False,
        client_cls: Type[SilaClient] = SilaClient,
    ):
        """
        Browser that listens for SiLA Servers in the background

        Parameters
        ----------
        root_certs
            PEM-encoded root certificates
        private_key
            PEM-encoded private key
        cert_chain
            PEM-encoded certificate chain
        insecure
            If ``True``, no encryption will be used. Violates the SiLA 2 specification, only use for debugging purposes
        client_cls
            Class to be used for creating SiLA Client objects

        Notes
        -----
        Can be used as a context manager
        """
        self.listener = SilaServiceListener(
            self,
            insecure=insecure,
            root_certs=root_certs,
            private_key=private_key,
            cert_chain=cert_chain,
            client_cls=client_cls,
        )
        super().__init__(Zeroconf(), "_sila._tcp.local.", self.listener)

    @property
    def clients(self) -> List[SilaClient]:
        """List of SiLA Clients connected to all currently detected SiLA Servers"""
        return list(self.listener.services.values())

    def find_server(
        self, server_name: Optional[str] = None, server_uuid: Optional[Union[UUID, str]] = None, timeout: float = 0
    ) -> SilaClient:
        """
        Wait until a matching SiLA Server is found

        Parameters
        ----------
        server_name
            Only connect to SiLA Servers with this server name
        server_uuid
            Only connect to SiLA Servers with this server UUID
        timeout
            Time in seconds. If no matching server was found in this time, a ``TimeoutError`` will be raised

        Returns
        -------
        client
            SiLA Client connected to a matching SiLA Server

        Raises
        ------
        TimeoutError
            If no server was found
        """
        if timeout < 0:
            raise ValueError("Timeout must be non-negative")

        start_time = datetime.now()
        while timeout == 0 or (datetime.now() - start_time).total_seconds() < timeout:
            for client in self.clients:
                if server_name is not None and client.SiLAService.ServerName.get() != server_name:
                    continue
                if server_uuid is not None and client.SiLAService.ServerUUID.get() != str(server_uuid):
                    continue
                return client
            time.sleep(0.1)

        raise TimeoutError(f"No suitable SiLA server was found after {timeout} seconds")

    def __del__(self):
        if not self.done:
            self.cancel()

    def __enter__(self) -> SilaDiscoveryBrowser:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.done:
            self.cancel()

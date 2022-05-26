from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from zeroconf import Zeroconf

from sila2.discovery.service_info import SilaServiceInfo

if TYPE_CHECKING:
    from sila2.server.sila_server import SilaServer


class SilaServiceBroadcaster:
    zc: Zeroconf

    def __init__(self):
        self.zc = Zeroconf()

    def register_server(
        self, server: SilaServer, address: str, port: int, ca: Optional[bytes] = None
    ) -> SilaServiceInfo:
        service_info = SilaServiceInfo(server, address, port, ca)
        self.zc.register_service(service_info)
        return service_info

    def unregister_server(self, info: SilaServiceInfo) -> None:
        self.zc.unregister_service(info)

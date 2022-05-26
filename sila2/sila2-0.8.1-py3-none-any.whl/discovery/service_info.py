from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from zeroconf import ServiceInfo

if TYPE_CHECKING:
    from sila2.server.sila_server import SilaServer


class SilaServiceInfo(ServiceInfo):
    sila_server: SilaServer

    def __init__(self, server: SilaServer, address: str, port: int, ca: Optional[bytes] = None):
        properties = dict(
            version=server.server_version,
            server_name=server.server_name,
            description=server.server_description,
        )

        if ca is not None:
            current_ca_pos = 0
            current_line_num = 0
            while current_ca_pos < len(ca):
                key = f"ca{current_line_num}"
                current_line_num += 1

                value_length = 255 - len(key) - 1  # TXT records have max length 255 and are formatted as "key=value"
                properties[key] = ca[current_ca_pos : current_ca_pos + value_length]
                current_ca_pos += value_length

        super().__init__(
            type_="_sila._tcp.local.",
            name=f"{server.server_uuid}._sila._tcp.local.",
            parsed_addresses=[address],
            port=port,
            properties=properties,
        )
        self.sila_server = server

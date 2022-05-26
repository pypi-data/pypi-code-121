import itertools
import ssl
import warnings
from typing import Dict, Optional, Type
from uuid import UUID

from cryptography import x509
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.backends import default_backend
from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf

from sila2.client.sila_client import SilaClient


class SilaServiceListener(ServiceListener):
    services: Dict[str, SilaClient]

    def __init__(
        self,
        parent_browser: ServiceBrowser,
        *,
        insecure: bool = False,
        root_certs: Optional[bytes] = None,
        private_key: Optional[bytes] = None,
        cert_chain: Optional[bytes] = None,
        client_cls: Type[SilaClient] = SilaClient,
    ):
        self.parent_browser = parent_browser
        self.services = {}
        self.insecure = insecure
        self.root_certs = root_certs
        self.private_key = private_key
        self.cert_chain = cert_chain
        self.client_cls = client_cls

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        self.__add_client(info)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        self.__add_client(info)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        if name in self.services:
            self.services.pop(name)

    def __add_client(self, service_info: Optional[ServiceInfo] = None) -> None:
        if service_info is None:  # happens sometimes
            return

        service_name = service_info.name
        service_uuid = UUID(service_name.split(".")[0])
        ip_address = service_info.parsed_addresses()[0]
        port = service_info.port

        try:
            if self.cert_chain is not None or self.private_key is not None or self.root_certs is not None:
                self.services[service_name] = self.client_cls(
                    ip_address,
                    port,
                    cert_chain=self.cert_chain,
                    private_key=self.private_key,
                    root_certs=self.root_certs,
                )
            elif self.insecure:
                self.services[service_name] = self.client_cls(ip_address, port, insecure=True)
            else:
                ca = self.__get_ca_from_service_info(service_info)
                if ca is not None:
                    # SiLA servers using untrusted certificates must have a certificate with Common Name "SiLA2"
                    cert = x509.load_pem_x509_certificate(
                        ssl.get_server_certificate((ip_address, port)).encode("ascii"), backend=default_backend()
                    )
                    common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                    if common_name != "SiLA2":
                        raise RuntimeError("Certificates of untrusted servers must have the common name 'SiLA2'")

                    self.services[service_name] = self.client_cls(ip_address, port, root_certs=ca)
                    warnings.warn(
                        RuntimeWarning(
                            f"Connected to server at {ip_address}:{port} with UUID {service_uuid} "
                            f"via untrusted certificate"
                        )
                    )
                else:
                    warnings.warn(
                        RuntimeWarning(
                            f"Detected server at {ip_address}:{port} with UUID {service_uuid}, "
                            f"but found no way to connect to it "
                            f"(insecure connections are disabled, no certificate information privided)"
                        )
                    )
        except Exception as ex:
            warnings.warn(
                RuntimeWarning(
                    f"Failed to connect to server at {ip_address}:{port} with UUID {service_uuid}: "
                    f"{ex.__class__.__name__} - {ex}"
                )
            )

    @staticmethod
    def __get_ca_from_service_info(service_info: ServiceInfo) -> Optional[bytes]:
        if b"ca0" not in service_info.properties:
            return None

        ca = b""
        for i in itertools.count():
            key = f"ca{i}".encode("ascii")
            if key in service_info.properties:
                ca += service_info.properties[key]
            else:
                break
        if ca == b"":
            return
        x509.load_pem_x509_certificate(ca)  # check if a full CA was found
        return ca

from __future__ import annotations

import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID

import grpc

from sila2.discovery.broadcaster import SilaServiceBroadcaster
from sila2.discovery.service_info import SilaServiceInfo
from sila2.framework.binary_transfer.server_binary_transfer_handler import ServerBinaryTransferHandler
from sila2.framework.constraints.maximal_length import MaximalLength
from sila2.framework.constraints.pattern import Pattern
from sila2.framework.feature import Feature
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier
from sila2.framework.utils import parse_feature_definition, xpath_sila
from sila2.server.encryption import generate_self_signed_certificate
from sila2.server.feature_implementation_base import FeatureImplementationBase
from sila2.server.feature_implementation_servicer import FeatureImplementationServicer
from sila2.server.metadata_interceptor import MetadataInterceptor

if TYPE_CHECKING:
    from sila2.framework.command.command import Command
    from sila2.framework.command.intermediate_response import IntermediateResponse
    from sila2.framework.command.parameter import Parameter
    from sila2.framework.command.response import Response
    from sila2.framework.data_types.data_type_definition import DataTypeDefinition
    from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
    from sila2.framework.metadata import Metadata
    from sila2.framework.property.property import Property


class SilaServer:
    grpc_server: grpc.Server
    features: Dict[str, Feature]
    feature_servicers: Dict[str, FeatureImplementationServicer]
    generated_ca: Optional[bytes]
    """PEM-encoded certificate authority of self-signed certificate, if generated on server startup"""

    server_name: str
    """SiLA Server Name"""
    server_type: str
    """SiLA Server Type"""
    server_uuid: UUID
    """SiLA Server UUID"""
    server_description: str
    """SiLA Server Description"""
    server_version: str
    """SiLA Server Version"""
    server_vendor_url: str
    """SiLA Server Vendor URL"""

    service_broadcaster: SilaServiceBroadcaster
    running_instances: List[SilaServiceInfo]

    binary_transfer_handler: ServerBinaryTransferHandler

    metadata_interceptors: List[MetadataInterceptor]
    """Registered metadata interceptors"""

    children_by_fully_qualified_identifier: Dict[
        FullyQualifiedIdentifier,
        Union[
            Feature,
            Command,
            Property,
            Parameter,
            Response,
            IntermediateResponse,
            DefinedExecutionErrorNode,
            DataTypeDefinition,
            Metadata,
        ],
    ]
    """All child elements, accessible by their fully qualified identifier"""

    def __init__(
        self,
        server_name: str,
        server_type: str,
        server_description: str,
        server_version: str,
        server_vendor_url: str,
        server_uuid: Optional[Union[str, UUID]] = None,
        max_grpc_workers: int = 100,
        max_child_task_workers: int = 100,
    ):
        """
        SiLA Server

        Parameters
        ----------
        server_name
            SiLA Server Name, max. 255 characters
        server_type
            SiLA Server Type, must start with a capital letter and can only contain letters (a-z, A-Z) and digits (0-9)
        server_description
            SiLA Server Description
        server_version
            SiLA Server Version, e.g. ``"1.2"``, ``"1.2.3"``, or ``"1.2.3_beta"``.

            Pattern: ``Major.Minor.Patch_Details``,
            where *Major*, *Minor* und *Patch* are numeric, *Details* is text (a-z, A-Z, 0-9, _).
            *Patch* and *Details* are optional.
        server_vendor_url
            SiLA Server Vendor URL: The product or vendor homepage, must start with ``"http://"`` or ``"https://"``
        server_uuid
            SiLA Server UUID. If given as a string, it must be formatted like ``"082bc5dc-18ae-4e17-b028-6115bbc6d21e"``
        max_grpc_workers
            Max. number of worker threads used by gRPC
        max_child_task_workers
            Max. number of worker threads used by the implementation
            (e.g. observable command instances, observable property subscriptions, ...)
        """
        self.__was_started = False
        self.__is_running = False
        self.logger = logging.getLogger(__name__)
        self.generated_ca = None

        # import locally to prevent circular import
        from sila2.features.silaservice import SiLAServiceFeature
        from sila2.server.silaservice_impl import SiLAServiceImpl

        silaservice_fdl_tree = parse_feature_definition(SiLAServiceFeature._feature_definition)

        name_constraint = MaximalLength(
            int(
                xpath_sila(
                    silaservice_fdl_tree,
                    "//sila:Command[sila:Identifier/text() = 'SetServerName']//sila:MaximalLength/text()",
                )[0]
            )
        )
        type_constraint = Pattern(
            xpath_sila(
                silaservice_fdl_tree, "//sila:Property[sila:Identifier/text() = 'ServerType']//sila:Pattern/text()"
            )[0]
        )
        version_constraint = Pattern(
            xpath_sila(
                silaservice_fdl_tree, "//sila:Property[sila:Identifier/text() = 'ServerVersion']//sila:Pattern/text()"
            )[0]
        )
        vendor_url_constraint = Pattern(
            xpath_sila(
                silaservice_fdl_tree, "//sila:Property[sila:Identifier/text() = 'ServerVendorURL']//sila:Pattern/text()"
            )[0]
        )

        if not name_constraint.validate(server_name):
            raise ValueError(f"Server name {server_name!r} does not satisfy constraint {name_constraint!r}")
        if not type_constraint.validate(server_type):
            raise ValueError(f"Server type {server_type!r} does not satisfy constraint {type_constraint!r}")
        if not version_constraint.validate(server_version):
            raise ValueError(
                f"Server version {server_version!r} does not satisfy constraint {version_constraint!r}. "
                f"Examples: '2.1', '0.1.3', '1.2.3_preview'"
            )
        if not vendor_url_constraint.validate(server_vendor_url):
            raise ValueError(
                f"Server vendor url {server_vendor_url!r} does not satisfy constraint {vendor_url_constraint!r}"
            )

        self.server_name = server_name
        self.server_type = server_type
        if server_uuid is None:
            self.server_uuid = uuid.uuid4()
        else:
            self.server_uuid = server_uuid if isinstance(server_uuid, UUID) else UUID(server_uuid)
        self.server_description = server_description
        self.server_version = server_version
        self.server_vendor_url = server_vendor_url

        self.grpc_server = grpc.server(
            ThreadPoolExecutor(max_workers=max_grpc_workers, thread_name_prefix=f"grpc-executor-{self.server_uuid}")
        )
        self.service_broadcaster = SilaServiceBroadcaster()
        self.running_instances = []
        self.features = {}
        self.feature_servicers = {}
        self.metadata_interceptors = []

        self.binary_transfer_handler = ServerBinaryTransferHandler(self.grpc_server)

        self.child_task_executor = ThreadPoolExecutor(
            max_workers=max_child_task_workers, thread_name_prefix=f"child-task-executor-{self.server_uuid}"
        )

        self.children_by_fully_qualified_identifier = {}

        self.set_feature_implementation(SiLAServiceFeature, SiLAServiceImpl(parent_server=self))

    def set_feature_implementation(self, feature: Feature, implementation: FeatureImplementationBase) -> None:
        """
        Set a feature implementation

        Parameters
        ----------
        feature
            Feature to implement
        implementation
            Feature implementation

        Raises
        ------
        RuntimeError
            If the server was already started, or another implementation of the feature already was set
        """
        if self.__was_started:
            raise RuntimeError("Can only add features before starting the server")
        if feature._identifier in self.feature_servicers:
            raise RuntimeError("Can only add one implementation per feature")

        class FeatureServicer(FeatureImplementationServicer, feature._servicer_cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.set_implementation(implementation)

        servicer: FeatureImplementationServicer = FeatureServicer(self, feature)
        self.features[feature._identifier] = feature
        self.feature_servicers[feature._identifier] = servicer

        # add self as servicer to the gRPC server
        getattr(feature._grpc_module, f"add_{feature._identifier}Servicer_to_server")(servicer, self.grpc_server)

        feature._binary_transfer_handler = self.binary_transfer_handler
        self.children_by_fully_qualified_identifier[feature.fully_qualified_identifier] = feature
        self.children_by_fully_qualified_identifier.update(feature.children_by_fully_qualified_identifier)

    def add_metadata_interceptor(self, interceptor: MetadataInterceptor):
        """
        Add an interceptor for SiLA Client Metadata handling

        Parameters
        ----------
        interceptor
            Interceptor to add

        Raises
        ------
        RuntimeError
            If the server is already running
        """
        if self.__is_running:
            raise RuntimeError("Cannot add metadata interceptors to running servers")
        self.metadata_interceptors.append(interceptor)

    def __start(
        self,
        address: str,
        port: int,
        *,
        insecure: bool,
        private_key: Optional[bytes] = None,
        cert_chain: Optional[bytes] = None,
        enable_discovery: bool = True,
    ):
        # start grpc server
        if self.__was_started:
            raise RuntimeError("Cannot start server twice")

        address_string = f"{address}:{port}"
        self.generated_ca = None
        if insecure:
            self.logger.warning("Starting SiLA server without encryption. This violates the SiLA 2 specification.")
            self.grpc_server.add_insecure_port(address_string)
        else:
            if private_key is None and cert_chain is None:
                if not enable_discovery:
                    raise ValueError("If discovery is disabled, private key and certificate chain are required")

                self.logger.info("Generating self-signed certificate")
                private_key, cert_chain = generate_self_signed_certificate(self.server_uuid, address)
                self.generated_ca = cert_chain
            if private_key is None or cert_chain is None:
                raise ValueError(
                    "For secure connections, either provide both the private key and certificate chain, "
                    "or none of them (server will then generate a self-signed certificate)"
                )
            self.logger.info("Starting SiLA server with encryption")
            credentials = grpc.ssl_server_credentials([(private_key, cert_chain)])
            self.grpc_server.add_secure_port(address_string, server_credentials=credentials)
        self.grpc_server.start()

        # start implementations
        for servicer in self.feature_servicers.values():
            servicer.start()

        # start zeroconf broadcasting
        if enable_discovery:
            self.logger.info("Starting zeroconf broadcasting for SiLA Server Discovery")
            info = self.service_broadcaster.register_server(self, address, port, ca=self.generated_ca)
            self.running_instances.append(info)

        self.__is_running = True
        self.__was_started = True

    def start_insecure(self, address: str, port: int, enable_discovery: bool = True) -> None:
        """
        Start the server using unencrypted communication

        Parameters
        ----------
        address
            IP address or hostname where the server should run
        port
            Port where the server should run
        enable_discovery
            Whether to broadcast the server address for SiLA Server Discovery

        Notes
        -----
        From the SiLA Specification:

            It is RECOMMENDED that all SiLA Servers have SiLA Server Discovery enabled by default, but all
            SiLA Devices MUST have SiLA Server Discovery enabled by default.
        """
        self.__start(address, port, insecure=True, enable_discovery=enable_discovery)

    def start(
        self,
        address: str,
        port: int,
        private_key: bytes = None,
        cert_chain: bytes = None,
        enable_discovery: bool = True,
    ):
        """
        Start the server using unencrypted communication

        When no encryption information is provided, a self-signed certificate is generated.
        Its PEM-encoded certificate authority is then stored in :py:attr:`sila2.server.SilaServer.generated_ca`.

        Parameters
        ----------
        address
            IP address or hostname where the server should run
        port
            Port where the server should run
        private_key
            PEM-encoded private key for encrypted communication
        cert_chain
            PEM-encoded certificate chain for encrypted communication
        enable_discovery
            Whether to broadcast the server address for SiLA Server Discovery

        Warnings
        --------
        Using unencrypted communication violates the SiLA specification and should only be used for testing purposes

        Notes
        -----
        From the SiLA Specification:

            It is RECOMMENDED that all SiLA Servers have SiLA Server Discovery enabled by default, but all
            SiLA Devices MUST have SiLA Server Discovery enabled by default.
        """
        self.__start(
            address,
            port,
            insecure=False,
            private_key=private_key,
            cert_chain=cert_chain,
            enable_discovery=enable_discovery,
        )

    def stop(self, grace_period: Optional[float] = None):
        # stop zeroconf broadcasting
        for info in self.running_instances:
            self.service_broadcaster.unregister_server(info)
            self.running_instances.remove(info)

        # stop feature implementations
        for servicer in self.feature_servicers.values():
            servicer.cancel_all_subscriptions()
            servicer.implementation.stop()
        self.child_task_executor.shutdown(wait=True)

        # stop grpc server
        self.grpc_server.stop(grace_period).wait()

        self.__is_running = False

    def __getitem__(self, item: str) -> Feature:
        return self.features[item]

    def __del__(self):
        try:
            if self.__is_running:
                self.stop()
        except AttributeError:  # when __init__ fails, some attributes might not exist yet, then they cannot be stopped
            pass

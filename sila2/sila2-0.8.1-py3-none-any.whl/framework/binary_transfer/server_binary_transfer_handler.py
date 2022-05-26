from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Dict, Optional, Type
from uuid import UUID

from grpc import Server

from sila2.framework.abc.binary_transfer_handler import BinaryTransferHandler
from sila2.framework.abc.binary_transfer_handler import grpc_module as binary_transfer_grpc_module
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.binary_transfer.download_servicer import BinaryDownloadServicer
from sila2.framework.binary_transfer.invalid_binary_transfer_uuid import InvalidBinaryTransferUUID
from sila2.framework.binary_transfer.upload_servicer import BinaryUploadServicer

if TYPE_CHECKING:
    from sila2.framework.pb2.SiLAFramework_pb2 import Binary as SilaBinary


class ServerBinaryTransferHandler(BinaryTransferHandler):
    upload_servicer: binary_transfer_grpc_module.BinaryUploadServicer
    download_servicer: binary_transfer_grpc_module.BinaryDownloadServicer
    known_binaries: Dict[UUID, bytes]

    def __init__(self, grpc_server: Server):
        self.upload_servicer = BinaryUploadServicer(self)
        self.download_servicer = BinaryDownloadServicer(self)
        binary_transfer_grpc_module.add_BinaryUploadServicer_to_server(self.upload_servicer, grpc_server)
        binary_transfer_grpc_module.add_BinaryDownloadServicer_to_server(self.download_servicer, grpc_server)

        self.known_binaries = {}

    def to_native_type(self, binary_uuid: UUID, toplevel_named_data_node: Optional[NamedDataNode] = None) -> bytes:
        try:
            return self.known_binaries[binary_uuid]
        except KeyError:
            raise InvalidBinaryTransferUUID(f"Invalid binary transfer UUID: {binary_uuid}")

    def to_message(
        self, binary: bytes, message_type: Type[SilaBinary], toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> SilaBinary:
        binary_uuid = uuid.uuid4()
        self.known_binaries[binary_uuid] = binary
        return message_type(binaryTransferUUID=str(binary_uuid))

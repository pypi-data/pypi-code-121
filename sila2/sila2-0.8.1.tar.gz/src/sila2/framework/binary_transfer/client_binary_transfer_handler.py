from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Type
from uuid import UUID

from grpc import Channel

from sila2.framework.abc.binary_transfer_handler import BinaryTransferHandler
from sila2.framework.abc.binary_transfer_handler import grpc_module as binary_transfer_grpc_module
from sila2.framework.abc.binary_transfer_handler import pb2_module as binary_transfer_pb2_module
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.binary_transfer.binary_download_failed import BinaryDownloadFailed
from sila2.framework.binary_transfer.binary_transfer_error import BinaryTransferError
from sila2.framework.command.parameter import Parameter
from sila2.framework.utils import consume_generator

if TYPE_CHECKING:
    from sila2.framework.pb2.SiLAFramework_pb2 import Binary as SilaBinary


class ClientBinaryTransferHandler(BinaryTransferHandler):
    upload_stub: binary_transfer_grpc_module.BinaryUploadStub
    download_stub: binary_transfer_grpc_module.BinaryDownloadStub
    chunk_size = 1024**2  # 1 MB
    known_binaries: Dict[UUID, bytes]

    def __init__(self, channel: Channel):
        self.upload_stub = binary_transfer_grpc_module.BinaryUploadStub(channel)
        self.download_stub = binary_transfer_grpc_module.BinaryDownloadStub(channel)
        self.known_binaries = {}

    def to_native_type(self, binary_uuid: UUID, toplevel_named_data_node: Optional[NamedDataNode] = None) -> bytes:
        """Get binary data from a server response"""
        try:
            if binary_uuid in self.known_binaries:
                return self.known_binaries[binary_uuid]

            size: int = self.download_stub.GetBinaryInfo(
                binary_transfer_pb2_module.GetBinaryInfoRequest(binaryTransferUUID=str(binary_uuid))
            ).binarySize

            n_chunks = self.__compute_chunk_count(size)
            chunk_requests = (
                binary_transfer_pb2_module.GetChunkRequest(
                    binaryTransferUUID=str(binary_uuid), offset=i * self.chunk_size, length=self.chunk_size
                )
                for i in range(n_chunks)
            )

            raw_result = bytearray(size)
            for chunk_response in self.download_stub.GetChunk(chunk_requests):
                raw_result[chunk_response.offset : chunk_response.offset + self.chunk_size] = chunk_response.payload

            result = bytes(raw_result)
            self.known_binaries[binary_uuid] = result

            # request deletion to free up server resources
            self.download_stub.DeleteBinary(
                binary_transfer_pb2_module.DeleteBinaryRequest(binaryTransferUUID=str(binary_uuid))
            )
            return result
        except Exception as ex:
            if BinaryTransferError.is_binary_transfer_error(ex):
                raise BinaryTransferError.from_rpc_error(ex)
            raise BinaryDownloadFailed(f"Exception during binary download: {ex}")

    def to_message(
        self, binary: bytes, message_type: Type[SilaBinary], toplevel_named_data_node: Parameter
    ) -> SilaBinary:
        """Upload binary data to server"""
        try:
            n_chunks = self.__compute_chunk_count(len(binary))
            binary_uuid = UUID(
                self.upload_stub.CreateBinary(
                    binary_transfer_pb2_module.CreateBinaryRequest(
                        binarySize=len(binary),
                        chunkCount=n_chunks,
                        parameterIdentifier=toplevel_named_data_node.fully_qualified_identifier,
                    )
                ).binaryTransferUUID
            )

            chunk_requests = (
                binary_transfer_pb2_module.UploadChunkRequest(
                    binaryTransferUUID=str(binary_uuid),
                    chunkIndex=i,
                    payload=binary[i * self.chunk_size : (i + 1) * self.chunk_size],
                )
                for i in range(self.__compute_chunk_count(len(binary)))
            )

            chunk_responses = self.upload_stub.UploadChunk(chunk_requests)
            # UploadChunk can be implemented lazily so that a request is only processed once its response is requested
            consume_generator(chunk_responses)

            return message_type(binaryTransferUUID=str(binary_uuid))
        except Exception as ex:
            try:
                raise BinaryTransferError.from_rpc_error(ex)
            except:  # noqa: E722
                raise BinaryDownloadFailed(f"Exception during binary upload: {ex}")

    def __compute_chunk_count(self, binary_size: int) -> int:
        return binary_size // self.chunk_size + (1 if binary_size % self.chunk_size != 0 else 0)

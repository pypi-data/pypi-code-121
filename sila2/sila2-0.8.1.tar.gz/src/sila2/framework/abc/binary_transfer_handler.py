from __future__ import annotations

from abc import ABC, abstractmethod
from os.path import join
from typing import TYPE_CHECKING, Type
from uuid import UUID

from sila2 import resource_dir
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.utils import run_protoc

pb2_module, grpc_module = run_protoc(join(resource_dir, "proto", "SiLABinaryTransfer.proto"))

if TYPE_CHECKING:
    from sila2.framework.pb2 import SiLABinaryTransfer_pb2, SiLABinaryTransfer_pb2_grpc
    from sila2.framework.pb2.SiLAFramework_pb2 import Binary as SilaBinary

    pb2_module = SiLABinaryTransfer_pb2
    grpc_module = SiLABinaryTransfer_pb2_grpc


class BinaryTransferHandler(ABC):
    @abstractmethod
    def to_native_type(self, binary_uuid: UUID, toplevel_named_data_node: NamedDataNode) -> bytes:
        pass

    @abstractmethod
    def to_message(
        self, binary: bytes, message_type: Type[SilaBinary], toplevel_named_data_node: NamedDataNode
    ) -> SilaBinary:
        pass

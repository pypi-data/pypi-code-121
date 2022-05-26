from __future__ import annotations

from base64 import standard_b64decode
from enum import Enum
from typing import TYPE_CHECKING

import grpc
from grpc import RpcError

from sila2.framework.abc.binary_transfer_handler import pb2_module as binary_transfer_pb2_module

if TYPE_CHECKING:
    from sila2.framework.pb2 import SiLABinaryTransfer_pb2
    from sila2.framework.pb2.SiLABinaryTransfer_pb2 import BinaryTransferError as SilaBinaryTransferError


class BinaryTransferError(Exception):
    _pb2_module: SiLABinaryTransfer_pb2 = binary_transfer_pb2_module
    error_type: BinaryTransferErrorType
    message: str

    def __init__(self, error_type: BinaryTransferErrorType, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)

    def to_message(self) -> SilaBinaryTransferError:
        error_type = getattr(self._pb2_module.BinaryTransferError, self.error_type.name)
        return self._pb2_module.BinaryTransferError(errorType=error_type, message=self.message)

    @staticmethod
    def is_binary_transfer_error(exception: Exception) -> bool:
        if not isinstance(exception, RpcError):
            return False
        if not exception.code() == grpc.StatusCode.ABORTED:
            return False
        try:
            BinaryTransferError._pb2_module.BinaryTransferError.FromString(standard_b64decode(exception.details()))
        except:  # noqa: E722
            return False
        return True

    @classmethod
    def from_rpc_error(cls, rpc_error: RpcError):
        if not cls.is_binary_transfer_error(rpc_error):
            raise ValueError("Error is no BinaryTransferError")

        bin_err = cls._pb2_module.BinaryTransferError.FromString(standard_b64decode(rpc_error.details()))
        if bin_err.errorType == bin_err.BINARY_DOWNLOAD_FAILED:
            from sila2.framework.binary_transfer.binary_download_failed import BinaryDownloadFailed

            return BinaryDownloadFailed(bin_err.message)
        if bin_err.errorType == bin_err.BINARY_UPLOAD_FAILED:
            from sila2.framework.binary_transfer.binary_upload_failed import BinaryUploadFailed

            return BinaryUploadFailed(bin_err.message)
        if bin_err.errorType == bin_err.INVALID_BINARY_TRANSFER_UUID:
            from sila2.framework.binary_transfer.invalid_binary_transfer_uuid import InvalidBinaryTransferUUID

            return InvalidBinaryTransferUUID(bin_err.message)

        raise NotImplementedError(f"BinaryTransferType type not supported: {bin_err.errorType}")  # should not happen


class BinaryTransferErrorType(Enum):
    INVALID_BINARY_TRANSFER_UUID = 0
    BINARY_UPLOAD_FAILED = 1
    BINARY_DOWNLOAD_FAILED = 2

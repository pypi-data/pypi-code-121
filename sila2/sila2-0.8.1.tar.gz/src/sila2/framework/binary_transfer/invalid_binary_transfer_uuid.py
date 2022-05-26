from sila2.framework.binary_transfer.binary_transfer_error import BinaryTransferError, BinaryTransferErrorType


class InvalidBinaryTransferUUID(BinaryTransferError):
    def __init__(self, message: str):
        super().__init__(BinaryTransferErrorType.INVALID_BINARY_TRANSFER_UUID, message)

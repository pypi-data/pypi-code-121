from sila2.framework.binary_transfer.binary_transfer_error import BinaryTransferError, BinaryTransferErrorType


class BinaryUploadFailed(BinaryTransferError):
    def __init__(self, message: str):
        super().__init__(BinaryTransferErrorType.BINARY_UPLOAD_FAILED, message)

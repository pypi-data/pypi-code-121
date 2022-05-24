from requests import Response

from .storage_exception import StorageException


class StorageServerException(StorageException):
    def __init__(
        self,
        message: str,
        original_exception: Exception = None,
        url: str = "",
        method: str = "GET",
        status_code: int = None,
        scope: str = "http request",
        http_response: Response = None,
    ):
        super().__init__(message)

        self.status_code = getattr(original_exception, "status_code", status_code)
        self.url = getattr(original_exception, "url", url)
        self.method = getattr(original_exception, "method", method)
        self.scope = scope
        self.message = message
        self.http_response = http_response

    def __str__(self):
        return (
            f"scope: {self.scope}, url: {self.url}, method: {self.method}, status_code: {self.status_code}"
            f" - {self.message}"
        )


class StorageNetworkException(StorageServerException):
    pass


class StorageAuthenticationException(StorageServerException):
    pass


class StorageServerResponseValidationException(StorageServerException):
    pass


class StorageCountryNotSupportedException(StorageServerException):
    def __init__(self, message="Requested country is not supported", country=None):
        super().__init__(message)

        self.country = country
        self.message = message

    def __str__(self):
        return f"{self.message}: country '{self.country}' is not supported"

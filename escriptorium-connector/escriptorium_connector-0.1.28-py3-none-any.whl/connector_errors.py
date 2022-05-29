# This file contains the escriptorium_connector specific
# Error types so the package user has a convenient
# Exception catching framework.

import requests


class EscriptoriumConnectorError(BaseException):
    ...

class EscriptoriumonnectorInitError(EscriptoriumConnectorError):
    ...

class EscriptoriumConnectorHttpError(EscriptoriumConnectorError):
    def __init__(self, error_message: str, http_error: requests.HTTPError):
        self.django_error = error_message
        self.error = http_error

    def __str__(self):
        return self.django_error

    def __repr__(self):
        nl = "\n"
        return f"""{self.django_error}{nl}{repr(self.error)}"""


class EscriptoriumConnectorDtoError(EscriptoriumConnectorError):
    def __init__(
        self,
        original_error: BaseException,
        request_status: int,
        url: str,
        raw_response: str,
    ):
        self.original_error = original_error
        self.request_status = request_status
        self.url = url
        self.raw_response = raw_response

    def __str__(self):
        nl = "\n"
        return f"""HTTP request code: {self.request_status}{nl}from: {self.url}{nl}{self.request_status}{nl}with response: {self.raw_response}"""

    def __repr__(self):
        nl = "\n"
        return f"""{repr(self.original_error)}{nl}{str(self)}"""


class EscriptoriumConnectorDtoSyntaxError(EscriptoriumConnectorDtoError):
    ...


class EscriptoriumConnectorDtoTypeError(EscriptoriumConnectorDtoError):
    ...


class EscriptoriumConnectorDtoValidationError(EscriptoriumConnectorDtoError):
    ...

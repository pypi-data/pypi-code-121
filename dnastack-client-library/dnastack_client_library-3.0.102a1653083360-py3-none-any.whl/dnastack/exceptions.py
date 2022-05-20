from typing import List, Type, AnyStr, Optional

from requests import Response


class PublisherException(Exception):
    """
    The base class for exceptions within the Publisher python library
    """

    def __str__(self):
        return str(self.__repr__())


class ConfigException(PublisherException):
    def __init__(self, key: str):
        super().__init__()

        self.key = key


def display_keys(obj: dict, prefix: str = None) -> str:
    output = ""
    for key in sorted(obj.keys()):
        if isinstance(obj[key], dict):
            if prefix:
                output += display_keys(obj[key], prefix=f"{prefix}.{key}")
            else:
                output += display_keys(obj[key], prefix=f"{key}")
        else:
            if prefix:
                output += f"\t{prefix}.{key}\n"
            else:
                output += f"\t{key}\n"
    return output


class NoConfigException(ConfigException):
    def __repr__(self):
        return f"There is no configuration value for key [{self.key}]"


class InvalidConfigTypeException(ConfigException):
    def __init__(self, expected: Type, actual: Type, key: str):
        super().__init__(key)
        self.expected = expected
        self.actual = actual

    def __repr__(self):
        return f"Expected type [{self.expected}] for config variable [{self.key}], got [{self.actual}]"


class ServiceException(PublisherException):
    """
    An Exception that is raised for errors within Services
    """

    def __init__(self, msg: str = None, url: str = None):
        super().__init__()

        self.msg = msg
        self.url = url

    def __repr__(self):
        if self.url:
            return f"{self.url}: {self.msg or ''}"
        else:
            return self.msg or ''


class InvalidOAuthClientParamsError(PublisherException):
    def __init__(self, msg: AnyStr = None):
        self.msg = msg

    def __repr__(self):
        error_msg = f"Unable to build OAuth Client from provided parameters"

        if self.msg:
            error_msg += f": {self.msg}"

        return error_msg


class ServiceTypeException(PublisherException):
    """
    An Exception that is raised for inconsistencies in service types
    """

    def __init__(self, expected_type: str, actual_type: str):
        super().__init__()

        self.expected_type = expected_type
        self.actual_type = actual_type

    def __repr__(self):
        return f"Expected service type [{self.expected_type}], got [{self.actual_type}]"


class ServiceTypeNotFoundError(PublisherException):
    def __init__(self, service_type: str):
        super().__init__()

        self.service_type = service_type

    def __repr__(self):
        return f"Could not find service type of name [{self.service_type}]"


class ServiceRegistryException(ServiceException):
    def __init__(self, url: AnyStr = None, msg: AnyStr = None):
        super().__init__(msg=msg, url=url)

    def __repr__(self):
        error_msg = f"Error while getting service registry information"
        if self.url:
            error_msg += f" from [{self.url}]"
        if self.msg:
            error_msg += f": {self.msg}"
        return error_msg


class InsufficientAuthInfoError(RuntimeError):
    pass


class AuthException(ServiceException):
    pass


class LoginException(AuthException):
    def __repr__(self):
        if not self.url:
            return self.msg
        return f"Could not log into [{self.url}]: {self.msg}"


class RefreshException(AuthException):
    def __repr__(self):
        return f"Could not refresh token for [{self.url}]: {self.msg}"


class OAuthTokenException(AuthException):
    def __repr__(self):
        return f"Could not fetch the OAuth token for [{self.url}]: {self.msg}"


class DRSException(PublisherException):
    def __init__(self, msg: str = None, url: str = None, object_id: str = None):
        self.msg = msg
        self.url = url
        self.object_id = object_id

    def __repr__(self):
        error_msg = "Failure downloading DRS object"
        if self.url:
            error_msg += f" with url [{self.url}]"
        elif self.object_id:
            error_msg += f" with object ID [{self.object_id}]"
        if self.msg:
            error_msg += f": {self.msg}"
        return error_msg


class DRSDownloadException(PublisherException):
    def __init__(self, errors: List[DRSException] = None):
        self.errors = errors

    def __repr__(self):
        error_msg = f"One or more downloads failed:\n"
        for err in self.errors:
            error_msg += f"{err}\n"
        return error_msg


class WorkflowFailedException(PublisherException):
    pass


class PaginationError(PublisherException):
    def __init__(self, response: Response, page_url: AnyStr = None, msg: AnyStr = None):
        self.response = response
        self.page_url = page_url
        self.msg = msg

    def __repr__(self):
        error_msg = "There was an error while getting the paginated response"

        if self.response:
            error_msg += f" for [{self.response.url}]"

        if self.page_url:
            error_msg += f": Error getting page [{self.page_url}]"

        if self.msg:
            error_msg += f": {self.msg}"

        return error_msg

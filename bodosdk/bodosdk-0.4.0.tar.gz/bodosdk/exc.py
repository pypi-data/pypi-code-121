class ResourceNotFound(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class UnknownError(Exception):
    pass


class ValidationError(Exception):
    pass


class Unauthorized(Exception):
    pass


class APIKeysMissing(Exception):
    pass


class WaiterTimeout(Exception):
    pass
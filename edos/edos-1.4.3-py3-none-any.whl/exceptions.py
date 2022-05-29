class UserReadableException(Exception):
    pass


class SecretDoesNotExists(UserReadableException):
    pass


class DatabaseEngineNotSupported(UserReadableException):
    pass


class DatabaseCreationError(UserReadableException):
    pass


class ServiceDoesNotExists(UserReadableException):
    pass


class TaskDoesNotExists(UserReadableException):
    pass


class SecretCreationError(UserReadableException):
    pass


class SecretRemovalError(UserReadableException):
    pass


class ContainerDoesNotExists(UserReadableException):
    pass


class SpaceCreationError(UserReadableException):
    pass

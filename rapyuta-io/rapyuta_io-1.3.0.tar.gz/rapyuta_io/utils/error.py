# encoding: utf-8

# custom error class for the API


class PackageNotFound(Exception):
    pass


class PlanNotFound(Exception):
    pass


class InsufficientResourceError(Exception):
    pass


class ServiceBindingError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class APIError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ResourceNotFoundError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class UnauthorizedError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ForbiddenError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class BadRequestError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class OperationNotAllowedError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeviceNotFoundException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ParameterMissingException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class LabelNotFoundException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ConfigNotFoundException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeserializationException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeploymentRunningException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class CommandException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class InvalidCommandException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class InvalidAuthTokenException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class InvalidParameterException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class UnknownTopicException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class UnknownTopicStatusException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class RetriesExhausted(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeploymentNotRunningException(Exception):
    """
    :ivar deployment_status: Deployment status object retrieved from the last poll
    """
    def __init__(self, msg, deployment_status=None):
        self.deployment_status = deployment_status
        Exception.__init__(self, msg)


class ComponentNotFoundException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class AliasNotProvidedException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DuplicateAliasException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class LogsUUIDNotFoundException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class InternalServerError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ConflictError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class BuildFailed(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ROSBagBlobError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class BuildOperationFailed(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)



from unittest import expectedFailure


class NotFoundError(Exception):
    pass


class InvalidDataError(Exception):
    pass


class ScytheError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class TooManyRequestsError(Exception):
    pass


class MultipleResultsError(Exception):
    """Multiple objects returned for fetch"""
    pass

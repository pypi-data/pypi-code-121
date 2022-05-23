class CrudException(Exception):
    """A generic crud exception."""


class ItemNotFoundException(CrudException):
    """Raised if an item cannot be found."""


class InvalidPayloadException(CrudException):
    """Raised if the payload is not valid."""

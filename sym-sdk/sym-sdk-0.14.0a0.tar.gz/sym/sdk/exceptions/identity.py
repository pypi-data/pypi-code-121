from sym.sdk.exceptions.sym_exception import ExceptionWithHint, SymException


class IdentityError(SymException):
    """This is the base class for errors that occur when managing identities.

    Args:
        name: The name of the exception (used as the second part of the error code, e.g. COULD_NOT_SAVE)
        message: The exception message to display
    """

    def __init__(self, name: str, message: str, error_type: str = "Identity"):
        super().__init__(error_type=error_type, name=name, message=message)


class CouldNotSaveError(IdentityError):
    """This error is raised in cases where a :class:`~sym.sdk.user.UserIdentity`
    was unable to be saved.
    """

    def __init__(self, message: str):
        super().__init__("COULD_NOT_SAVE", message)


class IdentityNotFound(IdentityError, ExceptionWithHint):
    """This error is raised in cases where a mapping of a Sym :class:`~sym.sdk.user.User` to an
    external identity (i.e., a :class:`~sym.sdk.user.UserIdentity`) could not be found and could not
    be automatically determined from the corresponding service.

    Args:
        email: The email address of the user for which identity lookup could not be performed
        service_id: The unique Implementer-provided identifier of the service for which identity
            lookup was needed
    """

    def __init__(self, email: str, service_id: str):
        super().__init__(
            "NOT_FOUND",
            f"Could not find or determine external identity for {email} in service {service_id}",
        )

    @property
    def hint(self) -> str:
        return "An Implementer can use the symflow CLI to manually add the user's identity"

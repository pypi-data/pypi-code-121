from abc import abstractmethod


class SymException(Exception):
    """This is the base class for all exceptions raised by the Sym Runtime.

    Args:
        error_type: The class of exception (used as the first part of the error_code, e.g. AuthenticationError)
        name: The name of the exception (used as the second part of the error_code, e.g. INVALID_JWT)
        message: The exception message to display
    """

    def __init__(self, error_type: str, name: str, message: str):
        self.message = message
        self.error_code = f"{error_type}:{name}"
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error": True,
            "message": self.message,
            "code": self.error_code,
        }


class ExceptionWithHint(SymException):
    """A trait that can be mixed into Exception classes that want to have messages formatted with a
    hint.

    Overrides the ``__str__`` method to provide a formatted output string.

    i.e. the output will look like
    > This is my main exception message
    >
    > *Hint:* This is the exception hint

    Caution: This class should not be used for matching exceptions in ``except`` statements!
    """

    @property
    @abstractmethod
    def hint(self) -> str:
        """The string to be displayed in the Hint section"""
        ...

    def __str__(self):
        return f"{self.message}\n\n*Hint:* {self.hint}"

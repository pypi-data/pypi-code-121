from typing import Any, Optional

class ArgumentException(Exception):
    """Raised when a method is invoked with an invalid argument."""

    def __init__(self, name: str, value: Any, message: Optional[str] = None) -> None:
        """Initializes a new instance.

        :param name: The name of the argument.
        :type name: str
        :param value: The actual value of the argument.
        :type value: Any
        :param message: An optional message that describes the problem, defaults to None.
        :type message: str, optional
        """

        super().__init__(message)
        self.__name: str = name
        self.__value: str = value

    @property
    def name(self) -> str:
        """Gets the name of the argument that caused the exception.

        :return: The name of the argument.
        :rtype: str
        """

        return self.__name

    @property
    def value(self) -> Any:
        """Gets the actual value of the argument that caused the exception.

        :return: The actual value of the argument.
        :rtype: Any
        """

        return self.__value

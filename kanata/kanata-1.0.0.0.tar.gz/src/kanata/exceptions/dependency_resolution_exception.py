from typing import Any, Optional, Type

class DependencyResolutionException(Exception):
    """Raised when dependency resolution fails."""

    def __init__(
        self,
        related_type: Optional[Type[Any]] = None,
        message: Optional[str] = None) -> None:
        """Initializes a new instance.

        :param related_type: An optional type related to the exception, defaults to None.
        :type related_type: Optional[Type[Any]]
        :param message: An optional message that describes the problem, defaults to None.
        :type message: Optional[str], optional
        """

        super().__init__(message)
        self.__related_type: Optional[Type[Any]] = related_type

    @property
    def related_type(self) -> Optional[Type[Any]]:
        """Gets the type related to the exception.

        :return: The type related to the exception.
        :rtype: Optional[Type[Any]]
        """

        return self.__related_type

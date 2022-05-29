from typing import Any

class DuplicateNodeException(Exception):
    """Raised when a duplicate node is detected in a graph."""

    def __init__(self, node: Any, *args: object) -> None:
        """Initializes a new instance.

        :param node: The node that causes the duplication.
        :type node: Any
        """

        super().__init__(*args)
        self.__node: Any = node

    @property
    def node(self) -> Any:
        """Gets the node that causes the duplication.

        :return: The node that causes the duplication.
        :rtype: Any
        """

        return self.__node

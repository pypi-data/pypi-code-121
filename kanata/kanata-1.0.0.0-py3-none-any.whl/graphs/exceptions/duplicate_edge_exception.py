from typing import Any

class DuplicateEdgeException(Exception):
    """Raised when a duplicate edge is detected in a graph that doesn't allow them."""

    def __init__(self, node1: Any, node2: Any, *args: object) -> None:
        """Initializes a new instance.

        :param node1: The first of the nodes with the duplicate edges.
        :type node1: Any
        :param node2: The second of the nodes with the duplicate edges.
        :type node2: Any
        """

        super().__init__(*args)
        self.__node1: Any = node1
        self.__node2: Any = node2
    
    @property
    def node1(self) -> Any:
        """Gets the first of the two nodes that have the duplicate edges.

        :return: The first of the two nodes that have the duplicate edges.
        :rtype: Any
        """

        return self.__node1
    
    @property
    def node2(self) -> Any:
        """Gets the second of the two nodes that have the duplicate edges.

        :return: The second of the two nodes that have the duplicate edges.
        :rtype: Any
        """

        return self.__node2

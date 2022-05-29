from typing import Any, Set

class CyclicGraphException(Exception):
    """Raised when a cycle is detected in a graph which doesn't allow one."""

    def __init__(self, nodes: Set[Any], *args: object) -> None:
        """Initializes a new instance.

        :param nodes: The list of nodes that form the cycle.
        :type nodes: Set[Any]
        """

        super().__init__(*args)
        self.__nodes: Set[Any] = nodes
    
    @property
    def nodes(self) -> Set[Any]:
        """Gets the list of nodes that form the cycle.

        :return: The list of nodes that form the cycle.
        :rtype: Set[Any]
        """

        return self.__nodes

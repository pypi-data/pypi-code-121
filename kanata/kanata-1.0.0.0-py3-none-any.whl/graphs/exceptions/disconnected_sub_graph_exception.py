from typing import Any, Tuple

class DisconnectedSubGraphException(Exception):
    """Raised when a disconnected sub-graph is detected in a graph that doesn't allow it."""

    def __init__(self, nodes: Tuple[Any, ...], *args: object) -> None:
        """Initializes a new instance.

        :param nodes: The list of nodes that form the disconnected sub-graph.
        :type nodes: Tuple[Any, ...]
        """

        super().__init__(*args)
        self.__nodes: Tuple[Any, ...] = nodes
    
    @property
    def nodes(self) -> Tuple[Any, ...]:
        """Gets the list of nodes that form the disconnected sub-graph.

        :return: The list of nodes that form the disconnected sub-graph.
        :rtype: Tuple[Any, ...]
        """

        return self.__nodes

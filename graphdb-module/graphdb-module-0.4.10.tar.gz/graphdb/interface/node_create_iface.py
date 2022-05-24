from abc import ABC, abstractmethod
from typing import List

from graphdb.schema import Node


class NodeCreateInterface(ABC):
    """Base class for basic operation create node"""

    @abstractmethod
    def create_node(self, node: Node) -> Node:
        """Create new node with label and properties if set in node class
        it will search node, if exists then update that node only
        :param node: object node
        :return: object node
        """
        raise NotImplementedError

    @abstractmethod
    def create_multi_node(self, nodes: List[Node]) -> bool:
        """Create multiple node with label and properties if set in node class,
        this will doing upsert value
        :param nodes: list of object node
        :return: boolean value
        """
        raise NotImplementedError

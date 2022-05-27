from abc import ABC, abstractmethod
from typing import Dict, Any

from graphdb.schema import Node


class NodeUpdateInterface(ABC):
    """Base class for basic operation update node"""

    @abstractmethod
    def update_node_property(self, node: Node, update_query: Dict[str, Any]) -> Node:
        """Update node with specified properties
        :param node: object class node
        :param update_query: dictionary filter query
        :return: object node
        """
        raise NotImplementedError

    @abstractmethod
    def replace_node_property(self, node: Node, update_query: Dict[str, Any]) -> Node:
        """Replace node properties with new properties
        :param node: object class node
        :param update_query: dictionary filter query
        :return: object node
        """
        raise NotImplementedError

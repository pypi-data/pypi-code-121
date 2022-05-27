from abc import ABC, abstractmethod
from typing import List, Union

from graphdb.schema import Node


class NodeSearchInterface(ABC):
    """Base class for basic operation search or read node"""

    @abstractmethod
    def find_node(
        self,
        node: Node,
        limit: int = 100,
    ) -> List[Node]:
        """Find node with specified parameters
        :param node: object node
        :param limit: default limit query
        :return: list of object node
        """
        raise NotImplementedError

    @abstractmethod
    def find_node_within(
        self,
        label_name: str,
        key_name: str,
        value: Union[List[str], List[int], List[float]],
    ) -> List[Node]:
        """Find node with specified parameters with multiple filter
        :param label_name: string label name for that node
        :param key_name: string key that we want to search
        :param value: it can be primitive data type, value that we want to search
        :return: list of object node
        """
        raise NotImplementedError

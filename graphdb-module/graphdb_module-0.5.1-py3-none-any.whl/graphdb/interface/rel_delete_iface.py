from abc import ABC, abstractmethod
from typing import List, Optional

from graphdb.schema import Relationship, Node


class RelationshipDeleteInterface(ABC):
    """Base class for basic operation delete relationship node"""

    @abstractmethod
    def delete_relationship(
        self,
        rel: Relationship,
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Delete only relationship from specified node
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        raise NotImplementedError

    @abstractmethod
    def remove_all_relationship_property(
        self,
        rel: Relationship,
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Remove all property from this relationship
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object node
        :return: object relationship
        """
        raise NotImplementedError

    @abstractmethod
    def remove_relationship_property(
        self,
        rel: Relationship,
        properties: List[str],
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Remove specified property from relationship
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship
        :param properties: list of property you want to remove from this relationship
        :return: object relationship
        """
        raise NotImplementedError

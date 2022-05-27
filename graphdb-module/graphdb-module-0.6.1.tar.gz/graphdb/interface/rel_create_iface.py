from abc import ABC, abstractmethod

from graphdb.schema import Relationship, Node


class RelationshipCreateInterface(ABC):
    """Base class for basic operation create relationship node"""

    @abstractmethod
    def create_relationship_with_upsert(
        self, node_from: Node, node_to: Node, rel: Relationship
    ) -> Relationship:
        """Create new relationship between 2 nodes
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        raise NotImplementedError

    @abstractmethod
    def create_relationship_without_upsert(
        self, node_from: Node, node_to: Node, rel: Relationship
    ) -> Relationship:
        """Create one-to-many relationships
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        raise NotImplementedError

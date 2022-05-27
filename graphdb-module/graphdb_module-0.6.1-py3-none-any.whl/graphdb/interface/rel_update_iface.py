from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from graphdb.schema import Relationship, Node


class RelationshipUpdateInterface(ABC):
    """Base class for basic operation create relationship relationship"""

    @abstractmethod
    def update_relationship_property(
        self,
        rel: Relationship,
        update_query: Dict[str, Any],
        node_from: Node = None,
        node_to: Node = None,
    ) -> Relationship:
        """Update relationship with specified properties
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object class relationship
        :param update_query: dictionary filter query
        :return: object relationship
        """
        raise NotImplementedError

    @abstractmethod
    def replace_relationship_property(
        self,
        rel: Relationship,
        update_query: Dict[str, Any],
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Replace relationship properties with new properties
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object class relationship
        :param update_query: dictionary filter query
        :return: object relationship
        """
        raise NotImplementedError

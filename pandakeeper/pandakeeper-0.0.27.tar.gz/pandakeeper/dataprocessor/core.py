from itertools import chain, repeat
from types import MappingProxyType
from typing import Optional, Union, Dict, List, Tuple, Iterator, Iterable, Mapping

import pandas as pd
from pandera import DataFrameSchema
from typing_extensions import final
from varutils.typing import check_type_compatibility

from pandakeeper.node import Node
from pandakeeper.validators import AnyDataFrame

__all__ = (
    'NodeConnection',
    'DataProcessor'
)


class NodeConnection:
    """Class that encapsulates a connection to an input Node."""
    __slots__ = ('__node', '__input_validator')

    def __init__(self, node: Node, input_validator: DataFrameSchema = AnyDataFrame) -> None:
        """
        Class that encapsulates a connection to an input Node.

        Args:
            node:             input Node to connect to.
            input_validator:  DataFrameSchema that validates the data coming from the input Node.
        """
        check_type_compatibility(node, Node)
        check_type_compatibility(input_validator, DataFrameSchema)
        self.__node = node
        self.__input_validator = input_validator

    @final
    @property
    def node(self) -> Node:
        """Input Node."""
        return self.__node

    @final
    @property
    def input_validator(self) -> DataFrameSchema:
        """Input validator."""
        return self.__input_validator

    @final
    def extract_data(self) -> pd.DataFrame:
        """Extracts and validates data from the input Node."""
        data = self.__node.extract_data()
        return self.__input_validator.validate(data)


class DataProcessor(Node):
    """
    Abstract class that defines an interface common to all data processors,
    i.e. Nodes that can receive data from other Nodes through NodeConnection instances.
    """
    __slots__ = ('__positional_node_connections', '__named_node_connections')

    def __init__(self, output_validator: DataFrameSchema = AnyDataFrame):
        """
        Abstract class that defines an interface common to all data processors,
        i.e. Nodes that can receive data from other Nodes through NodeConnection instances.

        Args:
            output_validator: DataFrameSchema that validates the data coming from the 'extract_data' method.
        """
        super().__init__(output_validator)
        self.__positional_node_connections: List[NodeConnection] = []
        self.__named_node_connections: Dict[str, NodeConnection] = {}

    @final
    @property
    def positional_input_nodes(self) -> Tuple[NodeConnection, ...]:
        """Returns positional input NodeConnections."""
        return tuple(self.__positional_node_connections)

    @final
    @property
    def named_input_nodes(self) -> Mapping[str, NodeConnection]:
        """Returns named input NodeConnections."""
        return MappingProxyType(self.__named_node_connections)

    @final
    def __connect_input_node_body(self,
                                  node_connection: NodeConnection,
                                  keyword: Optional[str] = None) -> None:
        """
        Supplemental method used bt the 'connect_input_node' and the 'connect_input_nodes' methods.

        Args:
            node_connection:  Node to connect to or NodeConnection to add.
            keyword:          Optional name of the NodeConnection.
        """
        if keyword is None:
            self.__positional_node_connections.append(node_connection)
        else:
            named_node_connections = self.__named_node_connections
            if keyword in named_node_connections:
                raise KeyError(f"Duplicate name '{keyword}' for named NodeConnection")
            named_node_connections[keyword] = node_connection
        self._add_edge_to_connection_graph(node_connection.node)

    @staticmethod
    def __check_node_connection(node: Union[Node, NodeConnection],
                                keyword: Optional[str],
                                arg_position: int = 0) -> Tuple[NodeConnection, Optional[str]]:
        """
        Supplemental method used by the '__check_node_connections' and the 'connect_input_node' methods.

        Args:
            node:          Node to connect to or NodeConnection to add.
            keyword:       Optional name of the NodeConnection.
            arg_position:  Argument position. See the context of the 'connect_input_nodes' method.

        Returns:
            (NodeConnection, input keyword)
        """
        if isinstance(node, Node):
            return NodeConnection(node), keyword
        elif isinstance(node, NodeConnection):
            return node, keyword
        if keyword is None:
            err_msg = f"Positional argument in position {arg_position} has incompatible type: {type(node)}"
        else:
            err_msg = f"Argument '{keyword}' has incompatible type: {type(node)}"
        raise TypeError(err_msg)

    @staticmethod
    def __check_node_connections(nodes: Iterable[Tuple[Optional[str], Union[Node, NodeConnection]]]) -> Iterator[
        Tuple[NodeConnection, Optional[str]]
    ]:
        """
        Supplemental method used by the 'connect_input_nodes' method.

        Args:
            nodes:  Iterable of Nodes to connect to or NodeConnections to add.

        Returns:
            Iterator of pairs (NodeConnection, input keyword)
        """
        check_node_connection = DataProcessor.__check_node_connection
        for i, (keyword, node) in enumerate(nodes):
            yield check_node_connection(node, keyword, i)

    @final
    def connect_input_node(self,
                           node_connection: Union[Node, NodeConnection],
                           keyword: Optional[str] = None) -> None:
        """
        Connects input Node.

        Args:
            node_connection:  Node to connect to or NodeConnection to add.
            keyword:          Optional name of the NodeConnection.
        """
        args = DataProcessor.__check_node_connection(node_connection, keyword)
        self.drop_cache()
        self.__connect_input_node_body(*args)

    @final
    def connect_input_nodes(self,
                            *positional_nodes: Union[Node, NodeConnection],
                            **keyword_nodes: Union[Node, NodeConnection]) -> None:
        """
        Connects multiple input Nodes.

        Args:
            positional_nodes:  positional Nodes to connect or NodeConnections to add.
            keyword_nodes:     named Nodes to connect or NodeConnections to add.
        """
        if positional_nodes or keyword_nodes:
            nodes = tuple(
                DataProcessor.__check_node_connections(
                    chain(
                        zip(repeat(None), positional_nodes),
                        keyword_nodes.items()
                    )
                )
            )
            self.drop_cache()
            for args in nodes:
                self.__connect_input_node_body(*args)

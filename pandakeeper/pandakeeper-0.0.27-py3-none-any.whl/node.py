from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Dict, Set
from warnings import warn

import pandas as pd
from pandera import DataFrameSchema
from typing_extensions import final
from varutils.typing import check_type_compatibility

from pandakeeper.errors import LoopedGraphError

__all__ = ('Node',)


class Node(metaclass=ABCMeta):
    """Abstract class that defines an interface common to all data manipulators."""

    __slots__ = ('__gateway_id', '__already_cached', '__output_validator')
    __instance_counter = 0
    __parental_graph: Dict['Node', Set['Node']] = defaultdict(set)
    __children_graph: Dict['Node', Set['Node']] = defaultdict(set)

    def __init__(self, output_validator: DataFrameSchema) -> None:
        """
        Abstract class that defines an interface common to all data manipulators.

        Args:
            output_validator: DataFrameSchema that validates the data coming from the 'extract_data' method.
        """
        check_type_compatibility(output_validator, DataFrameSchema)
        self.__gateway_id = Node.__instance_counter
        Node.__instance_counter += 1
        self.__already_cached = False
        self.__output_validator = output_validator

    @final
    def __hash__(self) -> int:
        return self.__gateway_id

    @final
    @property
    def _output_validator(self) -> DataFrameSchema:
        """
        Returns output validator.

        Returns:
            pandera.DataFrameSchema that validates the result of the 'transform_data' method.
        """
        return self.__output_validator

    @final
    @property
    def _is_parental_graph_topo_sorted(self) -> bool:
        """
        Checks whether parental graph is topologically sorted.

        Returns:
            Result of checking.
        """
        connection_graph = Node.__parental_graph

        visited_nodes = {self}
        nodes_to_visit = connection_graph[self].copy()
        try:
            while True:
                cur_node = nodes_to_visit.pop()
                if cur_node in visited_nodes:
                    return False
                visited_nodes.add(cur_node)
                nodes_to_visit |= connection_graph[cur_node]
        except KeyError:
            return True

    @final
    def _add_edge_to_connection_graph(self, parent_node: 'Node') -> None:
        """
        Adds directed edge {Self <- Parent} to the connection graph.

        Args:
            parent_node:  parent Node to connect self Node to.
        """
        Node.__parental_graph[self].add(parent_node)
        Node.__children_graph[parent_node].add(self)

    @final
    def _remove_edge_from_connection_graph(self, parent_node: 'Node') -> None:
        """
        Removes directed edge {Self <- Parent} from the connection graph.

        Args:
            parent_node:  parent Node to untie self Node from.
        """
        Node.__parental_graph[self].remove(parent_node)
        Node.__children_graph[parent_node].remove(self)

    @final
    @property
    def already_cached(self) -> bool:
        """Checks whether self is already cached."""
        return self.__already_cached

    @final
    @property
    def gateway_id(self) -> int:
        """Returns unique ID of the Node instance."""
        return self.__gateway_id

    @final
    def __make_node_cached(self) -> None:
        """Supplemental method for the 'make_node_cached' method."""
        data = self._load_non_cached()
        data = self.transform_data(data)
        data = self.__output_validator.validate(data)
        self._dump_to_cache(data)
        self.__already_cached = True

    @final
    def make_node_cached(self) -> None:
        """Caches self and all parent Nodes with True use_cached property."""
        if self.__already_cached:
            return
        if not self._is_parental_graph_topo_sorted:
            node_id = self.__gateway_id
            raise LoopedGraphError(f"Parental graph of Node (ID={node_id}) has loops")
        for parent in Node.__parental_graph[self]:
            if parent.use_cached and not parent.__already_cached:
                parent.__make_node_cached()
        if not self.use_cached:
            node_id = self.__gateway_id
            warn(f"'make_node_cached' called for Node (ID={node_id}) with False 'use_cached' property", RuntimeWarning)
            return
        self.__make_node_cached()

    @final
    def drop_cache(self) -> None:
        """Drops the Node's cache, dropping it in all child Nodes as well."""
        if self.__already_cached:
            self._clear_cache_storage()
            self.__already_cached = False

        children_graph = Node.__children_graph
        visited_nodes = {self}
        nodes_to_visit = children_graph[self].copy()
        try:
            while True:
                cur_node = nodes_to_visit.pop()
                if cur_node in visited_nodes:
                    node_id = cur_node.__gateway_id
                    raise LoopedGraphError(f"Node with ID={node_id} is child of itself")
                if cur_node.__already_cached:
                    cur_node._clear_cache_storage()
                    cur_node.__already_cached = False
                visited_nodes.add(cur_node)
                nodes_to_visit |= children_graph[cur_node]
        except KeyError:
            pass

    @final
    def extract_data(self) -> pd.DataFrame:
        """
        Extracts data from the Node.

        Returns:
            Extracted DataFrame.
        """
        if self.__already_cached:
            data = self._load_cached()
            return self.__output_validator.validate(data)
        if not self._is_parental_graph_topo_sorted:
            node_id = self.__gateway_id
            raise LoopedGraphError(f"Parental graph of Node (ID={node_id}) has loops")
        data = self._load_non_cached()
        data = self.transform_data(data)
        data = self.__output_validator.validate(data)
        if self.use_cached:
            self._dump_to_cache(data)
            self.__already_cached = True
        return data

    @final
    def set_output_validator(self, output_validator: DataFrameSchema) -> 'Node':
        """
        Sets the output validator.

        Args:
            output_validator: output validator to set.
        Returns:
            Self instance.
        """
        check_type_compatibility(output_validator, DataFrameSchema)
        self.__output_validator = output_validator
        return self

    @abstractmethod
    def _dump_to_cache(self, data: pd.DataFrame) -> None:
        """
        Defines the last logical step of the 'extract_data' method. Dumps extracted data to cache.

        Args:
            data: DataFrame to dump.
        """

    @abstractmethod
    def _clear_cache_storage(self) -> None:
        """Clears cache storage. Must be the inverse of '_dump_to_cache'. Used by the 'drop_cache' method."""

    @abstractmethod
    def _load_cached(self) -> pd.DataFrame:
        """
        Loads data previously dumped by '_dump_to_cache' method.

        Returns:
            Loaded data.
        """

    @abstractmethod
    def _load_non_cached(self) -> pd.DataFrame:
        """
        Loads raw input data. Used by the 'extract_data' as the first logical step if not self.already_cached.

        Returns:
            Loaded data.
        """

    @property
    @abstractmethod
    def use_cached(self) -> bool:
        """Whether to cache the result of the 'extract_data' method or run it from scratch each time."""

    @abstractmethod
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Applies transformations to the output of the '_load_non_cached' method. Used by the 'extract_data'
        as the last logical step before sending the data to the output validator for validation.

        Args:
            data: the output of the '_load_non_cached' method.
        Returns:
            Transformed output, ready to be validated by the output validator.
        """

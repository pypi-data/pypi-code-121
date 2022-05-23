from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_prefix import PrefixedColumn
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.table.base_source_table import SourceTable
from lumipy.query.expression.column.collection import CollectionExpression
from lumipy.query.expression.column.column_literal import LiteralColumn
from typing import List
from lumipy.common.string_utils import indent_str


class AliasedTable(SourceTable):
    """Class representing an alias applied to a source table.

    """

    def __init__(self, original: SourceTable, alias: str):
        """__init__ method of the AliasedTable class.

        Args:
            original (SourceTable): the source table to be aliased.
            alias (str): the alias value to apply.
        """
        self._original = original
        self._alias = alias

        # Prefix member columns with the alias
        columns = [PrefixedColumn(c, self._alias) for c in original.get_columns()]
        params = {f"{k}_{alias}": v.with_prefix(alias) for k, v in original.get_parameters().items()}

        # noinspection PyTypeChecker
        super().__init__(
            f"{original.get_from_arg_string()} AS {alias}",
            columns,
            original.get_client(),
            'aliased',
            params,
            original
        )

    def with_alias(self, alias: str) -> 'AliasedTable':
        raise TypeError("Can't alias an already-aliased table.")

    def get_alias(self):
        """

        Returns:

        """
        return self._alias

    def validate_source_columns(self, columns: List[BaseColumnExpression]) -> List[BaseColumnExpression]:
        """

        Args:
            columns:

        Returns:

        """
        col_list = super().validate_source_columns(columns)

        def process(col):
            if isinstance(col, PrefixedColumn) or isinstance(col, SourceColumn):
                return self.get_prefixed_col(col)
            else:
                return self.apply_prefix(col)

        p_col_list = [process(c) for c in col_list]
        return p_col_list

    def get_prefixed_col(self, col):

        """

        Args:
            col:

        Returns:

        """
        if not isinstance(col, SourceColumn) and not isinstance(col, PrefixedColumn):
            raise TypeError(f"Must supply either a source column instance or a prefixed column instance.")

        if isinstance(col, PrefixedColumn) and col.get_prefix() != self._alias:
            raise ValueError(
                f"Incompatible column: prefix doesn't match table alias: {col.get_prefix()} vs {self._alias}."
            )
        elif isinstance(col, PrefixedColumn):
            return col

        for p_col in self.get_columns():
            if p_col.get_without_prefix().hash_equals(col):
                return p_col

        return col

    def get_original(self) -> SourceTable:
        """Get the original non-aliased source table.

        Returns:
            SourceTable: the original source table.
        """
        return self._original

    def contains_column(self, column: BaseColumnExpression) -> bool:

        if isinstance(column, PrefixedColumn) and column.get_prefix() != self._alias:
            return False
        elif isinstance(column, PrefixedColumn):
            return super().contains_column(column)
        elif isinstance(column, SourceColumn):
            return any([c.get_without_prefix().hash_equals(column) for c in self.get_columns()])
        else:
            return False

    @staticmethod
    def _find_leaf_nodes(decomposition):
        # Find leaf nodes (source columns, literals, collections)
        leaves = {}
        types = [SourceColumn, LiteralColumn, CollectionExpression, PrefixedColumn]
        for node in decomposition.keys():
            if any(isinstance(node, t) for t in types):
                leaves[hash(node)] = node
        return leaves

    def _apply_prefixing_to_leaf_nodes(self, leaves):
        prefix_map = {}
        constructed = {}
        for hash_val, node in leaves.items():
            if isinstance(node, SourceColumn) and self.contains_column(node):
                prefixed = self.get_prefixed_col(node)
                constructed[hash(prefixed)] = prefixed
                prefix_map[hash(node)] = hash(prefixed)
            elif isinstance(node, PrefixedColumn):
                # todo: remove this bit
                constructed[hash(node)] = node
                prefix_map[hash(node.get_without_prefix())] = hash(node)
            else:
                constructed[hash(node)] = node
        return prefix_map, constructed

    def apply_prefix(self, expression):
        """Apply prefixes to source columns in a column expression. If the column belongs to this table it will be
        prefixed with the table alias otherwise it will be left alone.

        Args:
            expression (BaseColumnExpression): input expression

        Returns:
            BaseColumnExpression: expression with preixes applied
        """
        if isinstance(expression, PrefixedColumn) or isinstance(expression, LiteralColumn):
            # No effect on literals and already-prefixed columns
            return expression
        elif isinstance(expression, SourceColumn):
            # trivial case, prefixing a single source column
            return self.get_prefixed_col(expression)

        # Decompose expression into individual nodes
        decomposition = expression.get_decomposition()

        # Find the leaf nodes - nodes that do not depend on source columns
        leaves = self._find_leaf_nodes(decomposition)

        # Add prefix expression to source cols that belong to this aliased table and make a dictionary
        # mapping between source col hashes and prefixed source col hashes
        prefix_map, constructed = self._apply_prefixing_to_leaf_nodes(leaves)

        # Iteratively loop over the decomposed expression and look for nodes to construct whose parents exist
        # (found by comparing hashes) if the input node has been prefixed swap in the prefixed version.
        while True:

            n_built = len(constructed)
            for node, input_hashes in decomposition.items():

                # Already built, so we can move on to next
                if hash(node) in constructed.keys():
                    continue

                # Swap any unprefixed hashes for prefixed hashes
                target_hashes = [
                    prefix_map[h] if h in prefix_map.keys()
                    else h
                    for h in input_hashes
                ]

                # If all the input hashes for a node are in the constructed dict then we can make the next bit of the
                # expression DAG
                if all(h in constructed.keys() for h in target_hashes):
                    input_nodes = [constructed[h] for h in target_hashes]
                    try:
                        built_node = type(node)(*input_nodes)
                    except TypeError:
                        raise TypeError(
                            "Prefixing failed at expression reconstruction:"
                            f"\n  Class = {type(node).__name__}"
                            f"\n  Inputs = {','.join(type(i).__name__ for i in input_nodes)}"
                        )

                    constructed[hash(built_node)] = built_node

                    # if node has changed hash because of prefixing of its ancestors add to prefix map so later nodes
                    # can find and use it
                    if not node.hash_equals(built_node):
                        prefix_map[hash(node)] = hash(built_node)

                    # If the node we're looking at is equivalent to the expression (equal hash) and its replacement is
                    # built successfully then we've finished!
                    if node.hash_equals(expression):
                        return built_node

            # If the size of the constructed nodes dictionary does not change each iteration then the process has failed
            # Every iteration should be able to match a new node to it's parents (or substitute ones) and build it.
            # This indicates that there is a hash missmatch or a node is missing. Error with detailed information on
            # the state of the expression reconstruction will be thrown...
            # This can happen if there's a new expression type that's been introduced that constructs an intermediate
            # node in its constructor that's not added to its lineage. This method then can't find it and will fail.
            if n_built == len(constructed):
                repr_constructed = "\n".join(repr(c) for c in constructed.values())
                raise ValueError(
                    f'Prefixing failed during expression recomposition! There is a missing piece somewhere.\n'
                    f'Pieces:\n{indent_str(repr_constructed)}\n\n\n'
                    f'Target:\n{indent_str(repr(expression))}'
                )

    def __hash__(self):
        return hash(self._alias) + super().__hash__()

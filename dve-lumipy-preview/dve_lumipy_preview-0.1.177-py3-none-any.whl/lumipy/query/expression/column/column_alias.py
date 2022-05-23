from lumipy.common.string_utils import sql_str_to_name
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import LiteralColumn, python_to_expression
from typing import Dict, Union, NoReturn


# noinspection PyArgumentList
class AliasedColumn(BaseColumnExpression):
    """Column expression class that represents the operation of aliasing a column or function of column(s).

    """

    def __init__(self, column: BaseColumnExpression, alias: Union[str, LiteralColumn]):
        """__init__ method for AliasedColumn class.

        Args:
            column (BaseColumnExpression): column/function of columns to be aliased.
            alias (str): the name the column/function of columns is to be aliased as.
        """
        if isinstance(column, AliasedColumn):
            raise TypeError(
                f"Can't alias a a column that's already aliased:\n{column.get_sql()}."
            )
        if not issubclass(type(column), BaseColumnExpression):
            raise TypeError(
                f"Object to apply column alias to must inherit from BaseColumnExpression. Was {type(column).__name__}"
            )
        if not isinstance(alias, str) and not isinstance(alias, LiteralColumn):
            raise TypeError(
                f"Alias must be a non-empty string. Was a {type(alias).__name__}, value: {alias}."
            )

        alias_expr = python_to_expression(alias)
        self._alias = alias_expr.get_py_value()
        self._original = column
        super().__init__(
            column.source_table_hash(),
            lambda x, y: f"{x.get_sql()} AS [{y.get_py_value()}]",
            lambda x, y: True,
            lambda x, y: x,
            'alias',
            column,
            alias_expr
        )

    def get_name(self) -> str:
        """Get the pythonic name of this column

        Returns:
            str: the python name of the column
        """
        return sql_str_to_name(self._alias)

    def is_main(self) -> bool:
        """Get whether this column is a main column or not (whether it'll be selected by 'select ^')

        Returns:
            bool: whether the column is main.
        """
        from .column_prefix import PrefixedColumn
        from .source_column import SourceColumn
        if isinstance(self._original, SourceColumn) or isinstance(self._original, PrefixedColumn):
            return self._original.is_main()

        return False

    def get_alias(self) -> str:
        """Get the alias string

        Returns:
            str: the alias
        """
        return self._alias

    def get_original(self) -> BaseColumnExpression:
        """Get the original column expression

        Returns:
            BaseColumnExpression: the original column expression
        """
        return self._original

    def with_alias(self, alias: str) -> NoReturn:
        """Apply an alias to this column.

        Using this method on an aliased column will throw an exception.

        Args:
            alias (str): the alias to apply.

        """
        raise TypeError(f"Can't alias a column that's already aliased: \n{self.get_sql()}.")

    def __hash__(self):
        # Hash must be the same as the non-prefixed column for expression
        # decomposition, prefixing, and reconstruction to work.
        return hash(self._alias) + hash(self._original) + hash('alias')

    # noinspection PyUnresolvedReferences
    def as_col_on_new_table(self, new_table_name: str, new_table_hash: int) -> 'SourceColumn':
        """Converts this aliased column to a new source column that belongs to a table variable.

        Args:
            new_table_name (str): name of the new table.
            new_table_hash (int): hash value of the new table.

        Returns:
            SourceColumn: the new source column.
        """

        from lumipy.atlas.field_metadata import FieldMetadata
        from lumipy.query.expression.column.source_column import SourceColumn

        new_field_description = FieldMetadata(
            field_name=self.get_alias(),
            field_type='Column',
            table_name=new_table_name,
            data_type=self.get_type(),
            description=f"Alias of {self.get_sql()}",
            is_main=self.is_main(),
            is_primary_key=False,  # todo: implement in base. This is missing.
            param_default_value=None,
            table_param_columns=None
        )
        return SourceColumn(new_field_description, new_table_hash, with_brackets=True)

    # noinspection PyUnresolvedReferences
    def ascending(self) -> 'AscendingOrder':
        """Apply an ascending ordering expression to this column

        Returns:
            AscendingOrder: AscendingOrder instance representing the column ordering.
        """
        # Ordering expects the original SQL piece as an arg
        return self.get_original().ascending()

    # noinspection PyUnresolvedReferences
    def descending(self) -> 'DescendingOrder':
        """Apply a descending ordering expression to this column

        Returns:
            DescendingOrder: DescendingOrder instance representing the column ordering.
        """
        # Ordering expects the original SQL piece as an arg
        return self.get_original().descending()

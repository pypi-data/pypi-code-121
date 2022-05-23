from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.atlas.field_metadata import FieldMetadata


class PrefixedColumn(BaseColumnExpression):
    """Expression representing the addition of a prefix to a source column.

    For example ('LHS', [ExampleCol]) -> LHS.[ExampleCol].

    """

    def __init__(self, column: SourceColumn, prefix: str):
        """__init__ method of the PrefixedColumn class.

        Args:
            column (SourceColumn): source column expression to prefix.
            prefix (str): prefix string to use.
        """

        if type(prefix) != str:
            raise TypeError(f"Prefix value must be a str. Was {type(prefix).__name__}.")
        if type(column) != SourceColumn:
            raise TypeError(f"Can only prefix SourceColumn types. Was {type(column).__name__}.")

        self._prefix = prefix
        self._original = column
        super().__init__(
            column.source_table_hash(),
            lambda x: f"{prefix}.{x.get_sql()}",
            lambda x: True,
            lambda x: x,
            'prefix',
            column
        )

    def __hash__(self):
        return hash(hash(self._prefix) + hash(self._original))

    def get_name(self) -> str:
        """Get the pythonic name of this column

        Returns:
            str: the python name of the column
        """
        return self._original.get_name()

    def is_main(self) -> bool:
        """Get whether this column is a main column or not (whether it'll be selected by 'select ^')

        Returns:
            bool: whether the column is main.
        """
        return self._original.is_main()

    def get_prefix(self) -> str:
        """Get prefix string this expression adds.

        Returns:
            str: the prefix string
        """
        return self._prefix

    def get_without_prefix(self):
        """Get the original source column expression.

        Returns:
            SourceColumn: the original un-prefixed column.
        """
        return self._original

    def as_col_on_new_table(self, new_table_name, new_table_hash):
        """Converts this prefixed column to a new source column that belongs to a table variable.

        Args:
            new_table_name (str): name of the new table.
            new_table_hash (int): hash value of the new table.

        Returns:
            SourceColumn: the new source column.
        """

        new_field_description = FieldMetadata(
            field_name=self._original.get_sql(),
            field_type='Column',
            table_name=new_table_name,
            data_type=self._original.get_type(),
            description=self._original.get_definition().description,
            is_main=self._original.is_main(),
            is_primary_key=False,
            param_default_value=None,
            table_param_columns=None
        )
        return SourceColumn(new_field_description, new_table_hash)

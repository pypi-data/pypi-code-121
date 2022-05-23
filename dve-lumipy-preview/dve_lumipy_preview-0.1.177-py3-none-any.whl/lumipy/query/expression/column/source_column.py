from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.atlas.field_metadata import FieldMetadata


class SourceColumn(BaseColumnExpression):
    """Expression representing an original column on a source table: i.e. a column that it not derived from
    other columns in the table.

    """

    def __init__(
            self,
            field_definition: FieldMetadata,
            source_table_hash: int,
            with_brackets: bool = False
    ):
        """__init__ method of the SourceColumn class.

        Args:
            field_definition (FieldMetadata): field definition instance to build the source column from.
            source_table_hash (int): hash of the source table that this column will belong to.
            with_brackets (bool): whether to wrap the column's sql piece string in squre brackets.
        """
        def with_brackets_fn(x):
            return f"[{x.field_name}]"

        def without_brackets_fn(x):
            return x.field_name

        self._definition = field_definition

        super().__init__(
            source_table_hash,
            with_brackets_fn if with_brackets else without_brackets_fn,
            lambda x: True,
            lambda x: x,
            'column input',
            field_definition
        )

    def get_name(self) -> str:
        """Get the pythonic name of this column

        Returns:
            str: the python name of the column
        """
        return self._definition.name

    def get_sql_name(self) -> str:
        return self._definition.field_name

    def is_main(self):
        """Get whether this column is a main column or not (whether it'll be selected by 'select ^')

        Returns:
            bool: whether the column is main.
        """
        return self._definition.is_main

    def get_definition(self) -> FieldMetadata:
        """Get the underlying FieldMetadata object that defines this column.

        Returns:
            FieldMetadata: the underlying field metadata object.
        """
        return self._definition

    def as_col_on_new_table(self, new_table_name, new_table_hash):
        """Converts this column to a new source column that belongs to a table variable.

        Args:
            new_table_name (str): name of the new table.
            new_table_hash (int): hash value of the new table.

        Returns:
            SourceColumn: the new source column.
        """

        new_field_description = FieldMetadata(
            field_name=self.get_sql(),
            field_type='Column',
            table_name=new_table_name,
            data_type=self.get_type(),
            description=self._definition.description,
            is_main=self.is_main(),
            is_primary_key=self._definition.is_primary_key,
            param_default_value=self._definition.param_default_value,
            table_param_columns=self._definition.table_param_columns
        )
        return SourceColumn(new_field_description, new_table_hash)

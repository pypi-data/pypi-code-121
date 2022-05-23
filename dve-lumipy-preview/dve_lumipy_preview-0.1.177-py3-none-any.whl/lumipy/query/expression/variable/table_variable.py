from lumipy.query.expression.table.base_source_table import SourceTable
from lumipy.query.expression.variable.base_variable import BaseVariable
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression


class TableVariable(BaseVariable, SourceTable):
    """Class that represents a Luminesce table variable (@variable). This is an inheritor of BaseSourceTable and
    therefore behaves like a data source.

    """

    def __init__(self, var_name: str, table: BaseTableExpression):
        """__init__ method of the TableVariable class.

        Args:
            var_name: name of the table variable. Must not conflict with any SQL keywords.
            table: the table expression that this table variable is to be built from.
        """
        # Check var_name is a legal string
        # Check table is a SelectableTable subclass
        BaseVariable.__init__(
            self,
            '@',
            var_name,
            table.get_table_sql(),
        )

        # Reassign alias columns, column table names, remove prefixes
        new_table_name = f'@{var_name}'
        processed_columns = [
            c.as_col_on_new_table(
                new_table_name,
                hash(self.get_assignment_sql())
            )
            for c in table.get_columns()
        ]
        SourceTable.__init__(
            self,
            new_table_name,
            processed_columns,
            table.get_client(),
            'variable',
            {},
            table
        )

    def __hash__(self):
        return BaseVariable.__hash__(self)

from typing import List, Dict, Union
from typing import TYPE_CHECKING

from lumipy.client import Client
from lumipy.query.expression.base_expression import BaseExpression
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import python_to_expression
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.table.base_table import BaseTable
from lumipy.query.expression.table.table_parameter_assignment import ParameterAssignment
from lumipy.query.expression.variable.scalar_variable import ScalarVariable

if TYPE_CHECKING:
    from ..table_op.select_op import SelectTableExpression


class SourceTable(BaseTable):
    """Base class for tables that act as sources of data (data providers, joins, and table variables) that you can use
    with the select SQL keyword.

    """

    def __init__(
            self,
            from_arg_string: str,
            columns: List[SourceColumn],
            client: Client,
            table_op_name: str,
            param_assignments: Dict[str, ParameterAssignment],
            *values: BaseExpression
    ):
        """__init__ method for the base source table class.

        Args:
            from_arg_string (str): the SQL string that's the argument to the 'from' keyword. Can be a table name or
            subquery.
            columns (List[SourceColumn]): list of source column expressions that define the table's content.
            client (Client): web client for access to Luiminesce's web api.
            table_op_name (str): name labelling the table expression.
            param_assignments (Dict[str, ParameterAssignment]): dictionary of parameter names and their assignments.
            *values (BaseExpression): parent values of the source table. Will usually just be a provider definition, but
            will be two source tables in the case of a join table object.
        """

        self._from_arg_string = from_arg_string
        self._param_assignments = param_assignments
        super().__init__(
            columns,
            client,
            table_op_name,
            *values
        )

    def get_parameters(self) -> Dict[str, ParameterAssignment]:
        """Get the parameter assignments of the table.

        Returns:
            Dict[str, ParameterAssignment]: dict of param names and assignment expressions.
        """
        return self._param_assignments

    def get_from_arg_string(self) -> str:
        """Get the argument to the from keyword for this table

        Returns:
            str: value of the argument.
        """
        return self._from_arg_string

    def handle_star_or_caret(self, columns: Union[List[SourceColumn], List[str]]) -> List[SourceColumn]:
        """Handle cases when the select input args is ['*'] or ['^']. This gets all the columns, or all the main columns and
        returns them as a list. If it's a list of column objects they will pass through as a no-op.

        Args:
            columns: the args tuple given to a select statement.

        Returns:
            List[SourceColumns]: the corresponding list of column objects.
        """

        if len(columns) == 1 and isinstance(columns[0], str) and columns[0] == '*':
            return self.get_columns()
        elif len(columns) == 1 and isinstance(columns[0], str) and columns[0] == '^':
            in_columns = [c for c in self.get_columns() if c.is_main()]
            if len(in_columns) == 0:
                return self.get_columns()
            else:
                return in_columns
        else:
            return columns

    def _error_on_incompatible_column_expression(self, column: BaseColumnExpression):
        """Check whether a column expression and its dependencies belong to the table.
            Raise ValueError if the check fails.
        Args:
            column (BaseColumnExpression): column expression to validate

        Raises:
            ValueError: if a column or it's dependencies are not members of the table.
        """

        if self.contains_column(column) or isinstance(column, ScalarVariable):
            pass
        elif type(column) == SourceColumn:
            raise ValueError(
                f"Column {column.get_name()}/{column.get_sql()} "
                f"is not a member of the table."
            )
        else:
            for col_dep in column.get_col_dependencies():
                if not self.contains_column(col_dep):
                    table_name = type(self).__name__
                    raise ValueError(
                        f"Column {col_dep.get_name()}/{col_dep.get_sql()} "
                        f"is not a member of the table ({table_name})."
                    )

    def validate_source_columns(self, columns: List[BaseColumnExpression]) -> List[BaseColumnExpression]:
        """Validate and preprocess columns.

        For each input column, check membership and handle cases such as python
        primitives -> LiteralColumn and the '*' and '^' inputs -> column object lists.

        Args:
            columns (List[BaseColumnExpression, Union[str, int, bool, float, date, datetime]]): list of column inputs.

        Returns:
            List[BaseColumnExpression]: list of validated and processed columns.
        """
        in_columns = [python_to_expression(c) for c in columns]
        for col in in_columns:
            # Check col and its dependencies are in the table
            self._error_on_incompatible_column_expression(col)

        return in_columns

    def select(self, *columns: Union[str, BaseColumnExpression], **aliased_cols: BaseColumnExpression) -> 'SelectTableExpression':
        """Apply a select expression to this source table object.

        The select SQL statement is used to select a set of columns from a table of data. These can be columns
        that belong to the table; functions of columns that belong to the table; or literals such as 3.14,
        #09-07-1989# or 'my_string'.

        Args:
            *columns (BaseColumnExpression): column expressions to use as arguments to the select statement.
            **aliased_cols (BaseColumnExpression): aliased column expressions to use as arguments. The keyword is
            the alias and the value is the column expression to be aliased.

        Returns:
            SelectTableExpression: instance of SelectTableExpression representing the select expression applied to the
            source table.
        """

        from ..table_op.select_op import SelectTableExpression
        return SelectTableExpression(
            self,
            False,
            *columns,
            **aliased_cols
        )

    def select_distinct(self, *columns: BaseColumnExpression, **aliased_cols: BaseColumnExpression):
        """Apply a select distinct expression to this source table object.

        The select distinct SQL statement is used to select a unique set of columns from a table of data. These can be
        columns that belong to the table; functions of columns that belong to the table; or literals such as 3.14,
        #09-07-1989# or 'my_string'.

        Args:
            *columns (BaseColumnExpression): column expressions to use as arguments to the select distinct statement.
            **aliased_cols (BaseColumnExpression): aliased column expressions to use as arguments. The keyword is
            the alias and the value is the column expression to be aliased.

        Returns:
            SelectTableExpression: instance of SelectTableExpression representing the select distinct expression applied
            to the source table.
        """

        from ..table_op.select_op import SelectTableExpression
        return SelectTableExpression(
            self,
            True,
            *columns,
            **aliased_cols
        )

    def with_alias(self, alias: str) -> 'AliasedTable':
        """Apply an alias expression to this source table object.

        This method will add a table alias (SQL: '[table] as [alias_value]') and also add the alias as a prefix to all
        of the table's member columns.

        Args:
            alias (str): the alias value to use.

        Returns:
            AliasedTable: instance of AliasedTable class that represents this table with an alias applied.
        """
        from .table_alias import AliasedTable
        return AliasedTable(self, alias)

    def inner_join(
            self,
            other: 'SourceTable',
            on: BaseColumnExpression,
            left_alias: str = 'lhs',
            right_alias: str = 'rhs'
    ):
        """Build an inner join expression between this table and another.

        Args:
            other (SourceTable): other table to join on.
            on (BaseColumnExpression): the condition to join on.
            left_alias (str, optional): the alias of the left table. Defaults to 'lhs'.
            right_alias (str, optional): the alias of the right table. Defaults to 'rhs'.

        Returns:
            JoinSourceTable: Join source table representing the result of the inner join.
        """
        from .join_table import JoinSourceTable
        return JoinSourceTable(
            join_op_name='inner',
            left_table=self,
            right_table=other,
            on=on,
            left_alias=left_alias,
            right_alias=right_alias
        )

    def left_join(self, other, on, left_alias='lhs', right_alias='rhs'):
        """Build an left join expression between this table and another.

        Args:
            other (SourceTable): other table to join on.
            on (BaseColumnExpression): the condition to join on.
            left_alias (str, optional): the alias of the left table. Defaults to 'lhs'.
            right_alias (str, optional): the alias of the right table. Defaults to 'rhs'.

        Returns:
            JoinSourceTable: Join source table representing the result of the left join.
        """
        from .join_table import JoinSourceTable
        return JoinSourceTable(
            join_op_name='left',
            left_table=self,
            right_table=other,
            on=on,
            left_alias=left_alias,
            right_alias=right_alias
        )

    def cross_join(self, other, on, left_alias='lhs', right_alias='rhs'):
        """Build an cross join expression between this table and another.

        Args:
            other (SourceTable): other table to join on.
            on (BaseColumnExpression): the condition to join on.
            left_alias (str, optional): the alias of the left table. Defaults to 'lhs'.
            right_alias (str, optional): the alias of the right table. Defaults to 'rhs'.

        Returns:
            JoinSourceTable: Join source table representing the result of the cross join.
        """
        from .join_table import JoinSourceTable
        return JoinSourceTable(
            join_op_name='cross',
            left_table=self,
            right_table=other,
            on=on,
            left_alias=left_alias,
            right_alias=right_alias
        )

    def when(self, condition: BaseColumnExpression):
        """Start to build up a case expression consisting on 'when', 'then' and 'otherwise' (else) clauses.

        Case expressions are build via a chain of alternating .when() and .then() calls that end with an .otherwise()
        call.

        Args:
            condition (BaseColumnExpression): the first when condition of the case expression.

        Returns:
            When: the When object representing the first WHEN condition. Call .then() to chain the THEN value that
            follows.
        """
        from ..case.case import CaseStart
        return CaseStart(hash(self)).when(condition)


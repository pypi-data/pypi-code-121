from typing import List

from lumipy.query.expression.base_expression import BaseExpression
from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.column.column_literal import LiteralColumn, python_to_expression
from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.variable.scalar_variable import ScalarVariable


class CollectionExpression(BaseSqlExpression):
    """Expression class that represents a collection to test membership of. This can be a
    subquery or a list of literals

    """

    def __init__(self, *values):
        """__init__ method of the CollectionExpression class

        Args:
            *values: collection of python primitives, literal column expression objects, or scalar variable expression
            objects. Defines the members of the collection.
        """

        def element_type_check(el):
            return (not issubclass(type(el), BaseExpression)) \
                   or isinstance(el, ScalarVariable) \
                   or isinstance(el, LiteralColumn)

        def seq_sql_str_fn(*args):
            return f"({', '.join(a.get_sql() for a in args)})"

        def subqry_sql_str_fn(x):
            return f"({x.get_table_sql()})"

        # Convert iterable of literals/scalar vars or TableOp subquery with single column
        if len(values) == 1 and issubclass(type(values[0]), BaseTableExpression):

            n_cols = len(values[0].get_columns())
            if n_cols != 1:
                raise ValueError(f"In subquery arg must only have a single column. Has {n_cols}")

            in_vals = [values[0]]
            sql_str_fn = subqry_sql_str_fn

        elif all(element_type_check(v) for v in values):
            in_vals = [python_to_expression(v) for v in values]
            sql_str_fn = seq_sql_str_fn

        else:
            types_str = ", ".join(type(v).__name__ for v in values)
            raise TypeError(
                f"Invalid types for IN/NOT IN: {types_str}.\n" +
                "Must be sequence of literals/scalar vars as *args or a table subquery with a single column. "
            )

        super().__init__(
            'membership',
            sql_str_fn,
            lambda *x: True,
            lambda *x: SqlValType.Boolean,
            *in_vals
        )

    def get_col_dependencies(self) -> List['SourceColumn']:

        parents = self.get_lineage()
        if len(parents) == 1 and issubclass(type(parents[0]), BaseTableExpression):
            # Block source cols from subquery as these don't need to be checked
            return list()
        else:
            return super().get_col_dependencies()

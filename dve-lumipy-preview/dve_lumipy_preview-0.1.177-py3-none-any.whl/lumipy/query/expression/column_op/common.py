from functools import reduce

from lumipy.query.expression.column.column_literal import LiteralColumn
from lumipy.query.expression.column.column_prefix import PrefixedColumn
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.window.function import BaseWindowFunction


def get_expr_sql(x):
    if issubclass(type(x), BaseScalarOp):
        return f"({x.get_sql()})"
    else:
        return x.get_sql()


def derive_table_hash(in_values):
    # Get source table hashes so this expression can be distingished from one from another table but with
    # identical column names.
    table_sources = []
    for v in in_values:
        v_type = type(v)
        if v_type == SourceColumn or v_type == PrefixedColumn or v_type == LiteralColumn:
            # noinspection PyArgumentList
            table_sources.append(v.source_table_hash())
        elif issubclass(v_type, (BaseScalarOp, BaseAggregateColumn, BaseWindowFunction)):
            # noinspection PyArgumentList
            for col in v.get_col_dependencies():
                table_sources.append(col.source_table_hash())

    return reduce(lambda x, y: x ^ y, set(table_sources))
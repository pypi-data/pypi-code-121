from functools import reduce
from lumipy.query.expression.table_op.row_set_op import RowSetOp
from lumipy.query.expression.direct_provider.literal import TableLiteral
from pandas import DataFrame
from typing import List, Union, Tuple, Optional
from numpy import ndarray


"""
Utility functions for constructing queries that augment the fluent syntax. 
"""


def concat(sub_qrys, filter_duplicates=True) -> RowSetOp:
    """Vertical concatenation of subqueries. This is the lumipy equivalent of pandas.concat()

    Args:
        sub_qrys: iterable collection of subquery objects to be unioned together.
        filter_duplicates: whether to remove duplicate rows.

    Returns:
        RowSetOp: object representing the union of all the subqueries.
    """
    if filter_duplicates:
        return reduce(lambda x, y: x.union(y), sub_qrys)
    else:
        return reduce(lambda x, y: x.union_all(y), sub_qrys)


def from_array(values: Union[List, Tuple, ndarray], columns: Optional[List[str]] = None) -> TableLiteral:
    """Build a table literal object from an array of values. Must be a numpy ndarray or
    convertible to one and contain int, str, float or datetime values. The array must be either
    one or two dimensional.

    Args:
        values (Union[List, Tuple, ndarray]): the values to populate the table with.
        columns (Optional[List[str]]): optional list of column names.

    Returns:
        TableLiteral: table literal object that can be used as a table variable.
    """
    return TableLiteral(values, columns=columns)


def from_pandas(df: DataFrame) -> TableLiteral:
    """Build a table literal object from a pandas dataframe.

    Args:
        df (DataFrame): the pandas dataframe to express as a table literal.

    Returns:
        TableLiteral: table literal object that can be used as a table variable.
    """
    return TableLiteral(df.values, df.columns.tolist())

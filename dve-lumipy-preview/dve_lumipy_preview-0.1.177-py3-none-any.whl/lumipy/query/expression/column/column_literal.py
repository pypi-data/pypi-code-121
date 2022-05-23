from decimal import Decimal

from lumipy.query.expression.base_expression import BaseExpression
from datetime import datetime, date
from .column_base import BaseColumnExpression
from lumipy.common.string_utils import sql_str_to_name
from typing import Union

from lumipy.atlas.field_metadata import FieldMetadata
from ..sql_value_type import py_type_to_lumi_data_type
import numpy as np


def python_to_expression(
        value: Union[int, Decimal, float, str, datetime, date, bool, BaseExpression]
) -> Union[BaseExpression, BaseColumnExpression]:
    """Convert a python primitive to LiteralColumn if the input value is a python primitive, else pass expression
    through.

    Args:
        value (Union[int, Decimal, float, str, datetime, date, bool, List, BaseColumnExpression]): input value to
        (possibly) convert to LiteralColumn.

    Returns:
        Union[BaseExpression, BaseColumnExpression]: either the original column expression or the literal as LiteralColumn.
    """
    if not issubclass(type(value), BaseExpression):
        return LiteralColumn(value)
    else:
        return value


def _real_num_str(val):
    # Avoid scientific notation and lots of trailing zeros
    val_str = f"{val:1.15f}".rstrip('0')
    if val_str.endswith('.'):
        val_str += '0'
    return val_str


def primitive_to_str(x: Union[str, int, float, Decimal, datetime, date, list, bool]):
    """Convert a python primitive value to its SQL string counterpart.
    This handles extra chars that might need adding for the syntax such as '' around string literals
    or ## around datetime literals.

    Args:
        x (Union[str, int, float, Decimal, datetime, date, list, bool]): input python primitive value

    Returns:
        str: SQL string piece counterpart.
    """

    if isinstance(x, str):
        return f"'{x}'"
    elif isinstance(x, datetime):
        date_str = x.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"#{date_str}#"
    elif isinstance(x, date):
        date_str = x.strftime('%Y-%m-%d')
        return f"#{date_str}#"
    elif x is None:
        return "null"
    elif isinstance(x, bool) or np.issubdtype(type(x), bool):
        return '1' if x else '0'
    elif np.issubdtype(type(x), np.double):
        return _real_num_str(x)
    elif np.issubdtype(type(x), np.integer):
        return str(x)
    elif isinstance(x, Decimal):
        return _real_num_str(x)
    else:
        raise TypeError(f"Unsupported type when converting value to SQL literal: {type(x).__name__}")


class LiteralColumn(BaseColumnExpression):
    """Column expression that represents literal values in statements such as select (e.g. select 3.14 from table).

    """

    def __init__(self, values: Union[int, Decimal, float, str, datetime, date, bool]):
        """__init__ method for the LiteralColumn class.

        Args:
            values (Union[int, Decimal, float, str, datetime, date, bool]): python literal to convert to
            LiteralColumn.
        """

        type_sig = type(values)
        type_description = f"{type(values).__name__}"

        # Check primitive type is supported
        if type_sig not in py_type_to_lumi_data_type.keys():
            raise ValueError(
                f"Python type [{type_description}] is not supported in assignment expressions."
            )

        # Make a dummy field description
        name = 'const_' + sql_str_to_name(primitive_to_str(values))
        field_description = FieldMetadata(
            field_name=primitive_to_str(values),
            field_type='Column',
            table_name='literal_input',
            data_type=py_type_to_lumi_data_type[type_sig],
            description="literal value",
            is_main=False,
            is_primary_key=False,
            param_default_value=None,
            table_param_columns=None,
            name_override=name
        )

        self._py_value = values
        super().__init__(
            hash(field_description.table_name),
            lambda x: f"{x.field_name}",
            lambda x: True,
            lambda x: x,
            'literal',
            field_description
        )

    def get_py_value(self):
        return self._py_value

    def __hash__(self):
        return hash(self.get_sql())

from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.column.column_literal import python_to_expression, LiteralColumn
from lumipy.query.expression.sql_value_type import SqlValType
from datetime import date, datetime
from typing import Union
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.query.expression.variable.base_variable import BaseVariable


class ParameterAssignment(BaseSqlExpression):
    """Class that represents the assignment of a value to a Luminesce table provider parameter.

    """

    def __init__(
            self,
            field_definition: FieldMetadata,
            value: Union[int, float, bool, date, datetime, LiteralColumn],
            prefix: str = None
    ):
        """__init__ method for the ParameterAssignment expression class.

        Args:
            field_definition (FieldMetadata): field definition that defines this parameter.
            value (Union[int, float, bool, date, datetime, LiteralColumn]): value to assign to the parameter.
            prefix (Union[str, None], optional): prefix to put on the parameter name. None by default.
        """
        def with_prefix(x, y):
            return f"{prefix}.[{x.field_name}] = {y.get_sql()}"

        def without_prefix(x, y):
            return f"[{x.field_name}] = {y.get_sql()}"

        if issubclass(type(value), BaseVariable):
            in_val = value
        else:
            in_val = python_to_expression(value)

        if self._type_validation(in_val, field_definition):
            raise TypeError(
                f'Value assignment for parameter {field_definition.get_name()} was wrong type: ' +
                f"{in_val.get_type().name} vs {field_definition.get_type().name}"
            )

        super().__init__(
            "set param value",
            with_prefix if prefix is not None else without_prefix,
            lambda x, y: True,
            lambda x, y: SqlValType.Parameter,
            field_definition,
            in_val
        )

    @staticmethod
    def _type_validation(in_val, field_definition):
        return in_val.get_type() != field_definition.get_type() \
               and {in_val.get_type(), field_definition.get_type()} != {SqlValType.Date, SqlValType.DateTime} \
               and {in_val.get_type(), field_definition.get_type()} != {SqlValType.Int, SqlValType.Decimal}

    def with_prefix(self, prefix: str) -> 'ParameterAssignment':
        """Apply a prefix to the parameter.

        Args:
            prefix (str): prefix value to apply.

        Returns:
            ParameterAssignment: rebuilt parameter object with the prefix.
        """
        # noinspection PyTypeChecker
        return ParameterAssignment(self._lineage[0], self._lineage[1], prefix)

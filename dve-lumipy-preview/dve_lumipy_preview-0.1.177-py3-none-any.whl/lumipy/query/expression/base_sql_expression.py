from abc import abstractmethod

from termcolor import colored

from lumipy.common.string_utils import indent_str, connector, prettify_tree
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.query.expression.base_expression import BaseExpression
from typing import Callable, Union, NoReturn


class BaseSqlExpression(BaseExpression):
    """Base class for expressions that resolve to a piece of SQL (not just a valid query).

    """

    @abstractmethod
    def __init__(
            self,
            op_name: str,
            sql_str_fn: Callable,
            type_check_fn: Callable,
            return_type_fn: Callable,
            *values: Union['BaseExpression', FieldMetadata]
    ):
        """__init__ method for the BaseSqlExpression class.

        Args:
            op_name (str): name of the operation this class represents.
            sql_str_fn (Callable): function that turns the parent values into a SQL piece string.
            type_check_fn (Callable): function that checks the sql value types of the parents.
            return_type_fn (Callable): function that determines the output sql value type of this expression.
            *values Union[BaseExpression, FieldDefinition]: parent values of the expression.
        """
        if not callable(sql_str_fn):
            raise ValueError("Value supplied to str_fn arg is not a callable.")

        self._sql_str = sql_str_fn(*values)
        if self._sql_str is None:
            raise ValueError(
                "SQL expression string is 'None': an undefined expression has been constructed which "
                "should not be possible."
            )
        super().__init__(op_name, type_check_fn, return_type_fn, *values)

    def get_sql(self) -> str:
        """Get the SQL that this expression resolves to.

        Returns:
            str: SQL expression.
        """
        return self._sql_str

    def print_sql(self) -> NoReturn:
        """Print the SQL that this expression resolves to.

        """
        print(self._sql_str)

    def __str__(self):
        def parent_str(p):
            if issubclass(type(p), BaseExpression):
                return str(p)
            elif isinstance(p, FieldMetadata):
                return f"{p.table_name}: {p.field_name}"
            else:
                return str(p)

        parents = indent_str('\n'.join(map(parent_str, self._lineage)), n=3)
        out_str = ''
        out_str += f"{connector}{self._type.name} ⬅ SQL Piece: {self.get_sql()}\n"
        out_str += indent_str(f"{connector}[{colored(self._op_name.upper(), 'blue')}]\n{parents}")

        return prettify_tree(out_str)

from abc import abstractmethod

from lumipy.query.expression.base_expression import BaseExpression
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.client import Client
from typing import List


class BaseTable(BaseExpression):

    """
    The BaseTable Class is the base class for all table types. Its purpose is to represent a piece of
    data consisting of a collection of columns. It's responsible for tracking whether columns or expression
    built from columns belong to the table. It also holds the web client object so it can be passed
    along to objects that work with these via method chaining.
    Each of the columns that belong to the table are manifested as public attributes on instances of this class
    and its inheritors.
    """

    @abstractmethod
    def __init__(
            self,
            columns: List[BaseColumnExpression],
            client: Client,
            table_op_name: str,
            *values: BaseExpression
    ):
        """__init__ method of the BaseTable class.

        Args:
            columns List[BaseColumnExpression]: the columns that constitute this table.
            client (Client): luminesce webapi client object.
            table_op_name (str): name of the table op
            *values BaseExpression: input values to the table expression
        """
        if any(not issubclass(type(c), BaseColumnExpression) for c in columns):
            raise TypeError("All table columns must inherit from BaseColumnExpression.")

        for col in columns:
            if col.get_name() in self.__dict__.keys():
                raise ValueError(
                    f"Table ctor given duplicate column: field with this name already exists ({col.get_name()})."
                )
            else:
                self.__dict__[col.get_name()] = col

        self._client = client
        self._column_hashes = [hash(c) for c in self.get_columns()]

        super().__init__(
            table_op_name,
            lambda *args: True,
            lambda *args: SqlValType.Table,
            *values
        )

    def get_client(self) -> Client:
        """Get the connected luminesce webapi client.

        Returns:
            Client: the client object.
        """
        return self._client

    def get_columns(self) -> List[SourceColumn]:
        """Get a list of all of the columns that belong to this table.

        Returns:
            List[BaseColumnExpression]: list of columns / functions of columns
        """
        return [v for k, v in self.__dict__.items()
                if issubclass(type(v), BaseColumnExpression) and not k.startswith('_')]

    def contains_column(self, column: BaseColumnExpression) -> bool:
        """Check whether a column object is a member of this table.

        Args:
            column (BaseColumnExpression): the column expression to check.

        Returns:
            bool: True if column is a member, else False.
        """
        return hash(column) in self._column_hashes

    def __hash__(self):
        return hash(sum([hash(p) for p in self.get_lineage()]))

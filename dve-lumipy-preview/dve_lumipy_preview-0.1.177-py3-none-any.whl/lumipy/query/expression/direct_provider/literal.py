import numpy as np
from .direct_provider_base import DirectProviderBase
from ..sql_value_type import _get_type
from typing import Union, List, Tuple, Optional
from lumipy.client import Client
from lumipy.query.expression.column.column_literal import primitive_to_str


class TableLiteral(DirectProviderBase):
    """Class representing a SQL table literal where the table values are defined in the query SQL string.

    """

    def __init__(
            self,
            values: Union[List, Tuple, np.ndarray],
            columns: Optional[List[str]] = None,
            client: Optional[Client] = None
    ):
        """

        Args:
            values (Union[List, Tuple, np.ndarray]): values to use in the table literal.
            columns (Optional[List[str]]): optional column names to use in the table literal (defaults to Col0, Col1, ...)
            client (Optional[Client]): optional client to use in the fluent syntax when calling go()
        """

        self.vals = np.array(values)
        if len(self.vals.shape) not in (1, 2):
            raise ValueError(
                f"Bad shape for table literal data: must be one or two dimensional (was {len(self.vals.shape)})."
            )

        if len(self.vals.shape) == 1:
            self.vals = self.vals.reshape(-1, 1)

        if any(d == 0 for d in self.vals.shape):
            raise ValueError(f"All of the array dimensions must be non-zero in length: was {self.vals.shape}")

        if columns is None:
            columns = [f'Col{i}' for i in range(self.vals.shape[1])]

        row_strs = [f"({', '.join(primitive_to_str(v) for v in row)})" for row in self.vals]
        values_str = f"VALUES {', '.join(row_strs)}"
        cols_str = ", ".join(f'[column{i+1}] AS [{c}]' for i, c in enumerate(columns))

        def_str = f'\nSELECT\n  {cols_str}\nFROM\n  ({values_str})'

        var_name = f"tv_{str(hash(def_str))[1:]}"
        types = [_get_type(v) for v in self.vals[0]]
        guide = {c: t for c, t in zip(columns, types)}

        super().__init__(
            def_str,
            var_name,
            guide,
            client
        )

"""
sql rendering functions
"""
import re
from typing import List

from pyrasgo.schemas.dw_operation import Operation
from pyrasgo.utils import naming

__all__ = ['operations_as_cte']


def operations_as_cte(
    operations: List[Operation],
) -> str:
    """
    Returns a nested CTE statement to render this op set as a CTE
    """
    # Handle single transform chains, we already have the SQL
    if len(operations) == 1:
        return operations[0].operation_sql

    # Handle multi-transform chains
    operation_list = []
    # Need to replace old FQTNs with CTE aliases
    fqtn_mapping = {}
    for operation in operations:
        # create new aliases to replace old FQTNs with
        alias = operation.dw_table.table_name or naming.random_table_name()
        fqtn_mapping[operation.dw_table.fqtn] = alias

        op_sql = operation.operation_sql

        # replace all instances of generated FQTNs with CTE aliases
        for fqtn, alias in fqtn_mapping.items():
            op_sql = op_sql.replace(fqtn, alias)

        # if final op, we're done. join ops and leave last one alone
        # Final op itself might be a CTE, remove the WITH and slap it on the end of this chain
        if operation == operations[-1]:
            return 'WITH {}{}'.format(', \n'.join(operation_list), collapse_cte(op_sql))

        operation_list.append(f'{alias} AS (\n{op_sql}\n) ')


def collapse_cte(sql: str) -> str:
    """
    Returns a collapsed CTE if the sql itself is already a CTE (starts with "with")
    """
    return re.sub(r'^(WITH)\s', ', ', sql, 1, flags=re.IGNORECASE)

"""
DataWarehouse connection functions
"""
from typing import Union

from pyrasgo import errors
from .bigquery import BigQueryDataWarehouse
from .snowflake import SnowflakeDataWarehouse

__all__ = ["dw_connection", "DataWarehouse"]

DataWarehouse = Union[BigQueryDataWarehouse, SnowflakeDataWarehouse]


def dw_connection(organization_dw_type: str) -> DataWarehouse:
    """
    Returns a DataWarehouse class based on the organization
    """
    if organization_dw_type == "BIGQUERY":
        return BigQueryDataWarehouse()
    elif organization_dw_type == "SNOWFLAKE":
        return SnowflakeDataWarehouse()
    else:
        raise errors.DWCredentialsWarning(
            f"{organization_dw_type} is an unrecognized Cloud Data Warehouse. " " Cannot create a connection. "
        )

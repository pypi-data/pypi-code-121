from typing import Optional

from pandakeeper.validators import AnyDataFrame
from pandas import DataFrame
from pandera import DataFrameSchema
from pyspark import SparkContext, HiveContext, SparkConf

from sber_ld_dbtools.credentials import PasswordKeeper
from sber_ld_dbtools.loader.spark import SparkBaseLoader

__all__ = (
    'SparkHiveLoader',
)


def _read_hive_sql(sql_query: str, conn: SparkContext) -> DataFrame:
    hc = HiveContext(conn)
    sql_result = hc.sql(sql_query)
    return sql_result.toPandas()


class SparkHiveLoader(SparkBaseLoader):
    __slots__ = ()

    def __init__(self,
                 sql_query: str,
                 *,
                 credentials: Optional[PasswordKeeper] = None,
                 conf: Optional[SparkConf] = None,
                 output_validator: DataFrameSchema = AnyDataFrame) -> None:
        super().__init__(
            sql_query,
            credentials=credentials,
            conf=conf,
            read_sql_fn=_read_hive_sql,
            output_validator=output_validator
        )

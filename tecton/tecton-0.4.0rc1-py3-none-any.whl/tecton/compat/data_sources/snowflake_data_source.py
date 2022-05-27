from typing import Optional

from tecton.declarative.base import BaseBatchDSConfig
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import function_serialization


class SnowflakeDSConfig(BaseBatchDSConfig):
    """
    Configuration used to reference a Snowflake table or query.

    The SnowflakeDSConfig class is used to create a reference to a Snowflake table. You can also create a
    reference to a query on one or more tables, which will be registered in Tecton in a similar way as a view
    is registered in other data systems.

    This class used as an input to a :class:`BatchDataSource`'s parameter ``batch_ds_config``. This class is not
    a Tecton Object: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare as part of ``BatchDataSource`` that takes this configuration class instance as a parameter.
    """

    def __init__(
        self,
        *,
        database: str,
        schema: str,
        warehouse: Optional[str] = None,
        url: Optional[str] = None,
        role: Optional[str] = None,
        table: Optional[str] = None,
        query: Optional[str] = None,
        timestamp_key: Optional[str] = None,
        raw_batch_translator=None,
    ):
        """
        Instantiates a new SnowflakeDSConfig. One of table and query should be specified when creating this file.

        :param url: The connection URL to Snowflake, which contains account information
                         (e.g. https://xy12345.eu-west-1.snowflakecomputing.com).
        :param database: The Snowflake database for this Data source.
        :param schema: The Snowflake schema for this Data source.
        :param warehouse: The Snowflake warehouse for this Data source.
        :param role: (Optional) The Snowflake role that should be used for this Data source.

        :param table: The table for this Data source. Only one of `table` and `query` must be specified.
        :param query: The query for this Data source. Only one of `table` and `query` must be specified.

        :param raw_batch_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                     PySpark data source DataFrame and translates it to the DataFrame to be
                                     consumed by the Feature View. See an example of
                                     raw_batch_translator in the `User Guide`_.
        :param timestamp_key: (Optional) The name of the timestamp column (after the raw_batch_translator has been applied).
                               The column name does not need to be specified if there is exactly one timestamp column after the translator is applied.
                               This is needed for efficient time filtering when materializing batch features.

        :return: A SnowflakeDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html

        Example of a SnowflakeDSConfig declaration:

        .. code-block:: python

            from tecton.compat import SnowflakeDSConfig, BatchDataSource

            # Declare SnowflakeDSConfig instance object that can be used as an argument in BatchDataSource
            snowflake_ds_config = SnowflakeDSConfig(
                                              url="https://<your-cluster>.eu-west-1.snowflakecomputing.com/",
                                              database="CLICK_STREAM_DB",
                                              schema="CLICK_STREAM_SCHEMA",
                                              warehouse="COMPUTE_WH",
                                              table="CLICK_STREAM_FEATURES",
                                              query="SELECT timestamp as ts, created, user_id, clicks, click_rate"
                                                     "FROM CLICK_STREAM_DB.CLICK_STREAM_FEATURES")

            # Use in the BatchDataSource
            snowflake_ds = BatchDataSource(name="click_stream_snowflake_ds",
                                           batch_ds_config=snowflake_ds_config)
        """
        self._args = args = data_source_pb2.SnowflakeDataSourceArgs()
        args.database = database
        args.schema = schema
        if url:
            args.url = url
        if warehouse:
            args.warehouse = warehouse

        if role:
            args.role = role

        if table:
            args.table = table
        if query:
            args.query = query

        if raw_batch_translator is not None:
            args.raw_batch_translator.CopyFrom(function_serialization.to_proto(raw_batch_translator))
        if timestamp_key:
            args.timestamp_key = timestamp_key

    def _merge_batch_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        data_source_args.snowflake_ds_config.CopyFrom(self._args)

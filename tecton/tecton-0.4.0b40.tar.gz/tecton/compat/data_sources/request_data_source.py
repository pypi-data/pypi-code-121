from typing import List
from typing import Union

from pyspark.sql.types import StructType

from tecton.declarative.base import RequestSourceBase
from tecton.types import Field
from tecton_spark.id_helper import IdHelper


class RequestDataSource(RequestSourceBase):
    """
    Declare a ``RequestDataSource``, for using request-time data in an ``OnDemandFeatureView``.
    """

    def __init__(
        self,
        request_schema: Union[StructType, List[Field]],
    ):
        """
        Creates a new RequestDataSource

        :param request_schema: PySpark schema for the RequestDataSource inputs.

        Example of a RequestDataSource declaration:

        .. code-block:: python

            from tecton import RequestDataSource
            from pyspark.sql.types import DoubleType, StructType, StructField

            request_schema = StructType([StructField('amount', DoubleType())])
            transaction_request = RequestDataSource(request_schema=request_schema)
        """
        self.request_schema = request_schema
        self.id = IdHelper.from_string(IdHelper.generate_string_id())

    @property
    def schema(self):
        return self.request_schema

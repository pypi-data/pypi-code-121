import tecton_proto.data.batch_data_source_pb2 as batch_pb2
from tecton._internals import errors


# NOTE: When adding a new format, change data_source_helper.py:_partition_value_for_time if needed
class DatetimePartitionColumn:
    """
    Helper class to tell Tecton how underlying flat files are date/time partitioned for Hive/Glue data sources. This can translate into a significant performance increase.

    You will generally include an object of this class in the `datetime_partition_columns` option in a `HiveDSConfig` object.
    """

    # pass zero_padded=True if the partition column is a string that is zero-padded
    def __init__(self, column_name, datepart, zero_padded):
        """
        Instantiates a new DatetimePartitionColumn configuration object.


        :param column_name: The name of the column in the Glue/Hive schema that corresponds to the underlying date/time partition folder. Note that if you do not explicitly specify a name in your partition folders, Glue will name the column of the form ``partition_0``.
        :param datepart: The part of the date that this column specifies. Can be one of "year", "month", "day", "hour", or the full "date".
        :param zero_padded: Whether the ``datepart`` has a leading zero if less than two digits. This must be set to True if ``datepart`` = ``date``.

        Example definition:

            Assume you have an S3 bucket with parquet files stored in the following structure: ``s3://mybucket/2022/05/04/<multiple parquet files>`` , where ``2022`` is the year, ``05`` is the month, and ``04`` is the day of the month. In this scenario, you could use the following definition:

            .. code-block:: python

                datetime_partition_columns = [
                    DatetimePartitionColumn(column_name="partition_0", datepart="year", zero_padded=True),
                    DatetimePartitionColumn(column_name="partition_1", datepart="month", zero_padded=True),
                    DatetimePartitionColumn(column_name="partition_2", datepart="day", zero_padded=True),
                ]

        :return: DatetimePartitionColumn instantiation
        """
        self.column_name = column_name
        self.datepart = datepart
        self.zero_padded = zero_padded

        datepart = datepart.lower()
        if datepart == "year":
            self.format_string = "%Y"
            self.minimum_seconds = 365 * 24 * 60 * 60
        elif datepart == "month":
            self.format_string = "%m"
            self.minimum_seconds = 28 * 24 * 60 * 60
        elif datepart == "day":
            self.format_string = "%d"
            self.minimum_seconds = 24 * 60 * 60
        elif datepart == "hour":
            self.format_string = "%H"
            self.minimum_seconds = 60 * 60
        elif datepart == "date":
            if not zero_padded:
                # we don't support non-zero-padded date strings because we use string comparison for them which would get broken
                raise errors.UNSUPPORTED_OPERATION(
                    "DatetimePartitionColumn for date with zero_padded=False", "Must have zero-padded=True"
                )
            self.format_string = "%Y-%m-%d"
            self.minimum_seconds = 24 * 60 * 60
        else:
            raise errors.UNSUPPORTED_OPERATION(
                "DatetimePartitionColumn with datepart=%s" % datepart,
                "Supported dateparts: year, month, day, hour, date",
            )
        if not zero_padded:
            self.format_string = self.format_string.replace("%", "%-")

    def _to_proto(self):
        proto = batch_pb2.DatetimePartitionColumn()
        proto.column_name = self.column_name
        proto.format_string = self.format_string
        proto.minimum_seconds = self.minimum_seconds
        return proto

"""Useful functions for date/time"""
import datetime
from typing import List


DATE_FORMAT = "%Y-%m-%d"


class TimeUtils:
    """
    Class that provides useful functions for dates and times
    """

    @staticmethod
    def get_dates_in_time_interval(start_date: datetime.date, end_date: datetime.date) -> List[datetime.date]:
        """
        Get all dates between start and end date. It includes the start_date, but not the end_date.

        :param start_date: The start date
        :param end_date: The end date
        :return:
        """
        delta = end_date - start_date  # as timedelta
        days_between_start_end = [start_date + datetime.timedelta(days=i) for i in range(delta.days)]

        return days_between_start_end

    @staticmethod
    def generate_partition_folder_names(dates: List[datetime.date], partition_column="dt") -> List[str]:
        """
        Generates the partition folder names for a list of dates, eg for [2020-01-01, 2020-01-02] and partition column
        dt it generates ["dt=2020-01-01", "dt=2020-01-02"]

        :param dates: List of dates
        :param partition_column: Name of the partition column
        :return: List of folder names for the given dates
        """
        formatted_dates = [d.strftime(DATE_FORMAT) for d in dates]

        return [f"{partition_column}={d}" for d in formatted_dates]

    @staticmethod
    def string2date(the_date: str, date_format: str = DATE_FORMAT) -> datetime.date:
        """
        Convert a string to date

        :param the_date: date provided as string
        :param date_format: the format in which the date is provided
        :return: The date as a datetime.date
        """

        return datetime.datetime.strptime(the_date, date_format).date()

    @staticmethod
    def date2string(the_date: datetime.date, date_format: str = DATE_FORMAT) -> str:
        """
        Convert a string to date

        :param the_date: date provided as datetime.date
        :param date_format: the desired format
        :return: The date as a string
        """

        return the_date.strftime(date_format)

    @staticmethod
    def get_yesterday() -> datetime.date:
        """
        Gets yesterday's date as datetime.date

        :return: Yesterday's date
        """
        yesterday_datetime = datetime.date.today() - datetime.timedelta(1)

        return yesterday_datetime

"""Class describing an interval of time."""
import datetime


class TimeRange:
    """This class describe an interval of time."""

    def __init__(
        self, start: datetime.datetime, end: datetime.datetime, is_critical: bool
    ):
        """Period constructor."""
        self._start_date: datetime.datetime = start
        self._end_date: datetime.datetime = end
        self._is_critical: bool = is_critical

    @property
    def start_date(self) -> datetime.datetime:
        """Get start date of the time range."""
        return self._start_date

    @property
    def end_date(self) -> datetime.datetime:
        """Get end date of the time range."""
        return self._end_date

    @property
    def is_critical(self) -> bool:
        """Get critical status of the time range."""
        return self._is_critical

    def __repr__(self) -> str:
        """Make object repr more readable."""
        if self.is_critical:
            repr_str = f"<{self.__class__.__name__} - {self.start_date} - critical>"
        else:
            repr_str = f"<{self.__class__.__name__} - {self.start_date}>"
        return repr_str

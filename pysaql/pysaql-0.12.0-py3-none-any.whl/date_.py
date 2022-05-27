"""Contains date functions"""

from typing import Optional, Union

from .enums import DateDiffUnit, RelativeDateUnit, RelativeTimeframe
from .expression import Expression
from .function import Function
from .scalar import Scalar
from .util import escape_string


class DateFunction(Function):
    """Generic function that accepts a single date argument"""

    def __init__(self, date: Scalar):
        """Initializer

        Args:
            date: Date or field reference to process

        """
        super().__init__(date)


class day_in_week(DateFunction):
    """Returns an integer representing the day of the week for a specific date"""

    pass


class day_in_month(DateFunction):
    """Returns an integer representing the day of the month for a specific date"""

    pass


class day_in_quarter(DateFunction):
    """Returns an integer representing the day of the quarter for a specific date"""

    pass


class day_in_year(DateFunction):
    """Returns an integer representing the day of the year for a specific date"""

    pass


class week_first_day(DateFunction):
    """Returns the date of the first day of the week for the specified date"""

    pass


class fiscal_week_first_day(DateFunction):
    """Returns the fiscal date of the first day of the week for the specified date"""

    pass


class month_first_day(DateFunction):
    """Returns the date of the first day of the month for the specified date"""

    pass


class fiscal_month_first_day(DateFunction):
    """Returns the fiscal date of the first day of the month for the specified date"""

    pass


class quarter_first_day(DateFunction):
    """Returns the date of the first day of the quarter for the specified date"""

    pass


class fiscal_quarter_first_day(DateFunction):
    """Returns the fiscal date of the first day of the quarter for the specified date"""

    pass


class year_first_day(DateFunction):
    """Returns the date of the first day of the year for the specified date"""

    pass


class fiscal_year_first_day(DateFunction):
    """Returns the fiscal date of the first day of the year for the specified date"""

    pass


class to_date(Function):
    """Converts a string or Unix epoch seconds to a date"""

    _name: str = "toDate"

    def __init__(self, string: Scalar, format_string: Optional[str] = None):
        """Initializer

        Args:
            string: Date string to parse
            format_string: Format string. Defaults to None.

        """
        super().__init__(string, format_string)


class date_diff(Function):
    """Returns the amount of time between two dates."""

    def __init__(
        self, date_part: DateDiffUnit, start_date: Scalar, end_date: Scalar
    ) -> None:
        """Initializer

        Args:
            date_part: Date unit for measuring the time interval
            start_date: Start date
            end_date: End date

        """
        super().__init__(date_part, start_date, end_date)


class days_between(Function):
    """Returns the number of days between two dates."""

    _name = "daysBetween"

    def __init__(self, start_date: Scalar, end_date: Scalar) -> None:
        """Initializer

        Args:
            start_date: Start date
            end_date: End date

        """
        super().__init__(start_date, end_date)


class now(Function):
    """Returns the current datetime in UTC."""

    pass


class year(DateFunction):
    """Get the year from a date value"""

    pass


class quarter(DateFunction):
    """Get the quarter from a date value"""

    pass


class month(DateFunction):
    """Get the month from a date value"""

    pass


class week(DateFunction):
    """Get the week from a date value"""

    pass


class day(DateFunction):
    """Get the day from a date value"""

    pass


class minute(DateFunction):
    """Get the minute from a date value"""

    pass


class second(DateFunction):
    """Get the second from a date value"""

    pass


class fiscal_year(DateFunction):
    """Get the fiscal year from a date value"""

    _name = "fiscalYear"


class fiscal_quarter(DateFunction):
    """Get the fiscal quarter from a date value"""

    _name = "fiscalQuarter"


class fiscal_month(DateFunction):
    """Get the fiscal month from a date value"""

    _name = "fiscalMonth"


class fiscal_week(DateFunction):
    """Get the fiscal week from a date value"""

    _name = "fiscalWeek"


class epoch_day(DateFunction):
    """Get the epoch day from a date value"""

    _name = "epochDay"


class epoch_second(DateFunction):
    """Get the epoch second from a date value"""

    _name = "epochSecond"


class date(Function):
    """Returns a date that can be used in a filter"""

    def __init__(
        self,
        year: Union[Scalar, int],
        month: Optional[Union[Scalar, int]] = None,
        day: Optional[Union[Scalar, int]] = None,
    ) -> None:
        """Initializer

        Args:
            year: Year value
            month: Month value. Defaults to None.
            day: Day value. Defaults to None.

        """
        super().__init__(year, month, day)

    def to_string(self) -> str:
        """Cast the date into a string

        Returns:
            SAQL string

        """
        args = [str(arg) for arg in self._args if arg is not None]
        name = self._name or self.__class__.__name__
        s = f"{', '.join(args)}"
        if len(args) > 1:
            s = f"{name}({s})"

        return s


class relative_date(Expression):
    """Construct a relative date to use in a filter expression"""

    def __init__(
        self, timeframe: RelativeTimeframe, unit: RelativeDateUnit, quantity: int = 1
    ) -> None:
        """Initializer

        Args:
            timeframe: Timeframe of the relative date range
            unit: Date unit
            quantity: Number of date units. This is ignored if the timeframe is current.
                Defaults to 1.

        """
        super().__init__()
        self.timeframe = timeframe
        self.unit = unit
        self.quantity = quantity

    def to_string(self) -> str:
        """Cast the relative date into a string

        Returns:
            SAQL string

        """
        if self.timeframe is RelativeTimeframe.current:
            return escape_string(f"{self.timeframe} {self.unit}")
        else:
            unit = f"{self.unit}s" if self.quantity > 1 else self.unit
            return escape_string(f"{self.quantity} {unit} {self.timeframe}")


class date_range(Expression):
    """Construct a date range to use in filter expression"""

    def __init__(
        self,
        start_date: Optional[Union[date, relative_date]] = None,
        end_date: Optional[Union[date, relative_date]] = None,
    ) -> None:
        """Initializer

        Args:
            start_date: Start date, either absolute or relative. Defaults to None, which
                indicates an open-ended start date.
            end_date: End date, either absolute or relative. Defaults to None, which
                indicates an open-ended end date.

        """
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date

    def to_string(self) -> str:
        """Cast the date range into a string

        Returns:
            SAQL string

        """
        if isinstance(self.start_date, date) and isinstance(self.end_date, date):
            start = ",".join(str(arg) for arg in self.start_date._args)
            end = ",".join(str(arg) for arg in self.end_date._args)
            return f"[dateRange([{start}], [{end}])]"
        else:
            start = str(self.start_date) if self.start_date else ""
            end = str(self.end_date) if self.end_date else ""
            return f"[{start}..{end}]"

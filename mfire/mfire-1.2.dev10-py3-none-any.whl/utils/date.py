"""
@package utils.date

Module for handling custom datetime, timedelta and period objects.
"""

# Built-in packages
from __future__ import annotations
import re
import datetime
from typing import Optional, Union

# Third parties packages
import numpy as np
import xarray as xr
import dateutil.parser

# Own package
from mfire.settings import Settings, TEMPLATES_FILENAMES
from mfire.utils.json_utils import JsonFile
from mfire.text.template import TemplateRetriever, read_file

# Logging

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

DATES = JsonFile(TEMPLATES_FILENAMES[Settings().language]["date"]).load()


class Datetime(datetime.datetime):
    """Datetime : overlayer of the built-in datetime.datetime class
    for more versatility.
    """

    def __new__(cls, *args, **kwargs):
        if kwargs and not args:
            args = (datetime.datetime(**kwargs),)
        if not args:
            return Datetime.utcnow()
        tz_kw = kwargs.get("tzinfo", datetime.timezone.utc)
        if len(args) == 1:
            top = args[0]
            ndt = None
            ldt = list()
            if top is NotImplemented:
                return NotImplemented
            if isinstance(top, bytes):
                top = datetime.datetime(top)
            if isinstance(top, xr.DataArray):
                top = top.values
            if isinstance(top, datetime.datetime):
                if top.tzinfo:
                    tz_kw = top.tzinfo
                ldt = [
                    top.year,
                    top.month,
                    top.day,
                    top.hour,
                    top.minute,
                    top.second,
                    top.microsecond,
                ]
            elif isinstance(top, str):
                ndt = dateutil.parser.parse(top)
            elif isinstance(top, (int, float)):
                ndt = datetime.datetime.utcfromtimestamp(top)
            elif isinstance(top, np.datetime64):
                timestamp = (
                    top - np.datetime64("1970-01-01T00:00:00")
                ) / np.timedelta64(1, "s")
                ndt = datetime.datetime.utcfromtimestamp(timestamp)

            if isinstance(ndt, datetime.datetime):
                if ndt.tzinfo:
                    tz_kw = ndt.tzinfo
                ldt = [
                    ndt.year,
                    ndt.month,
                    ndt.day,
                    ndt.hour,
                    ndt.minute,
                    ndt.second,
                    ndt.microsecond,
                ]

        else:
            ldt = [int(x) if isinstance(x, (int, float)) else x for x in args]
            if len(ldt) == 8:
                tz_kw = ldt.pop()
                if tz_kw is None:
                    tz_kw = datetime.timezone.utc

        if not ldt:
            raise ValueError("Datetime value unknown")
        return datetime.datetime.__new__(cls, *ldt, tzinfo=tz_kw)

    def __str__(self) -> str:
        return self.isoformat()

    def __add__(self, delta: Timedelta) -> Datetime:
        """Add to a Datetime object the specified delta

        Args:
            delta (Timedelta): Delta to add

        Returns:
            Datetime: New datetime
        """
        return Datetime(super().__add__(delta))

    def __radd__(self, delta: Timedelta) -> Datetime:
        """Reversed add."""
        return self.__add__(delta)

    def __sub__(self, delta: Union[Timedelta, Datetime]) -> Union[Datetime, Timedelta]:
        """Subtract to a Date object the specified delta

        Args:
            delta (Union[Timedelta, Datetime]): Delta to substract
                - if a Datetime, returns a Timedelta
                - if a Timedelta, returns a Datetime

        Returns:
            Union[Datetime, Timedelta]: Substracted value
        """
        substract = super().__sub__(delta)
        if isinstance(delta, Datetime):
            return Timedelta(substract)
        return Datetime(substract)

    def __rsub__(self, delta: Datetime) -> Timedelta:
        """Reversed-substract (works only with Datetime objects)"""
        return Timedelta(delta.__sub__(self))

    def astimezone(self, tz=LOCAL_TIMEZONE) -> Datetime:
        """convert to local time in new timezone tz

        Args:
            tz (timezone, optional): Timezone object.
                Defaults to LOCAL_TIMEZONE.

        Returns:
            Datetime: New datetime
        """
        return Datetime(super().astimezone(tz=tz))

    @classmethod
    def now(cls, tz=LOCAL_TIMEZONE) -> Datetime:
        """Returns the current local datetime.

        Args:
            tz (timezone, optional): Timezone object.
                Defaults to LOCAL_TIMEZONE.

        Returns:
            Datetime: Current local datetime
        """
        return Datetime(datetime.datetime.now(tz))

    @property
    def utc(self) -> Datetime:
        """convert local time in utc timezone

        Returns:
            Datetime: Utc datetime
        """
        return self.astimezone(tz=datetime.timezone.utc)

    @property
    def rounded(self) -> Datetime:
        """rounded : returns the actual datetime o'clock

        Returns:
            Datetime : Actual Datetime o'clock
        """
        return Datetime(self.year, self.month, self.day, self.hour, tzinfo=self.tzinfo)

    @property
    def midnight(self) -> Datetime:
        """midnight : returns midnight's time of the self date

        Returns:
            Datetime: midnight time of self date
        """
        return Datetime(self.year, self.month, self.day, tzinfo=self.tzinfo)

    @property
    def calendar_date(self) -> Datetime:
        """calendar_date: returns the calendar date of the given self.
        Example : Datetime(2021, 6, 28, 9, 4) calendar date is Datetime(2021, 6, 28)

        Returns:
            Datetime: calendar date
        """
        return Datetime(self.year, self.month, self.day, tzinfo=self.tzinfo)

    def is_same_day(self, other_datetime: Datetime) -> bool:
        """is_same_day: returns True if the self datetime and the given
        other datetime share the same calendar date.

        Args:
            other_datetime (Datetime): Other datetime to compare

        Returns:
            bool: True if the self datetime and the given other datetime
                share the same calendar date.
        """
        return self.calendar_date == Datetime(other_datetime).calendar_date

    def as_datetime(self) -> datetime.datetime:
        """return the datetime to the datetime.datetime format

        Returns:
            datetime.datetime: datetime object
        """
        return datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
        )

    def as_np_datetime64(self) -> np.datetime64:
        """Return the self datetime to the np.datetime64 format.
        Made for preventing np.datetime64 warning of conversion
        of timezone-aware datetimes.

        Returns:
            np.datetime64: self with a np.datetime64 format.
        """
        return np.datetime64(self.utc.replace(tzinfo=None))

    def is_synoptic(self) -> bool:
        """True if the current hour is a synoptic one."""
        return self.hour in (0, 6, 12, 18)

    @property
    def weekday_name(self) -> str:
        """weekday_name : return a Day type object corresponding
        to the actual weekday of the self date

        Returns:
            str : actual weekday's name
        """
        return DATES["weekdays"][self.weekday()]

    @property
    def month_name(self) -> str:
        """month_name : return a Month  type object corresponding
        to the actual month of the self date

        Returns:
            str : actual month's name
        """
        return DATES["months"][self.month - 1]

    def literal_day(self, display_year: Optional[bool] = True) -> str:
        """literal_day : returns the actual date's day literal description

        Args:
            display_year (Optional[bool], optional): Whether to display the self.year
                or not. Defaults to True.

        Returns:
            str: self day literal description
        """
        numday = str(self.day)
        numday += DATES["numdays"].get(numday, DATES["numdays"].get("*", ""))

        year = ""
        if display_year:
            year = str(self.year)

        return (
            DATES["literal_date"]
            .format(
                weekday=self.weekday_name,
                numday=numday,
                month=self.month_name,
                year=year,
            )
            .strip()
        )

    @property
    def moment(self) -> dict:
        """moment : property which return a Moment type object
        corresponding to the corresponding moment in the day
        """
        moments = sorted(
            [(moment, dico["start"]) for moment, dico in DATES["moments"].items()],
            key=lambda x: x[1],
            reverse=True,
        )
        moment = next(
            (moment for moment, start in moments if self.hour >= start), moments[0][0]
        )
        return DATES["moments"][moment]

    def format_bracketstr(self, bracketstr: str) -> str:
        """format_bracketstr : Replace date tags in brackets like, '[date]' or
        '[date-1]' in a str by the self formatted datetime.

        Args:
            bracketstr: String containing '[date]', '[date+n]' or '[date-m]' patterns
                with 'n' and 'm' being natural integers.
        Returns:
            str : Formatted string
        """
        if not isinstance(bracketstr, str):
            return bracketstr
        return re.sub(
            r"\[date(|[-+]\d*)\]",
            lambda x: str(
                (
                    self + Timedelta(days=int(float(x.group().strip("[date]") + ".0")))
                ).midnight
            ),
            bracketstr,
        )

    def describe_day(self, reference_datetime: Datetime) -> str:
        """describe_day: describes textually the self.day with the point of view
        of a given reference_datetime.
        Examples (with french settings):
        >>> d0 = Datetime(1996, 4, 17, 12)
        >>> print(d0.describe(d0))
        "aujourd'hui"
        >>> d0.describe(Datetime(1996, 4, 16))
        "demain"
        >>> d0.describe(Datetime(1996, 4, 18))
        "hier"
        >>> d0.describe(Datetime(1996, 4, 15))
        "mercredi"
        >>> d0.describe(Datetime.utcnow())
        "mercredi 17 avril 1996"

        Args:
            reference_datetime (Datetime): Point of view to describe the
                self.day.

        Returns:
            str: Textual description.
        """
        days_delta = (self.midnight - reference_datetime.midnight).days

        day_name = DATES["days_delta"].get(str(days_delta), self.weekday_name)

        if days_delta < -1 or days_delta > 6:
            display_year = self.year != reference_datetime.year
            day_name = self.literal_day(display_year=display_year)
            usage = DATES["week_shifts"]["usage"]
            if days_delta == 7:
                day_name = usage.format(
                    day=self.weekday_name, shift=DATES["week_shifts"]["next"]
                )
            elif -8 < days_delta < 0:
                day_name = usage.format(
                    day=self.weekday_name, shift=DATES["week_shifts"]["last"]
                )
        return day_name

    def describe_moment(self, reference_datetime: Datetime) -> str:
        """describe_moment: describes textually the self.moment with the point of view
        of a given reference_datetime.
        Examples (with french settings):
        >>> d0 = Datetime(2021, 4, 15, 10)
        >>> print(d0.describe(d0))
        "ce matin"
        >>> d0.describe(Datetime(2021, 4, 11))
        "matin"
        >>> d1 = Datetime(2021, 4, 15, 19)
        >>> d1.describe(Datetime(2021, 4, 15))
        "ce soir"
        >>> d1.describe(Datetime(2021, 4, 18))
        "soir"

        Args:
            reference_datetime (Datetime): Point of view to describe the
                self.moment.

        Returns:
            str: Textual description.
        """
        days_delta = (self.midnight - reference_datetime.midnight).days

        start_min = np.min([moment["start"] for moment in DATES["moments"].values()])
        if days_delta == 0 or (days_delta == 1 and self.hour < start_min):
            return self.moment["demo"]

        if days_delta < -1 or days_delta > 6:
            return self.moment["circ"]["all"]

        return self.moment["name"]

    def describe(self, reference_datetime: Datetime) -> str:
        """describe : function which describe self from the
        reference_datetime perspective.
        Exemple :
        >>> reference_time = Datetime(2021, 2, 12)
        >>> begin_time = Datetime(2021, 2, 13, 9)
        >>> end_time = Datetime(2021, 2, 14, 21)
        >>> begin_time.describe(reference_time)
        "demain matin"
        >>> end_time.describe(reference_time)
        "dimanche soir"

        Args:
            reference_datetime (Datetime): reference datetime from which
                perspective the self description must be done

        Returns:
            str : textual description of the datetime
        """
        moment_name = self.describe_moment(reference_datetime=reference_datetime)
        if moment_name == self.moment["demo"]:
            return moment_name

        day_name = self.describe_day(reference_datetime=reference_datetime)
        if self.moment == DATES["moments"]["night"]:
            if self.hour < 12:
                day_before_name = Datetime(self - Timedelta(days=1)).describe_day(
                    reference_datetime=reference_datetime
                )
                return DATES["overnight"].format(day_1=day_before_name, day_2=day_name)

            day_after_name = Datetime(self + Timedelta(days=1)).describe_day(
                reference_datetime=reference_datetime
            )
            return DATES["overnight"].format(day_1=day_name, day_2=day_after_name)

        return f"{day_name} {moment_name}"


class Timedelta(datetime.timedelta):
    """Timedelta : overlayer of the built-in datetime.timedelta class
    for more versatility, and for custom Datetime compatibility
    """

    def __new__(cls, *args, **kwargs):
        if kwargs:
            args = (datetime.timedelta(**kwargs),)
        if not args:
            raise ValueError("No initial value provided for Timedelta")
        top = args[0]
        ld = list()
        if top is NotImplemented:
            return NotImplemented
        if isinstance(top, datetime.timedelta):
            ld = [top.days, top.seconds, top.microseconds]
        elif len(args) >= 1:
            ld = list(args)
        if not ld:
            raise ValueError("Initial Timedelta value unknown")
        return datetime.timedelta.__new__(cls, *ld)

    def __len__(self) -> int:
        return self.days * 86400 + self.seconds

    def __add__(self, delta: Union[Timedelta, Datetime]) -> Union[Datetime, Timedelta]:
        """Add to a Timedelta object the specified delta (which could be
        either a Datetime object or a Timedelta object.)

        Args:
            delta (Union[Timedelta, Datetime]): delta to add
                - if a Datetime object, returns a Datetime object
                - if a Timedelta object, returns a Timedelta object

        Returns:
            Union[Datetime, Timedelta]: Added object
        """
        add = super().__add__(delta)
        if isinstance(add, Datetime):
            return Datetime(add)
        return Timedelta(add)

    def __radd__(self, delta: Union[Timedelta, Datetime]) -> Union[Datetime, Timedelta]:
        """Reversed add."""
        return self.__add__(delta)

    def __sub__(self, delta: Timedelta) -> Timedelta:
        """Substract to a Timedelta object the specified delta

        Args:
            delta (Timedelta): delta to substract

        Returns:
            Timedelta: New timedelta
        """
        return Timedelta(super().__sub__(delta))

    def __rsub__(self, delta: Union[Timedelta, Datetime]) -> Union[Datetime, Timedelta]:
        """Substract to the specified delta a Timedelta object

        Args:
            delta (Union[Timedelta, Datetime]): delta to substract
                - if a Datetime object, returns a Datetime object
                - if a Timedelta object, returns a Timedelta object

        Returns:
            Timedelta: New timedelta
        """
        substract = delta.__sub__(self)
        if isinstance(delta, Datetime):
            return Datetime(substract)
        return Timedelta(substract)

    def __mul__(self, factor: Union[int, float]) -> Timedelta:
        """Multiply the self Timedelta by the given factor

        Args:
            factor (Union[int, float]): factor to multiply

        Returns:
            Timedelta: Multiplied timedelta
        """
        return Timedelta(super().__mul__(factor))

    def __rmul__(self, factor: Union[int, float]) -> Timedelta:
        """Multiply the self Timedelta by the given factor

        Args:
            factor (Union[int, float]): factor to multiply

        Returns:
            Timedelta: Multiplied timedelta
        """
        return self * factor

    def __neg__(self) -> Timedelta:
        """Returns the negative timedelta

        Returns:
            Timedelta: [description]
        """
        return Timedelta(0) - self

    def total_hours(self) -> int:
        """total_hours: equivalent of self.total_seconds but with hours

        Returns:
            int: Number of total hours
        """
        return int(self.total_seconds() // 3600)


class Period:
    """Period : class describing periods objects defined by :
    - a beginning (self.begin_time)
    - an end (self.end_time)
    """

    def __init__(
        self, begin_time: Datetime, end_time: Optional[Datetime] = None,
    ):
        """__init__ : initialization method

        Args:
            request_time (Datetime): 'point of view' to describe the
                given period that lasts from self.begin_time to self.end_time
            begin_time (Datetime): Beginning of the period.
            end_time (Optional[Datetime], optional): End of the period.
                Defaults to None.
        """
        self._begin_time = Datetime(begin_time)
        self._end_time = self._begin_time
        if end_time is not None:
            self._end_time = Datetime(end_time)
        self._template_retriever = None

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, self.__class__)
            and self.begin_time == obj.begin_time
            and self.end_time == obj.end_time
        )

    def toJson(self) -> dict:
        dout = {}
        dout["begin_time"] = str(self.begin_time)
        dout["end_time"] = str(self.end_time)
        return dout

    @property
    def begin_time(self) -> Datetime:
        """begin_time

        Returns:
            Datetime: Beginning of the period
        """
        return self._begin_time

    @begin_time.setter
    def begin_time(self, begin_time: Datetime):
        """begin_time : self.begin_time setter. Checks the given datetime
        compatibility with self._end_time

        Args:
            begin_time (Datetime): datetime object to initialize the
                self.begin_time object
        """
        if self._begin_time == self._end_time:
            self._end_time = Datetime(begin_time)
        self._begin_time = Datetime(begin_time)
        if self._begin_time > self._end_time:
            self._end_time = self._begin_time

    @property
    def end_time(self) -> Datetime:
        """end_time

        Returns:
            Datetime: End of the period
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time: Datetime):
        """end_time : self.end_time setter. Checks the given datetime
        compatibility with the self._begin_time

        Args:
            end_time (Dateime): datetime object to initialize the
                self.end_time object
        """
        if end_time is None:
            self._end_time = self._begin_time
        self._end_time = Datetime(end_time)
        if self._begin_time > self._end_time:
            self._begin_time = self._end_time

    def union(self, period: Period) -> Period:
        """union: creates the union of self and a given period.
        Example:
        >>> p1 = Period(Datetime(2021, 1, 1), Datetime(2021, 1, 2))
        >>> p2 = Period(Datetime(2021, 1, 3), Datetime(2021, 1, 4))
        >>> p1.union(p2)
        Period(Datetime(2021, 1, 1), Datetime(2021, 1, 4))

        Args:
            period (Period): given period to unite with self.

        Returns:
            Period: "united" period
        """
        begin_time = min(self.begin_time, period.begin_time)
        end_time = max(self.end_time, period.end_time)
        return self.__class__(begin_time, end_time)

    def intersects(self, period: Period) -> bool:
        """intersects: checks whether a given period intersects with self.
        Example:
        >>> p1 = Period(Datetime(2021, 1, 1), Datetime(2021, 1, 2))
        >>> p2 = Period(Datetime(2021, 1, 3), Datetime(2021, 1, 4))
        >>> p3 = Period(Datetime(2021, 1, 1, 23), Datetime(2021, 1, 2, 23))
        >>> p1.intersects(p2)
        False
        >>> p1.intersects(p3)
        True
        >>> p2.intersects(p3)
        False

        Args:
            period (Period): given period to check whether it intersects self.

        Returns:
            bool: Whether period intersects with self.
        """
        return (
            period.begin_time <= self.begin_time <= period.end_time
            or self.begin_time <= period.begin_time <= self.end_time
        )

    def extends(self, period: Period, request_time: Datetime = None) -> bool:
        """extends: checks whether a given period is an extension of self. We consider
        that a period p1 extends another period p2 if the period (p1 +/- 3H) intersects
        the period (p2 +/- 3H) or if the jonctions have the same textual
        descriptions.
        Example:
        >>> p1 = Period(Datetime(2021, 1, 1), Datetime(2021, 1, 2))
        >>> p2 = Period(Datetime(2021, 1, 3), Datetime(2021, 1, 4))
        >>> p3 = Period(Datetime(2021, 1, 1, 23), Datetime(2021, 1, 2, 23))
        >>> p1.extends(p2)
        False
        >>> p1.extends(p3)
        True
        >>> p2.extends(p3)
        True

        Args:
            period (Period): period to check whether it extends self.
            request_time (Datetime, optional): Point of view for textual
                descriptions. Defaults to None.

        Returns:
            bool: Whether the given period and self extend themselves.
        """
        return (
            period.begin_time - Timedelta(hours=3)
            <= self.begin_time
            <= period.end_time + Timedelta(hours=3)
            or self.begin_time - Timedelta(hours=3)
            <= period.begin_time
            <= self.end_time + Timedelta(hours=3)
            or (
                request_time is not None
                and (
                    self.begin_time.describe(request_time)
                    == period.end_time.describe(request_time)
                    or self.end_time.describe(request_time)
                    == period.begin_time.describe(request_time)
                )
            )
        )

    @property
    def template_retriever(self) -> TemplateRetriever:
        """template_retriever: template retriever used for describing short periods

        Returns:
            TemplateRetriever: template retriever
        """
        if isinstance(self._template_retriever, TemplateRetriever):
            return self._template_retriever
        self._template_retriever = read_file(
            TEMPLATES_FILENAMES[Settings().language]["period"]["short"]
        )
        return self._template_retriever

    def describe(self, request_time: Datetime) -> str:
        """describe: provides a textual description of the self period
        according to a given request_time (point of view).

        Args:
            request_time (Datetime): Point of view used for describing
                self.

        Returns:
            str: Textual description of self.
        """
        rqst_time = Datetime(request_time)
        if abs(self.begin_time - self.end_time) <= Timedelta(hours=24):
            begin_diff = Timedelta(self.begin_time - rqst_time.midnight).total_hours()
            if 0 <= begin_diff <= 31:
                key = [
                    1,
                    rqst_time.hour,
                    begin_diff,
                    Timedelta(self.end_time - rqst_time.midnight).total_hours(),
                ]
            else:
                key = [
                    0,
                    rqst_time.hour,
                    self.begin_time.hour,
                    Timedelta(self.end_time - self.begin_time.midnight).total_hours(),
                ]
            template = self.template_retriever.get(key)
            if "{day" in template:
                day_p1 = Datetime(self.begin_time + Timedelta(hours=24))
                day_p2 = Datetime(self.begin_time + Timedelta(hours=48))
                day_m1 = Datetime(self.begin_time - Timedelta(hours=24))
                template = template.format(
                    day=self.begin_time.describe_day(rqst_time),
                    day_p1=day_p1.describe_day(rqst_time),
                    day_p2=day_p2.describe_day(rqst_time),
                    day_m1=day_m1.describe_day(rqst_time),
                )
            return template

        begin_description = self.begin_time.describe(rqst_time)
        end_descripton = self.end_time.describe(rqst_time)

        if begin_description == end_descripton:
            return begin_description

        return DATES["literal_period"].format(
            date_1=begin_description, date_2=end_descripton
        )

    def __repr__(self):
        return f"Period(begin_time={self.begin_time}, end_time={self.end_time})"

    def __str__(self):
        return self.__repr__()

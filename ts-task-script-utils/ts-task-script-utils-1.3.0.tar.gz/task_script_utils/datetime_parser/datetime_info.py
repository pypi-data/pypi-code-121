import re
import json
from datetime import datetime as dt
from itertools import product
from typing import Optional, Tuple

import pendulum
from pendulum.locales.en import locale

# pylint: disable=C0401
from pydash.arrays import flatten

from .datetime_config import DatetimeConfig
from .tz_list import _all_abbreviated_tz_list
from .ts_datetime import TSDatetime
from .utils.parsing import _parse_with_formats
from .parser_exceptions import (
    DatetimeParserError,
    InvalidOffsetError,
    OffsetNotKnownError,
    InvalidDateError,
    InvalidTimeError,
    MultipleOffsetsError,
    AmbiguousDateError,
    MultipleTimesFoundError,
    InvalidYearError,
)


# pylint: disable=R0902
class DateTimeInfo:
    """DatetimeInfo acts as base class for ShortDatetimeInfo and
    LongDatetimeInfo. This class definer the parsing logic. _parse
    takes a list of matcher functions. Child class should define
    these matcher function.
    """

    def __init__(self, date_time_raw: str, config: DatetimeConfig):
        self.date_time_raw: str = date_time_raw
        self.config: DatetimeConfig = config

        self.am_or_pm: Optional[str] = None
        self.iana_tz: Optional[str] = None
        self.offset_: Optional[str] = None
        self.abbreviated_tz: Optional[str] = None
        self.day: Optional[str] = None
        self.month: Optional[str] = None
        self.year: Optional[str] = None
        self.hour: Optional[str] = None
        self.minutes: Optional[str] = None
        self.seconds: Optional[str] = None
        self.fractional_seconds: Optional[str] = None

        self.parsed_datetime: Optional[TSDatetime] = None
        self.parsed_datetime_format: Optional[str] = None

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def _parse(self, matchers):
        """Run every token in tokenized datetime string through
        each matcher function in matchers list.
        """
        _matchers = list(matchers)
        tokens = self._tokenize_datetime_string()
        for token in tokens:
            for func in _matchers:
                result = func(token)
                if result:
                    # It means result of func(token)
                    # has matched something and we don't
                    # need that matcher anymore. Hence
                    # remove it from the _matcher list
                    _matchers.remove(func)

    def _tokenize_datetime_string(self):
        """This method is used to pre-process the input string
        and return token list splitted by whitespace
        It performs following pre-processing:
        1. Replace the letter T if it is sandwiched between two digits
        """
        raw_dt = self.date_time_raw
        processed_dt = self._remove_T_between_two_digits(raw_dt)
        return processed_dt.split()

    @staticmethod
    # pylint: disable=C0103
    def _remove_T_between_two_digits(string: str):
        # Input =  2018-13-09T11:12:23.000-05:30
        # output = 2018-13-09 11:12:23.000-05:30
        char_list = list(string)
        for idx in range(len(char_list[1:-1])):
            if (
                char_list[idx - 1].isdigit()
                and char_list[idx] == "T"
                and char_list[idx + 1].isdigit()
            ):
                char_list[idx] = " "

        return "".join(char_list)

    @property
    def offset(self):
        """
        Return UTC offset that was found during parsing
        """
        if self.offset_:
            return self.offset_

        if self.abbreviated_tz:
            if self.abbreviated_tz not in self.config.tz_dict:
                raise OffsetNotKnownError(
                    f"Offset value not known for '{self.abbreviated_tz}'"
                )
            return self.config.tz_dict[self.abbreviated_tz]

        return None

    @property
    def datetime_stamp(self):
        """Created Datetime string from parsed raw input string.
        The format is YYYY-MM-DD hh:mm:ss and fractional seconds
        (upto 6 digit), AM/PM and utc offset are appended
        conditionally.

        Returns:
            str/None: A datetime string
        """
        if self.parsed_datetime:
            return self.parsed_datetime.isoformat()

        if (
            self.day
            and self.month
            and self.year
            and self.hour
            and self.minutes
            and self.seconds
        ):
            dt_str = f"{self.year}-{self.month}-{self.day}"
            dt_str += f" {self.hour}:{self.minutes}:{self.seconds}"
            if self.fractional_seconds:
                # This property along with dt_format is used to create
                # a datetime object. Since python datetime support 6 digits for
                # microseconds, therefore truncating fraction seconds to
                # 6 digits
                dt_str += f".{self.fractional_seconds[:6]}"

            if self.am_or_pm and int(self.hour) <= 12:
                dt_str += f" {self.am_or_pm.upper()}"

            if self.offset:
                dt_str += f" {self.offset}"
            if self.iana_tz:
                dt_str += f" {self.iana_tz}"

            return dt_str

        return None

    @property
    def datetime_format(self):
        """Build datetime format using pendulum tokens.
        This property along with `datetime_stamp` property can be used
        to parse date using `pendulum.from_format`.

        Returns:
            str: A datetime format build using pendulum formatting
            tokens. This string represent the datetime format for
            `datetime_stamp`
        """
        if self.parsed_datetime_format:
            return self.parsed_datetime_format

        if not self.datetime_stamp:
            return None

        day = "D" if len(self.day) == 1 else "DD"
        month = "M" if len(self.month) == 1 else "MM"
        year = "YYYY"

        if self.am_or_pm and int(self.hour) <= 12:
            hrs = "h" if len(self.hour) == 1 else "hh"
        else:
            hrs = "H" if len(self.hour) == 1 else "HH"
        mins = "m" if len(self.minutes) == 1 else "mm"
        seconds = "s" if len(self.seconds) == 1 else "ss"
        fmt = f"{year}-{month}-{day} {hrs}:{mins}:{seconds}"

        if self.fractional_seconds:
            # Pendulum support upto 6 fractional seconds
            fmt += "." + ("S" * len(self.fractional_seconds[:6]))
        if self.am_or_pm and int(self.hour) <= 12:
            fmt += " A"
        if self.offset:
            fmt += " Z"
        if self.iana_tz:
            fmt += " z"

        return fmt

    @property
    def datetime(self) -> TSDatetime:
        """Use parsing result to build TSDatetime object"""
        if self.parsed_datetime:
            return self.parsed_datetime

        if not self.datetime_format or not self.datetime_stamp:
            return None

        datetime_ = pendulum.from_format(
            self.datetime_stamp, self.datetime_format, tz=None
        )
        ts_datetime = TSDatetime(
            datetime_=datetime_, subseconds=self.fractional_seconds
        )
        return ts_datetime

    @datetime.setter
    def datetime(self, ts_datetime: TSDatetime):
        datetime_ = ts_datetime.datetime

        self.day = f"{int(datetime_.day):02d}"
        self.month = f"{int(datetime_.month):02d}"
        self.year = f"{int(datetime_.year):04d}"
        self.hour = f"{int(datetime_.hour):02d}"
        self.minute = f"{int(datetime_.minute):02d}"
        self.seconds = f"{int(datetime_.second):02d}"

        offset = datetime_.strftime("%z")
        if offset:
            sign = offset[0]
            val = offset[1:]
            self.offset_ = f"{sign}{val[:2]}:{val[2:]}"

        self.fractional_seconds = ts_datetime._subseconds
        self.parsed_datetime = ts_datetime


class LongDateTimeInfo(DateTimeInfo):
    """LongDatetimeInfo defines matchers:
    - `_match_day_of_week_token`
    - `_match_month_token`
    - `_match_day_token`
    - `_match_fractional_seconds`

    The idea is to detect which pendulum token should be used for
    building date format. The matchers detect the required tokens
    and `_build_long_date_format` return the resulting pendulum format
    for matching date.
    We then take a cartesian product of the date format with an
    exhaustive list of time formats built using `_build_time_formats`.
    This cartesian product returns a list of long datetime formats, which
    can be used to parse `date_time_raw` string if it is a valid long datetime
    string. This cartesian product is performed by `_build_long_datetime_formats_list`
    """

    def __init__(self, date_time_raw: str, config: DatetimeConfig):
        super().__init__(date_time_raw, config)

        self.token_day_of_week: Optional[str] = None
        self.token_day: Optional[str] = None
        self.token_month: Optional[str] = None
        self.has_fractional_seconds: Optional[str] = None

        self._parse_long_date_formats()

    def _parse_long_date_formats(self):
        matchers = [
            self._match_day_of_week_token,
            self._match_month_token,
            self._match_day_token,
            self._match_fractional_seconds,
        ]
        self._parse(matchers)
        if self.token_day is None:
            self.token_day = "DD"

        long_datetime_formats = self._build_long_datetime_formats_list()
        parsed_datetime, matched_format = _parse_with_formats(
            datetime_str=self.date_time_raw,
            config=self.config,
            formats=long_datetime_formats,
        )
        if parsed_datetime:
            self.datetime = parsed_datetime
            self.parsed_datetime_format = matched_format

    def _match_day_of_week_token(self, token: str) -> bool:
        days = locale.locale["translations"]["days"]
        token_map = {
            "dddd": days["wide"].values(),
            "ddd": days["abbreviated"].values(),
            "dd": days["short"].values(),
        }
        token = self._get_token(token, token_map)
        if token is not None:
            self.token_day_of_week = token
            return True
        return False

    def _match_month_token(self, date_time_token: str) -> bool:
        months = locale.locale["translations"]["months"]
        token_map = {
            "MMMM": months["wide"].values(),
            "MMM": months["abbreviated"].values(),
        }
        token = self._get_token(date_time_token, token_map)
        if token is not None:
            self.token_month = token
            return True
        return False

    def _match_day_token(self, date_time_token: str) -> bool:
        ordinals = ["st", "nd", "rd", "th"]
        token = None
        for val in ordinals:
            if date_time_token.endswith(val):
                token = "Do"
            elif date_time_token.endswith(f"{val},"):
                token = "Do,"
        if token is not None:
            self.token_day = token
            return True
        return False

    def _match_fractional_seconds(self, token):
        fraction_pattern = r"\d+\.\d+"
        matches = re.findall(fraction_pattern, token)
        if len(matches) == 1:
            match = matches[0]
            self.fractional_seconds = match.split(".")[1]
            return True
        return False

    @staticmethod
    def _get_token(token, token_map: dict):
        for key_, values in token_map.items():
            if token in values:
                return key_
            if token.replace(",", "") in values:
                return f"{key_},"
        return None

    def _build_long_date_format(self):
        """Use DatetimeInfo to build and return date format for
        long datetime string.

        Raises:
            InvalidDateError: Raised if parsing fails to
            detect tokens for month or day

        Returns:
            str: Return Date format built using pendulum
            formatting tokens
        """
        if not (self.token_month and self.token_day):
            raise InvalidDateError(f"{self.date_time_raw}")

        if self.token_day_of_week:
            date_fmt = (
                f"{self.token_day_of_week} "
                f"{self.token_month} "
                f"{self.token_day} "
                f"YYYY"
            )
        else:
            date_fmt = f"{self.token_month} {self.token_day} YYYY"
        return date_fmt

    def _build_time_formats(self):
        pendulum_time_tokens = [
            ["h", "hh", "H", "HH"],
            ["m", "mm"],
            ["s", "ss"],
        ]

        def map_am_pm(time_format):
            return time_format if time_format.startswith("H") else time_format + " A"

        time_formats = [":".join(tokens) for tokens in product(*pendulum_time_tokens)]
        if self.fractional_seconds:
            token = "SSSSSS"
            time_formats = map(lambda x: [x, f"{x}.{token}"], time_formats)

        time_formats = flatten(time_formats)
        time_formats = map(map_am_pm, time_formats)
        time_formats = map(
            lambda x: [
                x,
                x + " Z",
                x + " z",
                x + " ZZ",
                x + " Z z",
                x + " ZZ z",
                x + " z ZZ",
                x + " zz",
                x + " Z zz",
                x + " ZZ zz",
            ],
            time_formats,
        )
        time_formats = flatten(time_formats)
        return tuple(time_formats)

    def _build_long_datetime_formats_list(self) -> Tuple[str]:
        """Returns a list of long datetime formats built
        using pendulum formatting tokens.
        """
        parts = [
            [self._build_long_date_format()],
            self._build_time_formats(),
        ]
        formats = tuple(" ".join(values) for values in product(*parts))
        return formats


class ShortDateTimeInfo(DateTimeInfo):
    """ShortDateTime info defines matcher function for
    detecting date, time and timezone values
    """

    def __init__(self, date_time_raw: str, config: DatetimeConfig):
        super().__init__(date_time_raw, config)
        self._parse_short_date_formats()

    def _parse_short_date_formats(self):
        matchers = [
            self._match_iana_tz,
            self._match_time,
            self._match_short_date,
            self._match_am_or_pm,
            self._match_offset,
            self._match_tz_abbreviation,
        ]
        self._parse(matchers)

        # Add Validators here
        self._validate_meridiem()

    def _match_iana_tz(self, token: str) -> bool:
        """Match and set IANA timezone

        Args:
            token (str): A string value from `self.date_time_raw`
            when splitted by whitespace

        Returns:
            bool: Return True if iana_tz is matched else return False
        """
        if token in pendulum.timezones:
            self.iana_tz = token
            return True
        return False

    # pylint: disable=R0912
    def _match_time(self, token: str) -> bool:
        """Use Regex to find any time string present in
        input token. If time string is parsed successfully
        then set `self.hour`, `self.minutes`, `self.seconds`
        and `self.fractional_seconds`

        Args:
            token (str): A string value from `self.date_time_raw`
            when splitted by whitespace

        Raises:
            - MultipleTimesFoundError: When more than one time-string
            are matched
            - InvalidTimeError: When time like string is parsed, but the
            numeric value of hrs, minutes and seconds are out of bound.

        Returns:
            bool: Returns True if time is parsed successfully, else
            return False
        """
        # pylint: disable=C0301
        hh_mm_ss_pattern = r"\d{1,2}:\d{1,2}:\d{1,2}\.\d+|^\d{1,2}:\d{1,2}:\d{1,2}$|^\d{1,2}:\d{1,2}:\d{1,2}[+-]"  # noqa E501
        hh_mm_pattern = r"^(?![+-])\d{1,2}:\d{1,2}$|^(?![+-])\d{1,2}:\d{1,2}[+-]{1,1}"

        matches = re.findall(hh_mm_ss_pattern, token)
        if not matches:
            matches = re.findall(hh_mm_pattern, token)
            if not matches:
                return False

        if len(matches) > 1:
            raise MultipleTimesFoundError(f"Multiple Time values found: {matches}")

        time_ = matches[0].strip()
        if "+" in time_:
            time_ = time_.replace("+", "")
        if "-" in time_:
            time_ = time_.replace("-", "")
        time_ = time_.split(":")

        if len(time_) > 3:
            raise InvalidTimeError(matches[0])

        if len(time_) == 2:
            hour, minutes = time_
            seconds = "00"
        else:
            hour, minutes, seconds = time_

        if "." in seconds:
            seconds, fractional_seconds = seconds.split(".")
        else:
            fractional_seconds = None

        time_errors = []

        if not 0 <= int(hour) <= 24:
            time_errors.append(
                f"Invalid time : {hour}. Hours value must be between 0 and 24"
            )
        if not 0 <= int(minutes) <= 60:
            time_errors.append(
                f"Invalid time : {minutes}. Minutes value must be between 0 and 60"
            )
        if not 0 <= int(seconds) <= 60:
            time_errors.append(
                f"Invalid time : {seconds}. Seconds value must be between 0 and 60"
            )

        if time_errors:
            raise InvalidTimeError(
                f"Invalid time: {matches[0]}. {', '.join(time_errors)}"
            )

        self.hour = f"{int(hour):02d}"
        self.minutes = f"{int(minutes):02d}"
        self.seconds = f"{int(seconds):02d}"
        self.fractional_seconds = fractional_seconds
        return True

    def _match_short_date(self, token: str) -> bool:
        """Use Regex to find any short date string present in
        input token

        If a valid, non-ambiguous match is found, then it also sets
        `self.day`, `self.month` and `self.year`

        Args:
            token (str): A string value from `self.date_time_raw`
            when splitted by whitespace

        Returns:
            bool: Return True, if short date is parsed successfully.
        """
        year_first_pattern = r"(\d{4})[-./\\](\d{1,2})[-./\\](\d{1,2})"
        year_last_pattern = r"(\d{1,2})[-./\\](\d{1,2})[-./\\](\d{4})"
        two_digit_date_pattern = r"^(\d{1,2})[-./\\](\d{1,2})[-./\\](\d{1,2})"
        # no_sep_date_pattern = r"\d{6,6}"

        # YYYY-XX-XX
        year_first_matches = re.match(year_first_pattern, token)
        if year_first_matches:
            day, month, year = self._process_year_first_or_last_matches(
                year_first_matches.groups(), True
            )

            self._set_date(year, month, day)
            return True

        # XX-XX-YYYY
        year_last_matches = re.match(year_last_pattern, token)
        if year_last_matches:
            day, month, year = self._process_year_first_or_last_matches(
                year_last_matches.groups(), False
            )
            self._set_date(year, month, day)
            return True

        # Cases = [XX-XX-XX, XX-X-X, X-X-XX, X-X-X]
        two_digit_date_pattern_matches = re.match(two_digit_date_pattern, token)
        if two_digit_date_pattern_matches:
            day, month, year = self._process_two_digit_date_pattern(
                two_digit_date_pattern_matches.groups()
            )

            self._set_date(year, month, day)
            return True

        return False

    def _set_date(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def _match_offset(self, token: str) -> bool:
        """Use Regex to find if any utc offset value
        is present in input token
        If a match is found, set `self.offset_`

        Args:
            token (str): A string value from `self.date_time_raw`
            when splitted by whitespace

        Returns:
            bool: Return `True` if a valid offset value is matched
            else return False
        """
        # Can't parse 12-23-1223T11:12:23.000-05:30
        # offset with - sign, confuses with date separator
        # that why we need space 12-23-1223T11:12:23.000 -05:30
        patterns = [
            r"[Uu][Tt][Cc][+-]\d+",
            r"[+-]\d{1,2}:\d{1,2}",
            # r"[+-]\d{1}:\d{1}", # match this and fail later
            r"[+-]\d+",
        ]

        # if the token matched short date
        # then it is a date don't match for offset
        try:
            short_date = self._match_short_date(token)
        except DatetimeParserError:
            short_date = False

        if short_date:
            return False

        for pattern in patterns:
            matches = re.findall(pattern, token)
            if matches:
                if len(matches) != 1:
                    raise MultipleOffsetsError(f"Multiple offsets found: {matches}")
                match = matches[0].strip()
                if match.lower().startswith("utc"):
                    match = match[3:]
                sign, offset = match[0], match[1:]
                offset = self._pad_and_validate_time_offset_value(offset)
                if offset:
                    self.offset_ = f"{sign}{offset}"
                    return True
        return False

    def _match_am_or_pm(self, token: str) -> bool:
        """
        Use regex to check if input string contains
        AM or PM. Update `self.am_or_pm` and return True
        if a meridiem value is matched
        """
        pattern = r"[ap][m]$"
        matches = re.findall(pattern, token, flags=re.IGNORECASE)
        if not matches or len(matches) != 1:
            return False

        self.am_or_pm = matches[0].upper()
        return True

    def _match_tz_abbreviation(self, token: str) -> bool:
        """Check if the input token is an abbreviated timezone
        present in Datetime Config's tz_dict and if it is present,
        set `self.abbreviated_tz`

        Args:
            token (str): A string value from `self.date_time_raw`
            when splitted by whitespace

        Returns:
            bool: If abbreviated_tz is matched, return True.
        """
        if token.upper() in _all_abbreviated_tz_list:
            self.abbreviated_tz = token.upper()
            return True
        return False

    def _process_year_first_or_last_matches(self, date_parts, year_first):
        if year_first:
            year, others = date_parts[0], date_parts[1:]
        else:
            others, year = date_parts[:-1], date_parts[-1]

        if len(year) == 3:
            raise InvalidYearError(f"{date_parts} has invalid year.")

        if self.config.day_first is True:
            day, month = others
        elif self.config.day_first is False:
            month, day = others
        else:
            # if day_first is None
            if year_first:
                month, day = others[0], others[1]
                if int(month) > 12:
                    month, day = day, month
            else:
                day, month = self._disambiguate_day_and_month(*others)

        # Validate day, year, month
        try:
            dt(day=int(day), month=int(month), year=int(year))
        except ValueError as val_error:
            msg = f"{str(val_error)}, date={date_parts}, config={self.config}"
            raise InvalidDateError(msg)

        day = f"{int(day):02d}"
        month = f"{int(month):02d}"

        return day, month, year

    # pylint: disable=R0912
    def _process_two_digit_date_pattern(self, date_parts):
        if self.config.year_first is True:
            if self.config.day_first is True:
                # Input = YY-DD-MM
                year, day, month = date_parts
            elif self.config.day_first is False:
                # Input = YY-MM-DD
                year, month, day = date_parts
            else:
                # Input = YY-MM-DD
                year, month, day = date_parts
                if int(month) > 12:
                    month, day = day, month
                # At this point both month and day
                # could have improper values, eg day=42 and month=16
                # This is validated later below in this function.

        elif self.config.year_first is False:
            if self.config.day_first is True:
                # Input = DD-MM-YY
                day, month, year = date_parts
            elif self.config.day_first is False:
                # Input = MM-DD-YY
                month, day, year = date_parts
            else:
                # Input = XX-XX-YY
                date_str = "-".join([f"{int(token):02d}" for token in date_parts])
                day, month, year = self._try_formats(date_str, ("MM-DD-YY", "DD-MM-YY"))
        else:
            if self.config.day_first is True:
                # Input = DD-MM-YY
                day, month, year = date_parts
            elif self.config.day_first is False:
                # Could Be MM-DD-YY or YY-MM-DD
                date_str = "-".join([f"{int(token):02d}" for token in date_parts])
                day, month, year = self._try_formats(date_str, ("MM-DD-YY", "YY-MM-DD"))
            else:
                # Could Be MM-DD-YY or YY-MM-DD or DD-MM-YY
                date_str = "-".join([f"{int(token):02d}" for token in date_parts])
                day, month, year = self._try_formats(
                    date_str, ("MM-DD-YY", "YY-MM-DD", "DD-MM-YY")
                )

        if len(year) == 1:
            year = f"200{year}"
        elif len(year) == 2:
            year = f"20{year}"

        day = f"{int(day):02d}"
        month = f"{int(month):02d}"

        # Validate day, year, month
        try:
            dt(day=int(day), month=int(month), year=int(year))
        except ValueError as val_error:
            msg = f"{str(val_error)}, date={'-'.join(date_parts)}, {self.config}"
            raise InvalidDateError(msg)

        return day, month, year

    @staticmethod
    def _disambiguate_day_and_month(first_token: str, second_token: str) -> tuple:
        """Takes two tokens as input and tries to
        decide which token is day and which is month.

        Raises:
            AmbiguousDateError: When it fails to decide between day and month


        Returns:
            tuple: (day, month)
        """

        first_token_is_month = int(first_token) <= 12
        second_token_is_month = int(second_token) <= 12
        if (first_token_is_month and second_token_is_month) and (
            first_token == second_token
        ):
            return first_token, second_token

        if first_token_is_month and second_token_is_month:
            raise AmbiguousDateError(
                f"Can't decide day and month between: {first_token}, {second_token}"
            )

        if not first_token_is_month and not second_token_is_month:
            raise AmbiguousDateError(
                f"Can't decide day and month between: {first_token}, {second_token}"
            )

        day, month = (
            (first_token, second_token)
            if second_token_is_month
            else (second_token, first_token)
        )
        return day, month

    @staticmethod
    def _pad_and_validate_time_offset_value(offset: str) -> str:
        if ":" in offset:
            # 5:30 --> 05:30
            # 05:30 --> 05:30
            if len(offset) == 4:
                return f"0{offset}"
            if len(offset) == 5:
                return offset
            raise InvalidOffsetError(offset)

        # Else
        # 2 --> 02:00 | 09 --> 09:00 | 12 --> 12:00
        # 530 --> 05:30
        # 0930 --> 09:30 | 1200 --> 12:00
        if len(offset) == 1:
            return f"0{offset}:00"
        if len(offset) == 2:
            return f"{offset}:00"
        if len(offset) == 3:
            return f"0{offset[0]}:{offset[1:]}"
        if len(offset) == 4:
            return f"{offset[:2]}:{offset[2:]}"

        raise InvalidOffsetError(offset)

    @staticmethod
    def _is_format(date_str: str, format_: str):
        """Given a date string and a format,
        try to parse the date.

        Args:
            date_str (str): date string
            format (str): date format built using
            tokens used in `pendulum` library

        Returns:
            tuple: If date is parsed successfully return
            (True, datetime object) else return (False, None)
        """
        try:
            parsed = pendulum.from_format(date_str, format_)
            return parsed
        except ValueError:
            return None

    def _try_formats(self, date_str: str, formats: Tuple[str, ...]):
        """Given a date string and a list for formats, make sure
        only one of the format successfully parses the date.
        If multiple or no format parses the date, raise AmbiguousDateError
        Args:
            date_str (str): date string
            formats (List[str]): list of date format built using
            tokens used in `pendulum` library

        Raises:
            AmbiguousDateError: If multiple or no format parses the date,
            raise `AmbiguousDateError`

        Returns:
            tuple[str]: (day, month, year)
        """
        parsed_results = [
            (format_, self._is_format(date_str, format_)) for format_ in formats
        ]

        parsed_results = list(filter(lambda x: x[1] is not None, parsed_results))
        if len(parsed_results) != 1:
            raise AmbiguousDateError(
                f"Ambiguous date: {date_str}, possible formats: "
                f"{[parsed_result[0] for parsed_result in parsed_results]}."
            )
        result = parsed_results[0][1]
        return (str(result.day), str(result.month), str(result.year))

    def _validate_meridiem(self):
        if self.hour is None or self.am_or_pm is None:
            # Nothing to check.
            return

        if self.am_or_pm.upper() == "AM":
            if int(self.hour) > 12:
                raise InvalidTimeError(
                    f"Hour is {self.hour} but meridiem is {self.am_or_pm}"
                )

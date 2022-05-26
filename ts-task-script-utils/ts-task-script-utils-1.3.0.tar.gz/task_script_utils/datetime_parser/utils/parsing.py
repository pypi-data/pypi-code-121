from collections import Counter
from copy import copy
from re import error as re_error
from typing import Optional, Sequence, Tuple
import pendulum
from task_script_utils.datetime_parser.ts_datetime import TSDatetime
from task_script_utils.datetime_parser.utils.manipulation import (
    replace_z_with_offset,
    replace_abbreviated_tz_with_utc_offset,
    replace_zz_with_Z,
    from_pendulum_format,
)
from task_script_utils.datetime_parser.parser_exceptions import (
    DatetimeParserError,
    AmbiguousDatetimeFormatsError,
)
from task_script_utils.datetime_parser.datetime_config import (
    DEFAULT_DATETIME_CONFIG,
    DatetimeConfig,
)


def parse_with_formats(
    datetime_raw_str: str,
    formats: Sequence[str] = (),
    config: DatetimeConfig = DEFAULT_DATETIME_CONFIG,
) -> TSDatetime:
    """Parse datetime_str and construct a TSDatetime Object

    Args:
        datetime_raw_str (str): Raw datetime string
        formats (Sequence[str], optional): List of possible datetime
        formats. Defaults to empty tuple.
        These datetime formats must be built using `pendulum` datetime tokens.
        config (DatetimeConfig, optional): Datetime Configuration.
        Defaults to DEFAULT_DATETIME_CONFIG.

    Raises:
        DatetimeParserError: When datetime_str can be parsed into TSDatetime object
    Returns:
        TSDatetime
    """
    parsed_datetime = None

    # Parse Using formats list
    if formats:
        parsed_datetime, _ = _parse_with_formats(
            datetime_raw_str, formats=formats, config=config
        )

    if parsed_datetime is None:
        raise DatetimeParserError(f"Could not parse: {datetime_raw_str}")

    if not isinstance(parsed_datetime, TSDatetime):
        parsed_datetime = pendulum.instance(parsed_datetime)
        parsed_datetime = TSDatetime(datetime_=parsed_datetime)

    parsed_datetime.change_fold(config.fold)
    return parsed_datetime


def _parse_with_formats(
    datetime_str: str,
    formats: Sequence[str] = (),
    config: DatetimeConfig = DEFAULT_DATETIME_CONFIG,
) -> Tuple[Optional[TSDatetime], Optional[str]]:
    # If the input datetime string contains Z to denote UTC+0,
    # then Z is replaced by +00:00
    datetime_str = replace_z_with_offset(datetime_str)

    # If datetime config contains tz_dict, then replace
    # abbreviated_tz in datetime_str with its corresponding
    # utc offset values from datetime_config.tz_dict
    datetime_str_with_no_abbreviated_tz = replace_abbreviated_tz_with_utc_offset(
        datetime_str, config.tz_dict
    )
    updated_formats = copy(formats)
    if datetime_str_with_no_abbreviated_tz != datetime_str:
        # It means datetime_str did contain abbreviated_tz and we
        # have replaced it with its utc_offset value from tz_dict.
        # Now if the format in formats contains "zz", replace
        # it with "Z". This is because no library parses abbreviated tz
        # due to its ambiguous nature
        updated_formats = replace_zz_with_Z(updated_formats)

    if config.require_unambiguous_formats:
        parsed_times = []
        for idx, format_ in enumerate(updated_formats):
            try:
                parsed_times.append(
                    (
                        from_pendulum_format(
                            datetime_str_with_no_abbreviated_tz, format_, tz=None
                        ),
                        formats[idx],
                    )
                )
            except (ValueError, re_error):
                pass
        if not parsed_times:
            return None, None
        if len(parsed_times) == 1:
            return parsed_times[0]
        if len(parsed_times) > 1:
            unique_parsed_times = Counter(
                [parsed_time[0].isoformat() for parsed_time in parsed_times]
            )
            if len(Counter(unique_parsed_times).values()) > 1:
                raise AmbiguousDatetimeFormatsError(
                    "Ambiguity found between datetime formats: "
                    f"{[parsed_time[1] for parsed_time in parsed_times]}, the parsed"
                    f" datetimes {list(unique_parsed_times.keys())}, and the input"
                    f" datetime string '{datetime_str}'."
                )
            return parsed_times[0]

    for format_ in formats:
        try:
            parsed = from_pendulum_format(
                datetime_str_with_no_abbreviated_tz, format_, tz=None
            )
            return parsed, format_
        except (ValueError, re_error):
            pass
    return None, None

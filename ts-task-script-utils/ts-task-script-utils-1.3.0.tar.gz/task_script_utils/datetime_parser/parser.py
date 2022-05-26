from typing import Sequence

import pendulum
from task_script_utils.datetime_parser.parser_exceptions import (
    DatetimeParserError,
)
from task_script_utils.datetime_parser.ts_datetime import TSDatetime

from .datetime_config import DEFAULT_DATETIME_CONFIG, DatetimeConfig
from .datetime_info import ShortDateTimeInfo, LongDateTimeInfo
from .utils.parsing import _parse_with_formats
from .utils.manipulation import replace_z_with_offset


def parse(
    datetime_raw_str: str,
    formats: Sequence[str] = (),
    config: DatetimeConfig = DEFAULT_DATETIME_CONFIG,
) -> TSDatetime:
    """Parse datetime_str and construct a TSDatetime Object

    Args:
        datetime_raw_str (str): Raw datetime string
        formats (Sequence[str], optional): List of possible datetime
        formats. These datetime formats must be built using `pendulum` datetime tokens.
        Defaults to empty tuple.
        config (DatetimeConfig, optional): Datetime Configuration.
        Defaults to DEFAULT_DATETIME_CONFIG.

    Raises:
        DatetimeParserError: When datetime_str can be parsed into TSDatetime object
    Returns:
        TSDatetime
    """
    parsed_datetime = None
    datetime_info = None

    # If the input datetime string contains Z to denote UTC+0,
    # then Z is replaced by +00:00
    datetime_str = replace_z_with_offset(datetime_raw_str)
    # Parse Using formats list
    if formats:
        parsed_datetime, _ = _parse_with_formats(
            datetime_str, config=config, formats=formats
        )

    # Otherwise use DateInfo Parser to parse short dates
    if not parsed_datetime:
        datetime_info = ShortDateTimeInfo(datetime_str, config)
        parsed_datetime = datetime_info.datetime

    # Use long date formats
    if not parsed_datetime:
        datetime_info = LongDateTimeInfo(datetime_str, config)
        parsed_datetime = datetime_info.datetime

    if parsed_datetime is None:
        raise DatetimeParserError(f"Could not parse: {datetime_str}")

    if not isinstance(parsed_datetime, TSDatetime):
        parsed_datetime = pendulum.instance(parsed_datetime)
        parsed_datetime = TSDatetime(datetime_=parsed_datetime)

    parsed_datetime.change_fold(config.fold)
    return parsed_datetime

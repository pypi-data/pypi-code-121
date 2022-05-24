from datetime import datetime, timedelta
from typing import List, Dict, Union

from py_dot.core.lists import safe_insert
from py_dot.data.summary_time_unit import SummaryTimeUnit

def _get_frame_option(unit: SummaryTimeUnit):
    # todo
    if unit == SummaryTimeUnit.year:
        return (
            {'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0},
            {'days': 365},
            '%Y'
        )

    # todo
    if unit == SummaryTimeUnit.month:
        return (
            {'day': 1, 'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0},
            {'days': 30},
            '%Y-%m'
        )

    if unit == SummaryTimeUnit.date:
        return (
            {'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0},
            {'days': 1},
            '%Y-%m-%d'
        )

    if unit == SummaryTimeUnit.hour:
        return (
            {'minute': 0, 'second': 0, 'microsecond': 0},
            {'hours': 1},
            '%Y-%m-%d %H'
        )


def get_frame_from_series(
        series,
        begin: datetime,
        end: datetime,
        unit: SummaryTimeUnit,
        fill: any = 0,
        time_index=0,
        value_index=1,
        column_index=2,
        headers: list = None,
        value_headers: list = None,
        date_header: str = 'Date'
):
    row_map: Dict[str, List[Union[str, int]]] = {}

    replace_kwargs, timedelta_kwargs, strftime_fmt = _get_frame_option(unit)
    current_time = begin.replace(**replace_kwargs)
    last_time = end.replace(**replace_kwargs)
    amount = timedelta(**timedelta_kwargs)

    while current_time <= last_time:
        current_label = current_time.strftime(strftime_fmt)
        row_map[current_label] = [current_label]
        current_time += amount

    if headers or value_headers:
        headers = headers if headers is not None else [date_header, *value_headers]

        for item in series:
            current_label = item[time_index].strftime(strftime_fmt)
            column = item[column_index]

            if column in headers:
                safe_insert(
                    row_map[current_label],
                    headers.index(column),
                    item[value_index],
                    fill
                )
    else:
        headers = [date_header]

        for item in series:
            current_label = item[time_index].strftime(strftime_fmt)
            column = item[column_index]

            if column not in headers:
                headers.append(column)

            safe_insert(
                row_map[current_label],
                headers.index(column),
                item[value_index],
                fill
            )

    # fill the null to zero
    rows = list(row_map.values())
    header_length = len(headers)
    for row in rows:
        diff = header_length - len(row)
        while diff > 0:
            row.append(fill)
            diff -= 1

    frame = [headers]
    frame.extend(rows)

    return frame

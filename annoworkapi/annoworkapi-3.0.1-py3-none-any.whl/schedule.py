from __future__ import annotations

import datetime
from typing import Any, Dict, Generator, Tuple

from annoworkapi.enums import ScheduleType

_ExpectedWorkingHoursDict = Dict[Tuple[str, str], float]
"""keyがtuple(date, workspace_member_id), valueが予定稼働時間のdict
"""


def _date_range(start_date: str, end_date: str) -> Generator[str, None, None]:
    dt_start_date = datetime.datetime.fromisoformat(start_date)
    dt_end_date = datetime.datetime.fromisoformat(end_date)

    dt_date = dt_start_date
    while dt_date <= dt_end_date:
        yield str(dt_date.date())
        dt_date += datetime.timedelta(days=1)


def create_schedules_daily(
    schedule: dict[str, Any], expected_working_hours_dict: _ExpectedWorkingHoursDict
) -> list[dict[str, Any]]:
    """作業計画情報から、日ごとのアサイン時間が格納されたlistを生成します。

    Args:
        schedule: 作業計画情報
        expected_working_hours_dict: 予定稼働時間のdict.予定稼働時間の比率でアサインされている場合、予定稼働時間を参照します。
            keyが(date,workspace_member_id), valueが予定稼働時間

    Returns:
        日ごとのアサイン時間情報のlist。１つの要素には以下のキーが格納されています。
        * date
        * job_id
        * workspace_member_id
        * assigned_working_hours

    """
    start_date = schedule["start_date"]
    end_date = schedule["end_date"]
    result = []
    if schedule["type"] == ScheduleType.HOURS.value:
        for date in _date_range(start_date, end_date):
            result.append(
                {
                    "date": date,
                    "job_id": schedule["job_id"],
                    "workspace_member_id": schedule["workspace_member_id"],
                    "assigned_working_hours": schedule["value"],
                }
            )

    elif schedule["type"] == ScheduleType.PERCENTAGE.value:
        # 予定稼働時間の比率からアサインされた時間を算出する。
        for date in _date_range(start_date, end_date):
            expected_working_hours = expected_working_hours_dict.get((date, schedule["workspace_member_id"]), 0)
            assigned_working_hours = expected_working_hours * schedule["value"] * 0.01
            # アサイン時間が0の情報は不要なので、結果情報に格納しない
            if assigned_working_hours > 0:
                result.append(
                    {
                        "date": date,
                        "job_id": schedule["job_id"],
                        "workspace_member_id": schedule["workspace_member_id"],
                        "assigned_working_hours": assigned_working_hours,
                    }
                )

    return result

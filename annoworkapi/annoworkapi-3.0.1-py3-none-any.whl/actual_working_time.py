"""
実績作業時間に関するutil関数を定義しています。
"""
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple

from annoworkapi.utils import datetime_to_str, str_to_datetime

_ActualWorkingHoursDict = Dict[Tuple[datetime.date, str, str], float]
"""実績作業時間の日ごとの情報を格納する辞書
key: (date, workspace_member_id, job_id), value: 実績作業時間
"""


def get_term_start_end_from_date_for_actual_working_time(
    start_date: Optional[str], end_date: Optional[str], tzinfo: Optional[datetime.tzinfo] = None
) -> tuple[Optional[str], Optional[str]]:
    """開始日と終了日から、実績作業時間を取得するAPIに渡すクエリパラメタterm_startとterm_endを返します。

    Args:
        start_date: 開始日
        end_date: 終了日
        tzinfo: 指定した日付のタイムゾーン。Noneの場合は、システムのタイムゾーンとみなします。

    Notes:
        WebAPIの絞り込み条件が正しくない恐れがあります。

    Returns:
        実績作業時間を取得するAPIに渡すterm_startとterm_end
    """
    if tzinfo is None:
        # システムのタイムゾーンを利用する
        tzinfo = datetime.datetime.now().astimezone().tzinfo

    term_start: Optional[str] = None
    if start_date is not None:
        dt_local_start_date = datetime.datetime.fromisoformat(start_date).replace(tzinfo=tzinfo)
        term_start = datetime_to_str(dt_local_start_date)

    term_end: Optional[str] = None
    if end_date is not None:
        dt_local_end_date = datetime.datetime.fromisoformat(end_date).replace(tzinfo=tzinfo)
        # end_date="2021-01-02"なら term_endは "2021-01-01T23:59:59.999"になるようにする
        # WARNING: WebAPIの都合。将来的に変わる恐れがある
        tmp = dt_local_end_date + datetime.timedelta(days=1) - datetime.timedelta(microseconds=1000)
        term_end = datetime_to_str(tmp)

    return term_start, term_end


def _create_actual_working_hours_dict(actual: dict[str, Any], tzinfo: datetime.tzinfo) -> _ActualWorkingHoursDict:
    results_dict: _ActualWorkingHoursDict = {}

    dt_local_start_datetime = str_to_datetime(actual["start_datetime"]).astimezone(tzinfo)
    dt_local_end_datetime = str_to_datetime(actual["end_datetime"]).astimezone(tzinfo)

    workspace_member_id = actual["workspace_member_id"]
    job_id = actual["job_id"]

    if dt_local_start_datetime.date() == dt_local_end_datetime.date():
        actual_working_hours = (dt_local_end_datetime - dt_local_start_datetime).total_seconds() / 3600
        results_dict[(dt_local_start_datetime.date(), workspace_member_id, job_id)] = actual_working_hours
    else:
        dt_tmp_local_start_datetime = dt_local_start_datetime

        # 実績作業時間が24時間を超えることはないが、24時間を超えても計算できるような処理にする
        while dt_tmp_local_start_datetime.date() < dt_local_end_datetime.date():
            dt_next_date = dt_tmp_local_start_datetime.date() + datetime.timedelta(days=1)
            dt_tmp_local_end_datetime = datetime.datetime(
                year=dt_next_date.year, month=dt_next_date.month, day=dt_next_date.day, tzinfo=tzinfo
            )
            actual_working_hours = (dt_tmp_local_end_datetime - dt_tmp_local_start_datetime).total_seconds() / 3600
            results_dict[(dt_tmp_local_start_datetime.date(), workspace_member_id, job_id)] = actual_working_hours
            dt_tmp_local_start_datetime = dt_tmp_local_end_datetime

        actual_working_hours = (dt_local_end_datetime - dt_tmp_local_start_datetime).total_seconds() / 3600
        results_dict[(dt_local_end_datetime.date(), workspace_member_id, job_id)] = actual_working_hours

    return results_dict


def create_actual_working_times_daily(
    actual_working_times: list[dict[str, Any]], tzinfo: Optional[datetime.tzinfo] = None
) -> list[dict[str, Any]]:
    """`getActualWorkingTimes` APIなどで取得した実績時間のlistから、日付、ジョブ、メンバ単位で集計した実績時間を生成します。

    Args:
        actual_working_times: `getActualWorkingTimes` APIなどで取得した実績時間のlist
        tzinfo: 日付を決めるためのタイムゾーン。未指定の場合はシステムのタイムゾーンを参照します。

    Returns:
        日付、ジョブ、メンバ単位で集計した実績時間のlistを返します。listの要素はdictで以下のキーを持ちます。
         * date
         * job_id
         * workspace_member_id
         * actual_working_hours
    """
    results_dict: _ActualWorkingHoursDict = defaultdict(float)

    tmp_tzinfo = tzinfo if tzinfo is not None else datetime.datetime.now().astimezone().tzinfo
    assert tmp_tzinfo is not None

    for actual in actual_working_times:
        tmp_results = _create_actual_working_hours_dict(actual, tzinfo=tmp_tzinfo)

        for key, value in tmp_results.items():
            results_dict[key] += value

    results_list: list[dict[str, Any]] = []
    for (date, workspace_member_id, job_id), actual_working_hours in results_dict.items():
        # 実績作業時間が0の情報は不要なので、結果情報に格納しない
        if actual_working_hours > 0:
            results_list.append(
                dict(
                    date=str(date),
                    workspace_member_id=workspace_member_id,
                    job_id=job_id,
                    actual_working_hours=actual_working_hours,
                )
            )

    return results_list

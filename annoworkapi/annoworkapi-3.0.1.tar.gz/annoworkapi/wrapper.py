from __future__ import annotations

import datetime
import logging
from collections import defaultdict
from typing import Any, Optional

from annoworkapi.actual_working_time import (
    create_actual_working_times_daily,
    get_term_start_end_from_date_for_actual_working_time,
)
from annoworkapi.api import AnnoworkApi, allow_404_error
from annoworkapi.schedule import _ExpectedWorkingHoursDict, create_schedules_daily

logger = logging.getLogger(__name__)


def _filter_actual_working_times_daily(
    actual_daily_list: list[dict[str, Any]], term_start_date: Optional[str], term_end_date: Optional[str]
):
    if term_start_date is None and term_end_date is None:
        return actual_daily_list

    def is_match(elm: dict[str, Any]) -> bool:
        result = True
        if term_start_date is not None:
            result = result and elm["date"] >= term_start_date
        if term_end_date is not None:
            result = result and elm["date"] <= term_end_date
        return result

    return [e for e in actual_daily_list if is_match(e)]


class Wrapper:
    """
    AnnoWorkApiのラッパー.

    Args:
        api: AnnoworkApi Instance
    """

    def __init__(self, api: AnnoworkApi):
        self.api = api

    ###################################################################################################################
    # Account
    ###################################################################################################################
    @allow_404_error(logger=logger)
    def get_account_external_linkage_info_or_none(self, user_id: str) -> Optional[dict[str, Any]]:
        return self.api.get_account_external_linkage_info(user_id, log_response_with_error=False)

    def get_annofab_account_id_from_user_id(self, user_id: str) -> Optional[str]:
        info = self.get_account_external_linkage_info_or_none(user_id)
        if info is None:
            return None

        if "annofab" not in info["external_linkage_info"]:
            return None
        return info["external_linkage_info"]["annofab"].get("account_id")

    @allow_404_error(logger=logger)
    def get_workspace_or_none(self, workspace_id: str) -> Optional[dict[str, Any]]:
        return self.api.get_workspace(workspace_id, log_response_with_error=False)

    @allow_404_error(logger=logger)
    def get_workspace_tag_or_none(self, workspace_id: str, workspace_tag_id: str) -> Optional[dict[str, Any]]:
        return self.api.get_workspace_tag(workspace_id, workspace_tag_id, log_response_with_error=False)

    @allow_404_error(logger=logger)
    def get_job_or_none(self, workspace_id: str, job_id: str) -> Optional[dict[str, Any]]:
        return self.api.get_job(workspace_id, job_id, log_response_with_error=False)

    @allow_404_error(logger=logger)
    def get_job_children_or_none(self, workspace_id: str, job_id: str) -> Optional[list[dict[str, Any]]]:
        return self.api.get_job_children(workspace_id, job_id, log_response_with_error=False)

    @allow_404_error(logger=logger)
    def get_workspace_member_or_none(self, workspace_id: str, workspace_member_id: str) -> Optional[dict[str, Any]]:
        return self.api.get_workspace_member(workspace_id, workspace_member_id, log_response_with_error=False)

    ###################################################################################################################
    # actual_working_time
    ###################################################################################################################
    def get_actual_working_times_daily(
        self,
        workspace_id: str,
        *,
        job_id: Optional[str] = None,
        term_start_date: Optional[str] = None,
        term_end_date: Optional[str] = None,
        tzinfo: Optional[datetime.tzinfo] = None,
    ) -> list[dict[str, Any]]:
        """ワークスペース全体の実績時間を一括取得します。実績時間は日、ジョブ、メンバ単位で集計されています。

        Args:
            workspace_id (str):  ワークスペースID (required)
            job_id (str):  ジョブIDで絞り込みます。
            term_start_date (str): 検索範囲の開始日（YYYY-MM-DD）
            term_end_date (str):  検索範囲の終了日（YYYY-MM-DD）
            tzinfo: 日付を決めるためのタイムゾーン。未指定の場合はシステムのタイムゾーンを参照します。

        Returns:
            日付、ジョブ、メンバ単位で集計した実績時間のlistを返します。listの要素はdictで以下のキーを持ちます。
            * date
            * job_id
            * workspace_member_id
            * actual_working_hours

        """
        term_start, term_end = get_term_start_end_from_date_for_actual_working_time(
            term_start_date, term_end_date, tzinfo=tzinfo
        )
        query_params = {
            "job_id": job_id,
            "term_start": term_start,
            "term_end": term_end,
        }
        tmp = self.api.get_actual_working_times(workspace_id, query_params=query_params)
        daily_list = create_actual_working_times_daily(tmp, tzinfo=tzinfo)
        return _filter_actual_working_times_daily(
            daily_list, term_start_date=term_start_date, term_end_date=term_end_date
        )

    def get_actual_working_times_by_workspace_member_daily(
        self,
        workspace_id: str,
        workspace_member_id: str,
        *,
        term_start_date: Optional[str] = None,
        term_end_date: Optional[str] = None,
        tzinfo: Optional[datetime.tzinfo] = None,
    ) -> Any:
        """ワークスペースメンバーに対する実績時間を一括取得します。実績時間は日、ジョブ、メンバ単位で集計されています。


        Args:
            workspace_id (str):  ワークスペースID (required)
            workspace_member_id (str):  ワークスペースメンバーID (required)
            term_start_date (str): 検索範囲の開始日（YYYY-MM-DD）
            term_end_date (str):  検索範囲の終了日（YYYY-MM-DD）
            tzinfo: 日付を決めるためのタイムゾーン。未指定の場合はシステムのタイムゾーンを参照します。

        Returns:
            日付、ジョブ、メンバ単位で集計した実績時間のlistを返します。listの要素はdictで以下のキーを持ちます。
            * date
            * job_id
            * workspace_member_id
            * actual_working_hours

        """
        term_start, term_end = get_term_start_end_from_date_for_actual_working_time(
            term_start_date, term_end_date, tzinfo=tzinfo
        )
        query_params = {
            "term_start": term_start,
            "term_end": term_end,
        }
        tmp = self.api.get_actual_working_times_by_workspace_member(
            workspace_id, workspace_member_id, query_params=query_params
        )
        daily_list = create_actual_working_times_daily(tmp, tzinfo=tzinfo)
        return _filter_actual_working_times_daily(
            daily_list, term_start_date=term_start_date, term_end_date=term_end_date
        )

    ###################################################################################################################
    # schedule
    ###################################################################################################################

    def get_schedules_daily(
        self,
        workspace_id: str,
        *,
        term_start: Optional[str] = None,
        term_end: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """日、ジョブ、メンバ単位のアサイン時間を取得します。

        Notes:
            内部で `api.get_expected_working_times` を実行します。

        Args:
            workspace_id: ワークスペースID
            term_start_date (str): 検索範囲の開始日（YYYY-MM-DD）
            term_end_date (str):  検索範囲の終了日（YYYY-MM-DD）
            job_id (str): 検索対象のジョブID

        Returns:
            日、ジョブ、メンバ単位のアサイン時間のlist。listの要素は以下のキーを持ちます。
            * date
            * job_id
            * workspace_member_id
            * assigned_working_hours
        """

        def _get_min_max_date(s_list: list[dict[str, Any]]) -> tuple[str, str]:
            min_date = "9999-99-99"
            max_date = "0000-00-00"
            for schedule in s_list:
                min_date = min(min_date, schedule["start_date"])
                max_date = max(max_date, schedule["end_date"])
            return min_date, max_date

        schedule_list = self.api.get_schedules(
            workspace_id, query_params={"job_id": job_id, "term_start": term_start, "term_end": term_end}
        )

        if len(schedule_list) == 0:
            return []

        min_date, max_date = _get_min_max_date(schedule_list)
        expected_working_times = self.api.get_expected_working_times(
            workspace_id, query_params={"term_start": min_date, "term_end": max_date}
        )
        expected_working_hours_dict: _ExpectedWorkingHoursDict = {
            (e["date"], e["workspace_member_id"]): e["expected_working_hours"]
            for e in expected_working_times
            if e["expected_working_hours"] > 0
        }

        result_dict: dict[tuple[str, str, str], float] = defaultdict(float)

        for schedule in schedule_list:
            schedules_daily = create_schedules_daily(schedule, expected_working_hours_dict)
            for elm in schedules_daily:
                result_dict[(elm["date"], elm["workspace_member_id"], elm["job_id"])] += elm["assigned_working_hours"]

        result_list = []
        for (date, tmp_workspace_member_id, tmp_job_id), assigned_working_hours in result_dict.items():
            if assigned_working_hours == 0:
                # アサイン時間が0の情報は不要なので、出力しないようにする
                continue

            if term_start is not None and not date >= term_start:
                continue
            if term_end is not None and not date <= term_end:
                continue

            result_list.append(
                dict(
                    date=date,
                    workspace_member_id=tmp_workspace_member_id,
                    job_id=tmp_job_id,
                    assigned_working_hours=assigned_working_hours,
                )
            )

        return result_list

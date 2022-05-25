import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class StatisticsHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_stats_lastvote(self):
        """Returns last vote."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/stats/lastVote")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Last Vote", r)

        return content, r

    def get_stats_response_count_for_factor(
        self,
        factor: int,
        start_date: str,
        end_date: str,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns the number of responses per responseId for one factor."""

        content = {}
        params = {
            "factorId": factor,
            "dateFrom": start_date,
            "dateTo": end_date,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/stats/responseCountForFactor", params=params
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Count For Factor", r)

        return content, r

    def get_stats_days(
        self,
        factor: int,
        start_date: str,
        end_date: str,
        period: bool,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statistics by day (and by period or not)."""

        content = {}
        params = {
            "factorId": factor,
            "dateFrom": start_date,
            "dateTo": end_date,
            "period": period,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(f"{ConfigHelper.host}/stats/days", params=params)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Days", r)

        return content, r

    def get_stats_months(
        self,
        factor: int,
        start_date: str,
        end_date: str,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statsitics by month (and by period)."""

        content = {}
        params = {
            "factorId": factor,
            "dateFrom": start_date,
            "dateTo": end_date,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(f"{ConfigHelper.host}/stats/months", params=params)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Months", r)

        return content, r

    def get_stats_season(
        self,
        factor: int,
        start_date: str,
        end_date: str,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statistics by season."""

        content = {}
        params = {
            "factorId": factor,
            "dateFrom": start_date,
            "dateTo": end_date,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(f"{ConfigHelper.host}/stats/seasons", params=params)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Seasons", r)

        return content, r

    def get_stats_themes_by_votes(
        self,
        start_date: str,
        end_date: str,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns the themes ordered by the number of votes (descending)."""

        content = {}
        params = {
            "dateFrom": start_date,
            "dateTo": end_date,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/stats/sortedByNbVotes", params=params
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Seasons", r)

        return content, r

    def get_stats_themes_by_feeling(
        self,
        start_date: str,
        end_date: str,
        room_id: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns themes ordered by the average of the resonses (i.e. satisfaction)."""

        content = {}
        params = {
            "dateFrom": start_date,
            "dateTo": end_date,
        }
        if room_id:
            params["roomId"] = room_id
        if group:
            params["groupId"] = group

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/stats/sortedByFeeling", params=params
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Seasons", r)

        return content, r

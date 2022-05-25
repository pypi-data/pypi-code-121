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
        raise NotImplementedError("Not implemented yet")

    def get_stats_response_count_for_factor(
        self,
        factor: int,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns the number of responses per responseId for one factor."""

        raise NotImplementedError("Not implemented yet")

    def get_stats_days(
        self,
        factor: int,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statistics by day (and by period or not)."""
        raise NotImplementedError("Not implemented yet")

    def get_stats_months(
        self,
        factor: int,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statsitics by month (and by period)."""
        raise NotImplementedError("Not implemented yet")

    def get_stats_season(
        self,
        factor: int,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns statistics by season."""
        raise NotImplementedError("Not implemented yet")

    def get_stats_themes_by_votes(
        self,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns the themes ordered by the number of votes (descending)."""
        raise NotImplementedError("Not implemented yet")

    def get_stats_themes_by_feeling(
        self,
        startdate: str,
        enddate: str,
        roomId: int = None,
        group: int or list[int] = None,
    ) -> Tuple[dict, Response]:
        """Returns themes ordered by the average of the resonses (i.e. satisfaction)."""
        raise NotImplementedError("Not implemented yet")

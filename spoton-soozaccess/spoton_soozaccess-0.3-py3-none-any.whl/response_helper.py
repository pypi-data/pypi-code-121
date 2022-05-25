from typing import Tuple
import json
from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class ResponseHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_responses(self) -> Tuple[dict, Response]:
        """Get all responses of the user for today."""
        content = {}
        try:
            r = self.session.get(f"{ConfigHelper.host}/oneshot/responses")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Responses", r)

        return content, r

    def get_all_responses(self, since: str, to: str) -> Tuple[dict, Response]:
        """Get all responses of the user for a specific period of time."""

        content = {}

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/oneshot/allresponses/since/{since}/to/{to}"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get All Responses", r)

        return content, r

    def get_factor_responses(self, theme: int, factor: int) -> Tuple[dict, Response]:
        """Get the responses of the user for today to this factor and for the given period."""

        content = {}

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/themes/{theme}/factors/{factor}/responses"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Factor Responses", r)

        return content, r

    def put_response(
        self, theme: int, factor: int, value: int, date: str
    ) -> Tuple[dict, Response]:
        """Insert the current response of the user for this factor. Key on the columns (userId, factorId, date, period). If date is not specified, it is set to today."""
        content = {
            "responseOptionId": value,
            "roomId": None,
            "period": "day",
            "date": date,
        }

        try:
            r = self.session.put(
                f"{ConfigHelper.host}/themes/{theme}/factors/{factor}/responses",
                json=content,
            )
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Put Response", r)

        return content, r

    def delete_response(
        self, theme: int, factor: int, response: int
    ) -> Tuple[dict, Response]:
        """Delete the given response."""

        try:
            r = self.session.delete(
                f"{ConfigHelper.host}/themes/{theme}/factors/{factor}/responses/{response}"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Delete Response", r)

        return {}, r

    def get_all_themes_responses(self) -> Tuple[dict, Response]:
        """Get responses of today to all themes for the user."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes/responses")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get All Themes Responses", r)

        return content, r

    def get_theme_responses(self, theme: int) -> Tuple[dict, Response]:
        """Get todays response of the user for given theme (only used for the environment category question)."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes/{theme}/responses")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get All Themes Responses", r)

        return content, r

    def put_theme_response(self, theme: int) -> Tuple[dict, Response]:
        """Update the crrent response of the user. Key on the columns (userId, themeId, period, date)."""
        raise NotImplementedError("Not implemented yet")

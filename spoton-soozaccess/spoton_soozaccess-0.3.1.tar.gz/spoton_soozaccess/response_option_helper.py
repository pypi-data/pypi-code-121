import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class ResponseOptionHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_oneshot(self) -> Tuple[dict, Response]:
        """Gets the whole survey catalogue (themes, factors, responseOptions) of an enterprise."""
        content = {}
        try:
            r = self.session.get(f"{ConfigHelper.host}/oneshot")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    One Shot", r)

        return content, r

    def get_factor_response_options(
        self, theme: int, factor: int
    ) -> Tuple[dict, Response]:
        """Get all possible responses for a particular factor."""

        content = {}

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/themes/{theme}/factors/{factor}/responseOptions"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Factor Response Options", r)

        return content, r

    def get_theme_response_options(self, theme: int) -> Tuple[dict, Response]:
        """Get the responseOptions to the quetsion of a theme."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes/{theme}/responseOptions")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Theme Response Options", r)

        return content, r

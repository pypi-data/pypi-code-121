import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class ThemeHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_themes(self) -> Tuple[dict, Response]:
        """Get all themes (not specific to an enterprise)."""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Themes", r)

        return content, r

    def get_theme(self, theme: int) -> Tuple[dict, Response]:
        """Get a specific theme."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes/{theme}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Theme", r)

        return content, r

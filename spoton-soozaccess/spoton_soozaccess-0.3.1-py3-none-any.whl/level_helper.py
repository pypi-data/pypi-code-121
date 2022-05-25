import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class LevelHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_levels(self) -> Tuple[dict, Response]:
        """Return the current level of the user for gamification. The points are increased by 25 with each PUT to the themes-responses endpoint."""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/levels")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Levels", r)

        return content, r

import json
from typing import Tuple
from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class FactorHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_factors(self, theme: int) -> Tuple[dict, Response]:
        """Get all factors for a theme (not specific to an enterprise)."""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/themes/{theme}/factors")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Factor", r)

        return content, r

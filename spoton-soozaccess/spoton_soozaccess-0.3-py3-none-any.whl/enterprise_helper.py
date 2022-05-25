import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class EnterpriseHelper:
    def __init__(self, session: Session):
        self.session = session

    def post_enterprise(self, name: str) -> Tuple[dict, Response]:
        """Create an enterprise."""

        content = {"name": name}

        try:
            r = self.session.post(f"{ConfigHelper.host}/enterprises", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Post Enterprise", r)

        return content, r

    def get_enterprise_factors(self, enterprise_id: int) -> Tuple[dict, Response]:
        """Get all factors with selected factors of an enterprise."""

        content = {}

        try:
            r = self.session.get(
                f"{ConfigHelper.host}/enterprises/{enterprise_id}/factors"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Enterprise Factors", r)

        return content, r

    def put_entreprise_factors(self, enterprise: int) -> Tuple[dict, Response]:
        """Purge and recreate selected factors of an enterprise."""
        raise NotImplementedError("Not implemented yet")

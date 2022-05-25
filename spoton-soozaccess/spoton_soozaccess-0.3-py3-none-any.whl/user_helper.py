import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class UserHelper:
    def __init__(self, session: Session, name: str, token: str):
        self.session = session
        self.name = name
        self.token = token

    def post_user(self, entreprise_id: int = 1) -> Tuple[dict, Response]:
        """Create a user."""
        content = {
            "firstName": self.name,
            "lastName": self.name,
            "sex": "m",
            "username": self.name,
            "email": f"{self.name}@test",
            "enterpriseId": entreprise_id,
            "token": self.token,
            "activatePopup": True,
            "points": 0,
        }
        try:
            r = self.session.post(f"{ConfigHelper.host}/users", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Create User", r)

        return content, r

    def put_user(self) -> Tuple[dict, Response]:
        """Update the connected user."""
        raise NotImplementedError("Not implemented yet")

    def login(self) -> Tuple[dict, Response]:
        """Login a user."""
        content = {"user": {"identifier": self.name, "token": self.token}}

        try:
            r = self.session.post(f"{ConfigHelper.host}/users/login", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status(f"*{self.name}* Login", r)

        return content, r

    def logout(self) -> Tuple[dict, Response]:
        """Logout the connected user."""
        try:
            r = self.session.post(f"{ConfigHelper.host}/users/logout")
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status(f"*{self.name}* Logout", r)

        return {}, r

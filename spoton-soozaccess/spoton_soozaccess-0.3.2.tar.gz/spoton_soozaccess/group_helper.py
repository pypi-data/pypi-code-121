from typing import Tuple
import json
from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper
from .logger import Logger


class GroupHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_user_groups(self) -> Tuple[dict, Response]:
        """Returns all groups of a user."""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/groups")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Groups", r)

        return content, r

    def post_group(self, name: str, description: str) -> Tuple[dict, Response]:
        """Create a group in the enterprise of the user."""
        if name in [g["group"]["name"] for g in self.get_user_groups()[0]]:
            Logger.write("Group already exists")
            return None, None

        content = {"name": name, "description": description}

        try:
            r = self.session.post(f"{ConfigHelper.host}/groups", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Insert Group", r)

        return content, r

    def put_group(
        self, group: int, name: str, description: str
    ) -> Tuple[dict, Response]:
        """Update a group (requires the user to be admin of the group)."""

        content = {
            "name": name,
            "description": description,
        }

        try:
            r = self.session.put(f"{ConfigHelper.host}/groups/{group}", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Put Group", r)

        return {}, r

    def delete_group(self, group: int) -> Tuple[dict, Response]:
        """Delete a group (requires the user to be admin of the group)."""
        if group not in [g["group"]["id"] for g in self.get_user_groups()[0]]:
            Logger.write("Group does not exist")
            return None

        try:
            r = self.session.delete(f"{ConfigHelper.host}/groups/{group}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Remove Group", r)

        return {}, r

    def remove_groups(self):
        for g in self.get_user_groups()[0]:
            self.delete_group(g["group"]["id"])

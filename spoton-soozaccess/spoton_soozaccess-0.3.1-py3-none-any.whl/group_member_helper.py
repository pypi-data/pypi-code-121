from typing import Tuple
import json
from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class GroupMemberHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_invitable_users(self, group: int) -> Tuple[dict, Response]:
        """Return users that can be invited to a group."""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/groups/{group}/invitableUsers")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Invitable Users", r)

        return content, r

    def post_group_invite(self, group: int, ids: list[int]) -> Tuple[dict, Response]:
        """Invite users to a specific group."""
        content = {"userIds": ids}

        try:
            r = self.session.post(
                f"{ConfigHelper.host}/groups/{group}/invite", json=content
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Invite to Group", r)

        return content, r

    def put_group_invitation(
        self, group: int, status: str = "accepted"
    ) -> Tuple[dict, Response]:
        """Accept/decline an invitation to join a group."""

        content = {"status": status}

        try:
            r = self.session.put(
                f"{ConfigHelper.host}/groups/{group}/invitation",
                json=content,
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Accept Group Invitation", r)

        return {}, r

    def get_group_members(self, id: int) -> Tuple[dict, Response]:
        """Return members of a group."""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/groups/{id}/members")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Groups Members", r)

        return content, r

    def delete_group_member(self, group: int, user: int) -> Tuple[dict, Response]:
        """Remove a user from a group."""

        content = {}

        try:
            r = self.session.delete(
                f"{ConfigHelper.host}/groups/{group}/members/{user}"
            )
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Groups", r)

        return content, r

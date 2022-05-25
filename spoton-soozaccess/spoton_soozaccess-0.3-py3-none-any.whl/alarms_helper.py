import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class AlarmsHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_alarms(self, id: str) -> Tuple[dict, Response]:
        """Get all alarms"""

        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/alarms/{id}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Alarms", r)

        return content, r

    def post_alarm(
        self,
        message: str,
        rule_id: int,
        status: str,
        state: str,
        state_date: str,
        state_message: str,
    ) -> Tuple[dict, Response]:
        """Post an alarm"""
        content = {
            "messageJSON": message,
            "ruleId": rule_id,
            "notificationStatus": status,
            "state": state,
            "stateDate": state_date,
            "stateMessage": state_message,
        }

        try:
            r = self.session.post(f"{ConfigHelper.host}/alarms", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Post alarm", r)

        return content, r

    def put_alarm(
        self,
        id: int,
        state: str,
        state_message: str,
        status: str,
    ) -> Tuple[dict, Response]:
        """Put an alarm"""

        content = {
            "state": state,
            "stateMessage": state_message,
            "notificationStatus": status,
        }

        try:
            r = self.session.put(f"{ConfigHelper.host}/alarms/{id}", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Put alarm", r)

        return {}, r

    def delete_alarm(self, id: int) -> Tuple[dict, Response]:
        """Delete an alarm"""

        try:
            r = self.session.delete(f"{ConfigHelper.host}/alarms/{id}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Delete Alarm", r)

        return {}, r

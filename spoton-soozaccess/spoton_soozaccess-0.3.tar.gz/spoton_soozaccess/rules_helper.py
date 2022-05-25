import json
from typing import Tuple

from requests import Response, Session
from requests.exceptions import HTTPError

from .config_helper import ConfigHelper


class RulesHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_rules(self) -> Tuple[dict, Response]:
        """Get all rules"""
        content = {}

        try:
            r = self.session.get(f"{ConfigHelper.host}/rules")
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Get Rules", r)

        return content, r

    def post_rule(
        self,
        periodicity: str,
        operator: str,
        participation_rate: float,
        voting_rate: float,
        vote_type: str,
        rate: float,
        prefix: str,
        name: str,
        factor_id: int,
        group_id: int,
        user_id: int,
    ) -> Tuple[dict, Response]:
        """Post a rule"""

        content = {
            "periodicity": periodicity,
            "operator": operator,
            "participationRate": participation_rate,
            "votingRate": voting_rate,
            "voteType": vote_type,
            "rate": rate,
            "messagePrefix": prefix,
            "name": name,
            "factorId": factor_id,
            "groupId": group_id,
            "personId": user_id,
        }

        try:
            r = self.session.post(f"{ConfigHelper.host}/rules", json=content)
            r.raise_for_status()
        except HTTPError as e:
            pass
        else:
            content = json.loads(r.content.decode("utf-8"))
        finally:
            ConfigHelper.show_status("    Post Rule", r)

        return content, r

    def put_rule(self, id: int):
        """Archives a rule"""

        try:
            r = self.session.put(f"{ConfigHelper.host}/rules/{id}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Put Group", r)

        return {}, r

    def delete_rule(self, id: int):
        """Deletes a rule"""

        try:
            r = self.session.delete(f"{ConfigHelper.host}/rules/{id}")
            r.raise_for_status()
        except HTTPError as e:
            pass
        finally:
            ConfigHelper.show_status("    Delete Rule", r)

        return {}, r

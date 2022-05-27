# -*- coding: utf-8 -*-
# Default Python Libraries
import re
from datetime import datetime


class Version(object):
    """Parsing and comparing version strings"""

    __pattern: re = re.compile("(\\d+)(?:\\.(\\d+))?(?:\\.(\\d+))?(?:\\.(\\d+))?(?:\\.(\\d+))?")

    def key(self, v: str) -> int:
        if not (v):
            return 0

        m: re = self.__pattern.match(v)
        # invalid version string
        if m is None:
            return 0

        gs = m.groups()
        key = 0
        places = len(gs)
        for i in range(places):
            p = gs[i]
            if p is None:
                break
            if len(p) > 3:
                # ugh... unsupported
                return 0
            key += int(p) * 10 ** (places - i)

        # print(f"{v} = {key}")
        return key


VERSION = Version()

# print(v.compare("1.5.0", "1.5.0"))
# vs = ["999.999.999.999.999", "1.5.0", "2.3.555.0", "2.3.8", "5.1", "3", "0.9.6", "2.3.8.1", "2.3.5"]
# print(sorted(vs, key=v.key))


def TO_BPM_DATE(dt: datetime) -> int:
    """Converts a datetime to a BPM platform date/time value"""
    if not (dt):
        return 0
    return int(dt.timestamp() * 1000)


def FROM_BPM_DATE(timestamp: int) -> datetime:
    """Converts a date / time value from the BPM platform to a datetime object"""
    if timestamp == 0:
        return None
    return datetime.fromtimestamp(timestamp / 1e3)


class OrgUtils(object):
    """Org model related utilities"""

    @classmethod
    def summarize_qa_list(cls, *qas):
        """Returns a summarizing string for the given qas"""
        if not (qas):
            return ""
        summary = ""
        for agent in qas:
            name = (
                agent.agent_name
                if agent.agent_name == agent.org_pos_name
                else f"{agent.agent_name} ({agent.org_pos_name})"
            )
            if summary == "":
                summary = name
            else:
                summary = summary + ", " + name

        return summary

    @classmethod
    def build_staff_assignment_rule_for_agent(cls, agent_id: int, org_pos_id: int) -> str:
        """
        Creates a staff assignment rule selecting exactly the given agent.
        """
        return f"Agent(id={agent_id}) AND OrgPosition(id={org_pos_id})"

"""A list of package metadata items containing vulnerability notices"""
from collections import UserList


class Vulnerabilities(UserList):
    """A list of package metadata items containing vulnerability notices"""

    def __repr__(self):
        advisories = [[data_item, advisory] for data_item in self for advisory in data_item.advisories]
        if len(advisories) == 0:
            return "No vulnerabilities found"
        return f"{len(advisories)} vulnerabilities found" if len(advisories) > 1 else "One vulnerability found"

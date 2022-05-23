from geodesic.bases import APIObject
from geodesic.account.user import User
from geodesic import raise_on_error
from geodesic.service import ServiceClient

from typing import Dict, List

# Organizations client
organizations_client = ServiceClient("krampus", 1, "organizations")


def get_organization(name: str = None):
    if name is None:
        raise ValueError("must provide organization name")
    res = raise_on_error(organizations_client.get(name))
    p = res.json()['organization']
    if p is None:
        return None
    return Organization(**p)


def get_organizations():
    res = raise_on_error(organizations_client.get(''))
    return [Organization(**o) for o in res.json()['organizations']]


class Organization(APIObject):
    """
    The Organization class to manage groups users

    Args:
        **organization: metadata about a particular Organization
    """
    _limit_setitem = [
        "alias",
        "description",
        "homepage",
        "total_seats"
    ]

    def __init__(self, **organization):
        self._client = organizations_client
        for k, v in organization.items():
            if k in ('name', 'remaining_seats'):
                self._set_item(k, v)
            else:
                setattr(self, k, v)

    def create(self) -> None:
        """
        Creates a new Organization
        """
        raise_on_error(self._client.post("", organization=self))

    def delete(self) -> None:
        """
        Deletes an Organization
        """
        raise_on_error(self._client.delete(self.name))

    def save(self) -> None:
        """
        Updates an existing Organization
        """
        raise_on_error(self._client.put(self.name, organization=self))

    @property
    def members(self) -> Dict[str, User]:
        """
        All of the members and admins
        """
        res = raise_on_error(self._client.get(f"{self.name}/members"))
        return {
            'admins': [User(**m) for m in res.json().get('admins', [])],
            'members': [User(**m) for m in res.json().get('members', [])],
        }

    def add_members(self, members: List[User] = [], admins: List[User] = []) -> None:
        """
        Add members to this Organization

        Args:
            members: a list of users to give ordinary membership to
            admins: a list of users to give admin privileges to
        """
        raise_on_error(self._client.post(f"{self.name}/members", members=members, admins=admins))

    def remove_member(self, u: User):
        """
        Remove a member from this Organization

        Args:
            u: A User to remove
        """
        raise_on_error(self._client.delete(f"{self.name}/{u.subject}"))

    @property
    def remaining_seats(self):
        """
        Gets the number of seats remaining in this Organization (total_seats - # of users)
        """
        res = raise_on_error(self._client.get(self.name))
        return res.json()['organization'].get('remaining_seats', 0)

    @property
    def name(self):
        return self['name']

    @property
    def alias(self):
        return self['alias']

    @alias.setter
    def alias(self, v: str):
        if not isinstance(v, str):
            raise ValueError("alias must be a string")
        self._set_item('alias', v)

    @property
    def description(self):
        return self['description']

    @description.setter
    def description(self, v: str):
        if not isinstance(v, str):
            raise ValueError("description must be a string")
        self._set_item('description', v)

    @property
    def homepage(self):
        return self['homepage']

    @homepage.setter
    def homepage(self, v: str):
        if not isinstance(v, str):
            raise ValueError("homepage must be a string")
        self._set_item('homepage', v)

    @property
    def total_seats(self):
        return self['total_seats']

    @total_seats.setter
    def total_seats(self, v: int):
        if not isinstance(v, int):
            raise ValueError("total_seats must be an int")
        self._set_item('total_seats', v)

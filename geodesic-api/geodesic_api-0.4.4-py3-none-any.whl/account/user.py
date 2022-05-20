import re
from geodesic.bases import APIObject
from geodesic.service import ServiceClient
from geodesic.client import raise_on_error
from geodesic.widgets import get_template_env, jinja_available
from typing import List

# ServiceClient for the Krampus Version 1 users API.
users_client = ServiceClient('krampus', 1, "users")

# Regex to check for valid emails.
email_re = re.compile(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
                      r"\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\""
                      r")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]"
                      r"|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z"
                      r"0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")

KRAMPUS_READ = 'krampus:read'
SPACETIME_READ = 'spacetime:read'
SPACETIME_WRITE = 'spacetime:write'
ENTANGLEMENT_READ = 'entanglement:read'
ENTANGLEMENT_WRITE = 'entanglement:write'
TESSERACT_READ = 'tesseract:read'
TESSERACT_WRITE = 'tesseract:write'

valid_permissions = [
    KRAMPUS_READ,
    SPACETIME_READ,
    SPACETIME_WRITE,
    ENTANGLEMENT_READ,
    ENTANGLEMENT_WRITE,
    TESSERACT_READ,
    TESSERACT_WRITE
]


class User(APIObject):
    """
    The User class to represent user info and control/update profile and permissions.
    Certain functionality will be restricted to admins.

    Args:
        **info: metadata about a particular user, this can be used to create or update
        the User's profile.
    """
    _limit_setitem = [
        "subject",
        "alias",
        "first_name",
        "last_name",
        "middle_name",
        "email",
        "avatar",
        "pronouns",
        "bio"
    ]

    def __init__(self, **info) -> None:
        # client for the users API
        self._client = users_client

        for k, v in info.items():
            setattr(self, k, v)

    @property
    def roles(self) -> List[str]:
        """
        Gets and returns all of the roles for this user: admin/internal/user. Global roles
        CANNOT be set through the REST API.
        """
        res = raise_on_error(self._client.get(f'{self.subject}/roles'))
        return res.json()['roles']

    @property
    def permissions(self) -> List[str]:
        """
        Gets and returns the user's permissions as a list of strings.

        Returns:
            permissions: the user's permissions for various services.
        """
        res = raise_on_error(self._client.get(f'{self.subject}/permissions'))
        return res.json()['permissions']

    @permissions.setter
    def permissions(self, permissions: List[str]) -> None:
        """
        Sets the user's permissions on the server side.

        Args:
            permissions: a list of permission strings. Only certain permissions are valid.
        """

        for permission in permissions:
            if permission not in valid_permissions:
                raise ValueError(f"{permission} is not valid. Valid options are {valid_permissions}")

        raise_on_error(self._client.put(f'{self.subject}/permissions', permissions=permissions))

    @property
    def enabled(self) -> bool:
        """
        Checks if this user's account is currently enabled in the system. Disabled accounts can't do anything.

        Returns:
            enabled: whether or not the user's account is enabled.
        """
        res = raise_on_error(self._client.get(f'{self.subject}/naughty'))
        if res.json()['naughty']:
            return False
        return True

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Enable or disable a user's account. Only available to admins

        Args:
            enabled: Whether to enable or disable this user's account
        """
        raise_on_error(self._client.put(f'{self.subject}/naughty', naughty=not enabled))

    def create(self) -> None:
        """
        Creates this user on the server side. Only available to admins
        """
        if self.subject is None:
            raise ValueError("must create user with a 'subject' specified")
        raise_on_error(self._client.post('', user=self))

    def save(self) -> None:
        """
        Updates this user on the server side. Only available to the admins or the current user
        """
        if self.subject is None:
            raise ValueError("cannot update a User with no subject")
        raise_on_error(self._client.put(f'{self.subject}', user=self))

    def delete(self):
        """
        Delete this account and all associations. Only available to admins or the current user.
        """
        if self.subject is None:
            raise ValueError("cannot delete a User without specifying a subject")
        raise_on_error(self._client.delete(f'{self.subject}'))

    @property
    def subject(self):
        """
        This is the unique identifier for the user.
        """
        return self['subject']

    @subject.setter
    def subject(self, v: str):
        if not isinstance(v, str):
            raise ValueError("subject must be a string")
        self._set_item('subject', v)

    @property
    def alias(self):
        """
        Human readable name for the user
        """
        return self['alias']

    @alias.setter
    def alias(self, v: str):
        if not isinstance(v, str):
            raise ValueError("alias must be a string")
        self._set_item('alias', v)

    @property
    def first_name(self):
        """
        User's first name
        """
        return self['first_name']

    @first_name.setter
    def first_name(self, v: str):
        if not isinstance(v, str):
            raise ValueError("first_name must be a string")
        self._set_item('first_name', v)

    @property
    def last_name(self):
        """
        User's last name
        """
        return self['last_name']

    @last_name.setter
    def last_name(self, v: str):
        if not isinstance(v, str):
            raise ValueError("last_name must be a string")
        self._set_item('last_name', v)

    @property
    def middle_name(self):
        """
        User's middle name
        """
        return self['middle_name']

    @middle_name.setter
    def middle_name(self, v: str):
        if not isinstance(v, str):
            raise ValueError("middle_name must be a string")
        self._set_item('middle_name', v)

    @property
    def email(self):
        """
        User's email address
        """
        return self['email']

    @email.setter
    def email(self, v: str):
        if not isinstance(v, str):
            raise ValueError("email must be a string")
        if not (v == "" or email_re.match(v)):
            raise ValueError("email must be a valid email address")
        self._set_item('email', v)

    @property
    def avatar(self):
        """
        User's avatar/profile picture
        """
        return self['avatar']

    @avatar.setter
    def avatar(self, v: str):
        if not isinstance(v, str):
            raise ValueError("avatar must be a string")
        self._set_item('avatar', v)

    @property
    def pronouns(self):
        """
        User's prefered pronouns
        """
        return self['pronouns']

    @pronouns.setter
    def pronouns(self, v: str):
        if not isinstance(v, str):
            raise ValueError("pronouns must be a string")
        self._set_item('pronouns', v)

    @property
    def bio(self):
        """
        User's biography
        """
        return self['bio']

    @bio.setter
    def bio(self, v: str):
        if not isinstance(v, str):
            raise ValueError("bio must be a string")
        self._set_item('bio', v)

    def _repr_html_(self):
        if not jinja_available():
            return self.__repr__()

        template = get_template_env().get_template("user_template.html.jinja")
        return template.render(u=self)


def myself() -> User:
    """
    Returns the current logged in user

    Returns:
        user: The currently logged in User.
    """
    res = raise_on_error(users_client.get("self"))
    return User(**res.json()['user'])


def get_user(subject: str) -> User:
    """
    Returns the requested user if the requestor has permissions

    Args:
        subject: the subject of the requested user

    Returns:
        user: the requested User
    """
    res = raise_on_error(users_client.get(subject))
    return User(**res.json()['user'])


def get_users() -> List[User]:
    """
    Returns all users, if the current user has permission

    Returns:
        users: a list of all users.
    """
    res = raise_on_error(users_client.get(""))
    return [User(**u) for u in res.json()['users']]

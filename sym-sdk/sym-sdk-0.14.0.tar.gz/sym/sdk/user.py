"""Representations of Users in both Sym and third parties."""

import itertools
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .resource import SymBaseResource


class UserIdentity(ABC, SymBaseResource):
    """Represents a :class:`~sym.sdk.user.User`'s
    identity in an external system such as Slack or PagerDuty.
    """

    def __str__(self) -> str:
        return f"Identity({self.service}: {self.user_id})"

    def __repr__(self) -> str:
        return str(self)

    @property
    @abstractmethod
    def service(self) -> str:
        """The name of the external system providing the identity.

        For example, :mod:`~sym.sdk.integrations.slack`.
        """

    @property
    @abstractmethod
    def service_id(self) -> str:
        """The ID of the external system providing the identity.

        For example, "T123ABC" for a Slack Workspace.
        """

    @property
    @abstractmethod
    def user_id(self) -> str:
        """The :class:`~sym.sdk.user.User`'s identifier in the external system.

        For example, the :class:`~sym.sdk.user.User`'s Slack ID.
        """


class User(ABC, SymBaseResource):
    """The atomic representation of a user in Sym.

    :class:`~sym.sdk.user.User`s have many :class:`~sym.sdk.user.UserIdentity`,
    which are used for referencing said user in external systems.
    """

    def __str__(self) -> str:
        identities = list(itertools.chain.from_iterable(self.identities.values()))
        return f"User(email={self.email}, username={self.username}, identities={identities})"

    def __repr__(self) -> str:
        return f"User({self.username})"

    def __hash__(self):
        return hash(self.__class__) + hash(self.username)

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.username == other.username

    @property
    @abstractmethod
    def email(self) -> Optional[str]:
        """The :class:`~sym.sdk.user.User`'s email if the user is of type "normal", or None otherwise."""

    @property
    @abstractmethod
    def username(self) -> str:
        """The :class:`~sym.sdk.user.User`'s username if the user is of type "bot", or
        the email if the user is of type "normal".
        """

    @property
    @abstractmethod
    def type(self) -> str:
        """The :class:`~sym.sdk.user.User`'s type (i.e. "bot" or "normal")."""

    @property
    @abstractmethod
    def first_name(self) -> Optional[str]:
        """The :class:`~sym.sdk.user.User`'s first name."""

    @property
    @abstractmethod
    def last_name(self) -> Optional[str]:
        """The :class:`~sym.sdk.user.User`'s last name."""

    @property
    @abstractmethod
    def identities(self) -> Dict[str, List[UserIdentity]]:
        """Retrieves the set of identities associated with this
        :class:`~sym.sdk.user.User`, grouped by service type.

        A mapping of service types to lists of :class:`~sym.sdk.user.UserIdentity`.
        """

    @abstractmethod
    def identity(
        self,
        service_type: str,
        service_id: Optional[str] = None,
    ) -> Optional[UserIdentity]:
        """Retrieves this :class:`~sym.sdk.user.User`'s :class:`~sym.sdk.user.UserIdentity`
        for a particular external system.

        External systems specified by a service_type, and optionally a service_id.

        Args:
            service_type: The name of one of Sym's :mod:`~sym.sdk.integrations`.
            service_id: An identifier for an instance of a service, such as a Slack Workspace ID.

        Returns:
            A :class:`~sym.sdk.user.UserIdentity`, or None if no identity is found for the Integration.
        """

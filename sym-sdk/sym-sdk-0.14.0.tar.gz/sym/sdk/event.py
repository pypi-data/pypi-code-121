"""Triggers for the various steps of a :class:`~sym.sdk.events.Flow`."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from sym.sdk.flow import Flow, Run
from sym.sdk.resource import SRN, SymResource
from sym.sdk.templates import Template
from sym.sdk.user import User


class Payload(SymResource):
    """The :class:`~sym.sdk.events.Payload` object contains the data of the
    :class:`~sym.sdk.events.Event`.
    """

    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        """A datetime object indicating when the :class:`~sym.sdk.events.Event` was created."""

    @property
    @abstractmethod
    def fields(self) -> Dict[str, Any]:
        """A dict containing the values submitted by the user who created
        the :class:`~sym.sdk.events.Event`
        """

    @property
    @abstractmethod
    def srn(self) -> SRN:
        """The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.events.Event` instance."""

    @property
    @abstractmethod
    def user(self) -> User:
        """The :class:`~sym.sdk.user.User` who triggered the :class:`~sym.sdk.events.Event`."""


class Channel(SymResource):
    """The :class:`~sym.sdk.event.Channel` object contains information about the channel
    from which an event was sent.
    """

    @property
    @abstractmethod
    def identifier(self) -> Optional[str]:
        """The identifier of the channel (e.g. ``#general`` for a Slack channel).

        Note that, if the event originated from a Slack *shortcut* (as opposed to
        a slash command), identifier will be ``None``. This is because shortcuts
        are global and not linked to any specific channel.
        """

    @property
    @abstractmethod
    def type(self) -> str:
        """The channel type (e.g. ``slack`` or ``sym``)."""


class EventMeta(SymResource, ABC):
    """Contains metadata about an :class:`~sym.sdk.event.Event` instance."""


class Event(SymResource, ABC):
    """The :class:`~sym.sdk.events.Event` class contains information on an event which has been
    received by Sym, routed to a :class:`~sym.sdk.flow.Run` of a :class:`~sym.sdk.flow.Flow`, and is
    triggering specific user-defined Handlers.

    Each Handler will be invoked with a single argument, which is an instance of this class.
    This :class:`~sym.sdk.events.Event` instance will describe the current execution state,
    and can be used to dynamically alter the behavior and control flow of
    Templates.

    Read more about `Handlers <https://docs.symops.com/docs/handlers>`_.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the :class:`~sym.sdk.event.Event`."""

    @property
    @abstractmethod
    def payload(self) -> Payload:
        """A :class:`~sym.sdk.event.Payload` object, which contains the primary data
        of the :class:`~sym.sdk.event.Event`.
        """

    @property
    @abstractmethod
    def meta(self) -> EventMeta:
        """An :class:`~sym.sdk.event.EventMeta` object, which contains metadata
        about the :class:`~sym.sdk.event.Event` instance.
        """

    @property
    @abstractmethod
    def template(self) -> Template:
        """A :class:`~sym.sdk.templates.template.Template` object, indicating which
        :class:`~sym.sdk.templates.template.Template` the current :class:`~sym.sdk.flow.Flow` inherits from.
        """

    @property
    @abstractmethod
    def flow(self) -> Flow:
        """A :class:`~sym.sdk.flow.Flow` object, indicating the :class:`~sym.sdk.flow.Flow` that
        the current :class:`~sym.sdk.flow.Run` is an instance of.
        """

    @property
    @abstractmethod
    def run(self) -> Run:
        """A :class:`~sym.sdk.flow.Run` object, indicating the current
        :class:`~sym.sdk.flow.Run`.
        """

    @property
    @abstractmethod
    def channel(self) -> Channel:
        """A :class:`~sym.sdk.event.Channel` object indicating the channel the
        current :class:`~sym.sdk.event.Event` instance is coming from.
        """

    @property
    def user(self) -> User:
        """The :class:`~sym.sdk.user.User` who triggered the :class:`~sym.sdk.event.Event`."""
        return self.payload.user

    @abstractmethod
    def get_actor(self, event_name: str) -> Optional[User]:
        """Retrieve the :class:`~sym.sdk.user.User` who triggered a specific
        :class:`~sym.sdk.event.Event`.

        For example, for a :class:`~sym.sdk.flow.Run` using the
        :class:`~sym.sdk.templates.approval.ApprovalTemplate`, to get the approver::

            approver = event.get_actor("approve")

        For a list of event names, see the relevant template's Enum (e.g.
        :class:`~sym.sdk.templates.approval.ApprovalTemplateStep`).

        Note that, for the :class:`~sym.sdk.templates.approval.ApprovalTemplate`, the ``escalate``
        and ``deescalate`` actors will be the same as the ``approve`` actor, because those events
        are automatically triggered by the ``approve`` event.

        Args:
            event_name (str): The name of the :class:`~sym.sdk.event.Event` to retrieve the
                actor for.

        Returns:
            The :class:`~sym.sdk.user.User` who triggered the :class:`~sym.sdk.event.Event`
            with the given ``event_name``, if that :class:`~sym.sdk.event.Event` has occurred
            in the current :class:`~sym.sdk.flow.Run`. Otherwise returns ``None``.
        """

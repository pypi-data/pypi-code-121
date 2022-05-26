from abc import ABC, abstractmethod
from typing import Any, Dict

from sym.sdk.resource import SymResource


class Integration(ABC, SymResource):
    """Represents an Integration (service-specific config and state) in the Sym SDK.

    For the purposes of the SDK, Integrations can be thought of as the "state" of a Strategy. Or, to
    put it another way, if a Strategy tells Sym how to interact with an external service to perform
    escalations, the Integration is the service-specific state Sym maintains, including the identity
    mappings of Sym users to the external service."""

    @property
    @abstractmethod
    def type(self) -> str:
        """The type of service represented by this Integration object."""

    @property
    @abstractmethod
    def external_id(self) -> str:
        """A unique (for this type), meaningful identifier for this Integration.

        This allows you to have multiple integrations of the same type. The meaning of the
        ``external_id`` varies from Strategy to Strategy—some Strategies use this as a domain or
        tenant identifier for some services, while for others it's simply an Implementer-defined
        identifier.

        For example, a Slack Integration uses the Slack workspace ID as the ``external_id`` value,
        while an Okta Integration uses the Okta Domain as the ``external_id``.
        """

    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """A dictionary of settings for the Integration, as specified in Terraform. May be empty,
        but will never be ``None``."""

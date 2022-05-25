"""Tools for working with secrets."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from sym.sdk.resource import SymResource


class SecretSource(ABC, SymResource):
    """This class represents a `sym_secrets <https://docs.symops.com/docs/tf-secrets>`_ (plural)
    Terraform resource.

    A ``sym_secrets`` resource represents a remote service or location where secrets are stored; for
    example, AWS Secrets Manager.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        """The type of remote storage; for example, ``aws_secrets_manager``."""

    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """A dictionary of settings for the secret storage, as specified in Terraform."""


class Secret(ABC, SymResource):
    """This class represents a
    `sym_secret <https://docs.symops.com/docs/tf-secrets#supplying-a-secret>`_ (singular) Terraform
    resource.

    A ``sym_secret`` resource represents an individual secret stored in a remote service or location.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """The UUID of the secret resource."""

    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the secret in the remote secret store (e.g., AWS Secrets Manager)."""

    @property
    @abstractmethod
    def source(self) -> SecretSource:
        """The location where this secret is stored."""

    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """A dictionary of settings for the secret, as specified in Terraform."""

    @abstractmethod
    def retrieve_value(self) -> str:
        """Retrieve this secret's value from its remote storage."""

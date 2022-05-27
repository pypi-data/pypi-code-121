"""Types related to transport layer sending and receiving."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Type, TypeVar

from bitfount.types import _JSONDict

_T = TypeVar("_T")


@dataclass
class _SerializationMixin:
    """Mixin to provide (de)serialization functionality."""

    def serialize(self) -> _JSONDict:
        """Serialize the dataclass to a JSON-compatible dictionary."""
        return dataclasses.asdict(self)

    @classmethod
    def deserialize(cls: Type[_T], data: _JSONDict) -> _T:
        """Deserialize the dataclass from a JSON-compatible dictionary."""
        return cls(**data)


@dataclass
class _OIDCClientID(_SerializationMixin):
    """Form of Client ID response from pods to initial request."""

    client_id: str


@dataclass
class _OIDCAuthEndpointResponse:
    """Form of the details extracted from OIDC Auth Flow callback."""

    auth_code: str
    state: str


@dataclass
class _OIDCAuthFlowResponse(_SerializationMixin):
    """Form of OIDC Auth Flow message sent to pod for verification."""

    auth_code: str
    code_verifier: str
    redirect_uri: str


class _DeviceCodeDetailsPair(NamedTuple):
    """The separated pod- and modeller-related device code response details."""

    pod_details: _PodDeviceCodeDetails
    modeller_details: _ModellerDeviceCodeDetails


@dataclass
class _PodDeviceCodeDetails(_SerializationMixin):
    """The pod-related device code response details."""

    device_code: str
    expires_at: datetime
    interval: int

    def serialize(self) -> _JSONDict:
        """Serialize the dataclass to a JSON-compatible dictionary."""
        # Create basic serialization dictionary
        d = super().serialize()
        # Replace datetime with ISO format string
        d["expires_at"] = d["expires_at"].isoformat()
        return d

    @classmethod
    def deserialize(cls, data: _JSONDict) -> _PodDeviceCodeDetails:
        """Deserialize the dataclass from a JSON-compatible dictionary."""
        # Reconstruct datetime object
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


@dataclass
class _ModellerDeviceCodeDetails:
    """The modeller-related device code response details."""

    user_code: str
    verification_uri: str
    verification_uri_complete: str

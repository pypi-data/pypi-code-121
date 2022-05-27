"""Fixtures for authorisation-checkers-related classes."""
from dataclasses import dataclass
from typing import cast
from unittest.mock import Mock, NonCallableMock, create_autospec

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from pytest import fixture

from bitfount.federated.authorisation_checkers import (
    _IDENTITY_VERIFICATION_METHODS_MAP,
    IdentityVerificationMethod,
    _SignatureBasedAuthorisation,
)
from bitfount.federated.types import _TaskRequestMessageGenerator


@fixture
def default_task_request_msg_gen() -> _TaskRequestMessageGenerator:
    """Creates a TaskRequestMessageGenerator for the default verification method."""
    # Create default task_request_msg_gen
    default_authoriser = _IDENTITY_VERIFICATION_METHODS_MAP[
        IdentityVerificationMethod.DEFAULT
    ]
    task_request_msg_gen = default_authoriser.create_task_request_message_generator()
    return task_request_msg_gen


@fixture
def saml_task_request_msg_gen() -> _TaskRequestMessageGenerator:
    """Creates a TaskRequestMessageGenerator for the SAML verification method."""
    # Create SAML task_request_msg_gen
    saml_authoriser = _IDENTITY_VERIFICATION_METHODS_MAP[
        IdentityVerificationMethod.SAML
    ]
    task_request_msg_gen = saml_authoriser.create_task_request_message_generator()
    return task_request_msg_gen


@dataclass
class KeyBasedGenerator:
    """Container for the key and generator for key-based task_request_msg_gen."""

    key: NonCallableMock
    gen: _TaskRequestMessageGenerator


@fixture
def key_based_task_request_msg_gen() -> KeyBasedGenerator:
    """Creates a TaskRequestMessageGenerator for the key-based verification method."""
    # Create key-based task_request_msg_gen
    key_based_authoriser: _SignatureBasedAuthorisation = cast(
        _SignatureBasedAuthorisation,
        _IDENTITY_VERIFICATION_METHODS_MAP[IdentityVerificationMethod.KEYS],  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
    )

    private_key: NonCallableMock = create_autospec(RSAPrivateKey, instance=True)
    task_request_msg_gen = key_based_authoriser.create_task_request_message_generator(
        private_key
    )

    return KeyBasedGenerator(private_key, task_request_msg_gen)


@fixture
def mock_task_request_msg_gen() -> Mock:
    """Creates a mock TaskRequestMessageGenerator."""
    # Create mock task_request_msg_gen
    task_request_msg_gen: Mock = create_autospec(_TaskRequestMessageGenerator)

    return task_request_msg_gen

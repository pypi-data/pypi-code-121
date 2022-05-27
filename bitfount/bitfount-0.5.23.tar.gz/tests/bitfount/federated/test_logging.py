"""Tests logging.py."""

import logging
from typing import Dict
from unittest.mock import Mock

from _pytest.logging import LogCaptureFixture
import pytest

from bitfount.federated.logging import (
    _federate_logger,
    _FederatedLogFilter,
    _FederatedLogger,
    _get_federated_logger,
    _MailboxHandler,
)
from tests.utils.helper import unit_test

LOGGING_METHODS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@pytest.fixture
def log_message() -> str:
    """Returns dummy log message."""
    return "testing123"


@unit_test
@pytest.mark.parametrize("level", LOGGING_METHODS + ["notareallogginglevel"])
def test_get_federated_logger(caplog: LogCaptureFixture, level: str) -> None:
    """Tests `get_federated_logger` returns a logger with the right methods."""
    logger = _get_federated_logger("bitfount.federated.test")
    msg = f"{level}_msg"

    assert logger.name == "bitfount.federated.test"

    if level in LOGGING_METHODS:
        assert hasattr(logger, f"federated_{level.lower()}")
        method_to_call = getattr(logger, f"federated_{level.lower()}")

        # Confirming that the method can be called - an error will be raised if it can't
        method_to_call(msg)
    else:
        assert not hasattr(logger, f"federated_{level.lower()}")

    for record in caplog.records:
        assert record.levelname == level
        assert record.msg == msg


@unit_test
def test_federate_logger() -> None:
    """Tests that `federate_logger` has the right handlers and filters."""
    mock_mailbox = Mock()
    _federate_logger(mock_mailbox)

    federated_logger = logging.getLogger("bitfount.federated")

    # Make assertions on logger
    assert federated_logger.hasHandlers()
    assert len(federated_logger.handlers) == 1
    handler = federated_logger.handlers[0]
    assert isinstance(handler, _MailboxHandler)

    # Make sure that the filter is on the handler rather than the logger
    assert len(federated_logger.filters) == 0

    # Make assertions on handler
    assert handler.level == logging.DEBUG
    assert len(handler.filters) == 1
    assert isinstance(handler.filters[0], _FederatedLogFilter)


@unit_test
def test_federate_logger_only_attaches_handler_once() -> None:
    """Tests that federate_logger only attaches handler once."""
    mock_mailbox = Mock(mock_name="first-mailbox")
    _federate_logger(mock_mailbox)
    federated_logger = logging.getLogger("bitfount.federated")
    assert len(federated_logger.handlers) == 1
    handler = federated_logger.handlers[0]
    assert isinstance(handler, _MailboxHandler)
    assert handler.mailbox == mock_mailbox

    # We make a second call to `federate_logger` which removes the first handler
    mock_mailbox2 = Mock(mock_name="second-mailbox")
    _federate_logger(mock_mailbox2)
    assert len(federated_logger.handlers) == 1
    handler = federated_logger.handlers[0]
    assert isinstance(handler, _MailboxHandler)
    assert handler.mailbox == mock_mailbox2


@unit_test
@pytest.mark.parametrize(
    "name",
    [
        "bitfount.federated",
        "bitfount.federated.aggregators",
        "bitfount.federated.protocols.base",
        "bitfount.federated.transport.base_transport",
        "tests.bitfount.federated",
        "bitfount.hub",
    ],
)
def test_federated_logger_propagates(log_message: str, name: str) -> None:
    """Tests that module loggers within the federated package also become federated.

    Those not in the `federated` package raise a ValueError.
    """
    mock_mailbox = Mock()
    _federate_logger(mock_mailbox)
    if not name.startswith("bitfount.federated"):
        with pytest.raises(ValueError):
            _get_federated_logger(name)
    else:
        logger = _get_federated_logger(name)
        assert isinstance(logger, _FederatedLogger)
        logger.warning(log_message)
        logger.federated_warning(name)
        mock_mailbox.log.assert_called_once()
        assert mock_mailbox.log.call_args[0][0]["msg"] == name


@unit_test
@pytest.mark.parametrize(
    "log_method, extra_arguments, federated",
    [
        ("warning", {}, False),
        ("warning", {"federated": False}, False),
        ("warning", {"federated": True}, True),
        ("federated_warning", {}, True),
    ],
)
def test_federated_logger_filter(
    caplog: LogCaptureFixture,
    extra_arguments: Dict[str, bool],
    federated: bool,
    log_message: str,
    log_method: str,
) -> None:
    """Tests the the FederatedLogFilter correctly filters messages prior to the Handler.

    Tests that only log messages with the `federated` attribute set to True are passed
    on to the MailboxHandler.
    """
    mock_mailbox = Mock()
    _federate_logger(mock_mailbox)
    logger = _get_federated_logger("bitfount.federated")
    method_to_call = getattr(logger, log_method)
    if extra_arguments:
        method_to_call(log_message, extra=extra_arguments)
    else:
        method_to_call(log_message)

    assert len(caplog.records) == 1
    record = caplog.records[0]

    assert record.levelname == "WARNING"
    assert record.msg == log_message

    if federated:
        mock_mailbox.log.assert_called_once()
    else:
        mock_mailbox.log.assert_not_called()

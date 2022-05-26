import logging
from unittest.mock import MagicMock

import pytest

from cosapp.tools.fmu.logging import FMUForwardHandler, Fmi2Status


@pytest.mark.parametrize(
    "level,status",
    [
        (logging.CRITICAL, Fmi2Status.fatal),
        (logging.ERROR, Fmi2Status.error),
        (logging.WARNING, Fmi2Status.warning),
        (logging.INFO, Fmi2Status.ok),
        (logging.DEBUG, Fmi2Status.ok),
    ],
)
def test_FMUForwardHandler_logging2FmiLevel(level, status):
    assert FMUForwardHandler.logging2FmiLevel(level) == status


@pytest.mark.skip(reason="Randomly failing - to be investigated")
@pytest.mark.parametrize(
    "handler_level",
    [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG],
)
@pytest.mark.parametrize(
    "level, msg",
    [
        (logging.CRITICAL, "This is a fatal message"),
        (logging.ERROR, "This is a error message"),
        (logging.WARNING, "This is a warning message"),
        (logging.INFO, "This is a information message"),
        (logging.DEBUG, "This is a debug message"),
    ],
)
def test_FMUForwardHandler_emit(handler_level, level, msg):
    # Given
    fmu_log = MagicMock()
    fmu = MagicMock(log=fmu_log)

    FMUForwardHandler.add_handler(fmu, level=handler_level)

    # When
    logging.log(level, msg)

    # Then
    if level >= handler_level:
        assert fmu_log.call_args is not None
        message = fmu_log.call_args[0][0]
        assert message.endswith(msg)
        fmu_log.assert_called_once_with(
            message,
            FMUForwardHandler.logging2FmiLevel(level),
            debug = (level == logging.DEBUG),
        )
    else:
        fmu_log.assert_not_called()

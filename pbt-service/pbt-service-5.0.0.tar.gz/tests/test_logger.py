from logging import CRITICAL
import pytest


def test_logger(log, caplog):
    """Check exception hooks and re-raise."""
    with caplog.at_level(CRITICAL):
        with pytest.raises(ZeroDivisionError):
            try:
                1 / 0
            except ZeroDivisionError as exc:
                log.exception(exc)
                caplog.clear()
            finally:
                raise ZeroDivisionError()

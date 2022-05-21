from os import environ


def is_pytest() -> bool:
    """Check if pytest is currently running."""

    return "PYTEST_CURRENT_TEST" in environ

from ._version import version

__version__ = version


def _greeting(name: str) -> str:
    """Sample function to verify test coverage and type hints

    >>> _greeting("Alice")
    'Hello Alice!'
    """
    return f"Hello {name}!"

"""This module contains definition of known AIML versions."""
from enum import Enum, EnumMeta
from functools import total_ordering


class _AIMLVersionsMeta(EnumMeta):
    """
    Make the enum testeble for `in`.

    Metaclass that enables testing whether given item can
    be represented by the enum.
    """

    def __contains__(cls, item):
        """Test whether `item` is represented by this enum."""
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


@total_ordering
class AIMLVersion(Enum, metaclass=_AIMLVersionsMeta):
    """Enumeration of known AIML versions."""

    V1_0 = "1.0"
    """Version 1.0."""
    V1_0_1 = "1.0.1"
    """Version 1.0.1."""
    V2_0 = "2.0"
    """Version 2.0."""
    V2_1 = "2.1"
    """Version 2.1."""

    def __lt__(self, other: 'AIMLVersion'):
        """Compare AIML version, from the time release perspective."""
        return self.value < other.value


DEFAULT_VERSION = AIMLVersion.V2_1
"""The default version this interpreter is built for."""

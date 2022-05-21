"""Miscelanoues files used to define the bot config."""
from typing import Dict, Optional, Mapping


class Properties:
    """
    Properties of the bot.

    Similar interface as a Python's dictionary, but keeping all the values
    in uppercase.

    Example:
        >>> bot_props = Properties()
        >>> bot_props["name"] = "MyBot"
        >>> bot_props["age"] = "19"
        >>> int(bot_props["age"])
        19
        >>> "name" in bot_props
        True
        >>> bot_props["name"] == "MYBOT"
        True
    """

    def __init__(self, other: Optional[Mapping[str, str]] = None):
        """
        Initialize the properties of the bot.

        :param other: default values of properties
        """
        self._dict: Dict[str, str] = dict()
        if other:
            self.update(other)

    def __setitem__(self, key: str, value: str):
        """Set the bot's property to `value`."""
        self._dict[key.upper()] = value.upper()

    def __contains__(self, key: str) -> bool:
        """Check whether given property exists."""
        return key.upper() in self._dict

    def __getitem__(self, key: str):
        """Get bot's property from `key`."""
        return self._dict[key.upper()]

    def get(self, key: str, default: Optional[str] = None):
        """Get bot's property or return `default` if not found."""
        return self._dict.get(key.upper(), default)

    def update(self, other: Mapping[str, str]):
        """Update bot's properties."""
        for k, v in other.items():
            self.__setitem__(k, v)


class Predicates(Dict[str, str]):
    """
    Predicates of the bot.

    Has same interface as Python's dictionary.

    Example:
        >>> predicates = Predicates()
        >>> predicates["hungry"] = "always"
        >>> predicates.get("hungry", "idk") == "always"
        True
    """

import re
from enum import Enum
from typing import Any, List, Tuple, Set
from cosapp.utils.helpers import check_arg


class CommonPorts(Enum):
    """Port names common to every system.
    
    INWARDS : For orphan input variables
    OUTWARDS : For orphan output variables
    MODEVARS_IN : For orphan input mode variables
    MODEVARS_OUT : For orphan output mode variables
    """
    INWARDS = "inwards"
    OUTWARDS = "outwards"
    MODEVARS_IN = "modevars_in"
    MODEVARS_OUT = "modevars_out"

    @classmethod
    def names(cls) -> Set[str]:
        """Returns common port names as a set."""
        return set(case.value for case in cls)


def has_time(expression: Any) -> bool:
    """Checks if an expression contains 't'"""
    return re.search(r"\bt\b", str(expression)) is not None


def natural_varname(name: str) -> str:
    """Strip references to common port names from variable name
    """
    pattern = "|".join(CommonPorts.names())
    return re.sub(f"({pattern})\.", "", name.strip())


class NameChecker:
    """Class handling admissible names, through regular expression filtering"""
    def __init__(self,
        pattern = r"^[A-Za-z][\w]*$",
        message = "Name must start with a letter, and contain only alphanumerics and '_'",
        excluded: List[str] = [],
    ):
        self.__error_message = lambda name: None  # type: Callable[[str], str]
        self.__message = ""  # type: str
        self.__pattern = None  # type: re.Pattern
        self.__excluded = tuple()
        self.pattern = pattern
        self.message = message
        self.excluded = excluded

    @classmethod
    def reserved(cls) -> List[str]:
        """List of reserved names"""
        return ["t", "time"]

    @property
    def pattern(self) -> str:
        return self.__pattern.pattern

    @pattern.setter
    def pattern(self, pattern: str) -> None:
        self.__pattern = re.compile(pattern)

    @property
    def excluded(self) -> Tuple[str]:
        return self.__excluded

    @excluded.setter
    def excluded(self, excluded) -> None:
        excluded = excluded or []
        if isinstance(excluded, str):
            excluded = [excluded]
        else:
            check_arg(excluded, 'excluded', (list, tuple, set),
                value_ok = lambda col: all(isinstance(s, str) for s in col)
            )
        self.__excluded = tuple(excluded)

    @property
    def message(self) -> str:
        """Returns a human-readable message, transcripted from regexp rule"""
        return self.__message

    @message.setter
    def message(self, message: str) -> None:
        check_arg(message, "message", str)
        self.__message = message
        if len(self.__message) > 0:
            self.__error_message = lambda name: f"{self.__message}; got {name!r}."
        else:
            self.__error_message = lambda name: f"Invalid name {name!r}"

    def is_valid(self, name: str) -> bool:
        """Method indicating whether or not a name is valid, under the current rule"""
        try:
            self(name)
        except:
            return False
        else:
            return True

    def __call__(self, name) -> str:
        """Returns `name` if valid; otherwise, raises an exception"""
        check_arg(name, "name", str)
        message = None
        reserved = self.reserved()
        if name in reserved:
            message = f"Names {reserved} are reserved"
        elif name in self.excluded:
            message = f"Names {self.excluded} are invalid"
        elif self.__pattern.match(name) is None:
            message = self.__error_message(name)
        if message is not None:
            raise ValueError(message)
        return name

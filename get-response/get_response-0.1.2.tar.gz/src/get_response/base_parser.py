from abc import ABC
from abc import abstractmethod
from typing import Tuple, Any

T_GET_OBJECTS = Tuple[Any, ...]


class BaseParser(ABC):

    @abstractmethod
    def __init__(self, obj: str) -> None:
        self.obj = obj

    @abstractmethod
    def get_objects(self, field: str) -> T_GET_OBJECTS:
        """Method parsing the object and return what he found by given
        key.

        Method get object and trying to found in it values that exist
        in it by the given key.

        Args:
            field: Field which value must be found.

        Returns:
            Tuple[Any]: Method return a found values or empty tuple if
             searching are failed.
        """
        pass

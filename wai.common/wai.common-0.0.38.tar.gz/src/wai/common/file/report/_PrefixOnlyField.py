from abc import abstractmethod, ABC


class PrefixOnlyField(ABC):
    """
    Interface for fields that only have a prefix.
    """
    @abstractmethod
    def is_compound(self) -> bool:
        pass

    @abstractmethod
    def get_prefix(self) -> str:
        pass

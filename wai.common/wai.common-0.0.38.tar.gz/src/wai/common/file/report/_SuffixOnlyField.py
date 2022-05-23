from abc import abstractmethod


class SuffixOnlyField:
    """
    Interface for fields that only have a suffix.
    """
    @abstractmethod
    def is_compound(self) -> bool:
        pass

    @abstractmethod
    def get_suffix(self) -> str:
        pass

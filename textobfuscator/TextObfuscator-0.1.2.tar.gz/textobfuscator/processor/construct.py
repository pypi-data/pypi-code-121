from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from textobfuscator.utils import BaseDataclass


@dataclass
class Replace(BaseDataclass):
    count: Optional[int] = 0  # High priority.
    percent: Optional[int] = 0  # Middle priority.
    remaining: Optional[int] = 0  # Low priority.

    def is_valid(self) -> bool:
        """At least one number we can calc the final value."""
        return any((self.count is not None, self.percent is not None, self.remaining is not None))


@dataclass
class BreakWord(BaseDataclass):
    word: str
    places: int = 1
    fill: str = " "
    sensitive: bool = False

    def is_valid(self) -> bool:
        """At least we need a valid word to process."""
        return self.word is not None and self.word.strip() != ""


@dataclass
class ObfuscationConfig(BaseDataclass):
    replaces: Replace = field(default_factory=Replace)
    break_words: List[BreakWord] = field(default_factory=list)

    def is_valid(self) -> bool:
        """All config items need valid."""
        break_words_is_valid = all(word.is_valid() for word in self.break_words)
        return break_words_is_valid and self.replaces.is_valid()


class BaseObfuscator(ABC):
    @abstractmethod
    def mix(self, *args, **kwargs):
        """Each processor need to make a mix func to use."""
        raise NotImplementedError

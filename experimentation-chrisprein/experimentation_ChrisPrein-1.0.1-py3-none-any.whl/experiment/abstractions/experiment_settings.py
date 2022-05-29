from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, List, Generic, Dict

@dataclass
class ExperimentSettings(ABC):
    name: str
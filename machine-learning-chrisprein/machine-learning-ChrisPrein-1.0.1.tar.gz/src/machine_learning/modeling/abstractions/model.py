from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict, Any, Callable

TInput = TypeVar('TInput')
TTarget = TypeVar('TTarget')

class Model(Generic[TInput, TTarget], ABC):

    @abstractmethod
    def predict(self, input: TInput) -> TTarget:
        pass

    @abstractmethod
    def predict_batch(self, input_batch: List[TInput]) -> List[TTarget]:
        pass

    __call__ : Callable[..., Any] = predict
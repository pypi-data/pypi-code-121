from abc import ABC, abstractmethod
import torch

__all__ = ["BasicModel"]


class BasicModel(ABC):
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

    @abstractmethod
    def prepare_data(self, premise, hypothesis):
        pass

    @abstractmethod
    def predict(self, inputs):
        pass

    @abstractmethod
    def validate(self, filename):
        pass

    @staticmethod
    def get_available_models():
        return ["Roberta", "T5"]


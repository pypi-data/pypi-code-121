from typing import Dict,Any
from abc import ABC, abstractmethod
class ABCTokenizer(ABC):
    """Abstract base class for all implemented tokenizers.
    """

    def __init__(self):
        self._tokenizer = None

    @property
    def tokenizer(self):
        return self._tokenizer

    def to_dict(self) -> Dict[str, Any]:
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config':{}
        }

    def tokenize(self, text,max_len=None,**kwargs):
        """
        Tokenize text into token sequence
        Args:
            text: target text sample

        Returns:
            List of tokens in this sample
        """
        raise NotImplementedError

    def encode(self,text,
                second_text=None,
                maxlen=None,**kwargs):
        raise NotImplementedError

    def id_to_token(self, id):
        raise  NotImplementedError


from abc import ABC
from typing import Dict,List,Optional,Any,Tuple
import numpy as np

from nlp_tools.generators import  CorpusGenerator
from nlp_tools.types import TextSamplesVar
from nlp_tools.tokenizer import ABCTokenizer
from nlp_tools.utils import load_data_object


class ABCSentenceProcessor(ABC):
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'max_sentence_length':self.max_sentence_length,
                "embedding_max_position":self.embedding_max_position,
            },
            'text_tokenizer': self.text_tokenizer.to_dict(),

            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self,text_tokenizer=None, max_sentence_length=None,embedding_max_position=None,**kwargs: Any) -> None:
        self.text_tokenizer: ABCTokenizer = text_tokenizer
        self.max_sentence_length = max_sentence_length
        self.embedding_max_position = embedding_max_position



    def _override_load_model(self,config:Dict) -> None:
        self.text_tokenizer: ABCTokenizer = load_data_object(config['text_tokenizer'])


    def build_vocab(self,
                    x_data: TextSamplesVar,
                    y_data: TextSamplesVar) -> None:
        corpus_gen = CorpusGenerator(x_data, y_data)
        self.build_vocab_generator([corpus_gen])

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        raise NotImplementedError

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        return 2, batch_size, seq_length


    def transform(self,samples,seq_length: int = None):
        raise NotImplementedError

    def inverse_transform(self,
                          labels: List[int],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> List[str]:
        raise NotImplementedError




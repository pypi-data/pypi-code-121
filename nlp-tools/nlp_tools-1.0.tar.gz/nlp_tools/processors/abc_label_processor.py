from abc import ABC
from typing import Dict,List,Any,Tuple
import numpy as np

from nlp_tools.generators import  CorpusGenerator
from nlp_tools.types import TextSamplesVar



class ABCLabelProcessor(ABC):
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'vocab2idx': self.vocab2idx,
                'max_sentence_length':self.max_sentence_length,
                "embedding_max_position":self.embedding_max_position,
                "token_pad":self.token_pad
            },
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self,max_sentence_length=None,embedding_max_position=None,vocab2idx={},**kwargs: Any) -> None:
        self.vocab2idx = vocab2idx
        self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])
        self.max_sentence_length = max_sentence_length
        self.embedding_max_position = embedding_max_position
        self.token_pad = "[PAD]"


    @property
    def vocab_size(self) -> int:
        return len(self.vocab2idx)

    @property
    def is_vocab_build(self) -> bool:
        return self.vocab_size != 0

    def build_vocab(self,
                    x_data: TextSamplesVar,
                    y_data: TextSamplesVar) -> None:
        corpus_gen = CorpusGenerator(x_data, y_data)
        self.build_vocab_generator([corpus_gen])

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        raise NotImplementedError

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        return batch_size, seq_length

    def transform(self,samples,seq_length = None):
        raise NotImplementedError

    def inverse_transform(self,
                          labels,
                          lengths = None,
                          mapping_list=None,
                          threshold= 0.5) :
        raise NotImplementedError

    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length




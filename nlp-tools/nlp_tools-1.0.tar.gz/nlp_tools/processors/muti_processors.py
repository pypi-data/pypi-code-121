from abc import ABC
from typing import Dict,List,Any,Tuple
import numpy as np

from nlp_tools.generators import  CorpusGenerator
from nlp_tools.types import TextSamplesVar
from nlp_tools.processors.abc_label_processor import ABCLabelProcessor



class MutiProcessors(ABCLabelProcessor):
    def to_dict(self) -> Dict[str, Any]:
        processed_dict_list = []
        for processor in self.processors:
            processed_dict_list.append(processor.to_dict())

        return {
            'config': {
                'processors': processed_dict_list
            },
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self,processors) -> None:
        self.processors = processors



    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        for processor in self.processors:
            processor.build_vocab_generator(generators)

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        raise NotImplementedError

    def transform(self,samples,seq_length = None):
        output = []
        for processor in self.processors:
            transform_data = processor.transform(seq_length)
            if type(transform_data) == tuple or type(transform_data) == list:
                output.extend(list(transform_data))
            else:
                output.append(transform_data)
        return output

    def inverse_transform(self,
                          labels,
                          lengths = None,
                          mapping_list=None,
                          threshold= 0.5) :
        raise NotImplementedError

    def _override_load_model(self,config:Dict) -> None:
        self.processors = []
        for processor_dict  in  config['processors']:
            self.processors.append(load_data_object(processor_dict))

    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length




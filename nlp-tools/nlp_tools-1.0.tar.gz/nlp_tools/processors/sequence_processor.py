# encoding: utf-8


import collections
import operator
from typing import Dict, List, Any, Optional, Union

import numpy as np
import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nlp_tools.generators import CorpusGenerator
from nlp_tools.logger import logger
from nlp_tools.processors.abc_sentence_processor import ABCSentenceProcessor
from nlp_tools.types import TextSamplesVar


class SequenceProcessor(ABCSentenceProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(SequenceProcessor, self).to_dict()
        data['config'].update({
        })
        return data

    def __init__(self,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(SequenceProcessor, self).__init__(**kwargs)



    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def transform(self,samples: TextSamplesVar,seq_length: int = None) :

        if seq_length is None and self.max_sentence_length is not None:
            seq_length = self.max_sentence_length

        if seq_length is None:
            seq_length = max([len(self.text_tokenizer.tokenize(i)) for i in samples])

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position



        tokenizers_result = self.text_tokenizer.encode(samples, maxlen=seq_length)
        return tokenizers_result


    def inverse_transform(self,
                          labels: Union[List[List[int]], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> List[List[str]]:
        result = []
        for index, seq in enumerate(labels):
            labels_ = []
            for idx in seq:
                labels_.append(self.text_tokenizer.id_to_token(idx))
            if lengths is not None:
                labels_ = labels_[1:lengths[index] + 1]
            else:
                labels_ = labels_[1:-1]
            result.append(labels_)
        return result

    def get_max_seq_length_from_corpus(self,
                                   generators: List[CorpusGenerator],
                                   cover_rate: float = 0.95) -> int:
        """
        Calculate proper sequence length according to the corpus

        Args:
            generators:
            use_label:
            cover_rate:

        Returns:

        """
        seq_lens = []
        for gen in generators:
            for (sentence, _) in tqdm.tqdm(gen, desc="Calculating sequence length"):
                seq_lens.append(len(self.text_tokenizer.tokenize(sentence)))
        if cover_rate == 1.0:
            target_index = -1
        else:
            target_index = int(cover_rate * len(seq_lens))
        sequence_length = sorted(seq_lens)[target_index]
        logger.debug(f'Calculated sequence length = {sequence_length}')
        return sequence_length



if __name__ == "__main__":
    pass

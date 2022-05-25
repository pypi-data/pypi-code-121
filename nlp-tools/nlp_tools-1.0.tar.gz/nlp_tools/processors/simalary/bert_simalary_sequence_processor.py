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


class BertSimalarySequenceProcessor(ABCSentenceProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(BertSimalarySequenceProcessor, self).to_dict()
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
        super(BertSimalarySequenceProcessor, self).__init__(**kwargs)



    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def transform(self,samples: TextSamplesVar,seq_length: int = None) :

        if seq_length is None and self.max_sentence_length is not None:
            seq_length = self.max_sentence_length

        if seq_length is None:
            seq_length = max([len(self.text_tokenizer.encode(text=sample[0],second_text=sample[1])[0]) for sample in samples])

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position



        tokenids, segment_ids = [],[]
        for (text1,text2) in samples:
            seq_tokenids,seq_segment_ids = self.text_tokenizer.encode(text1,second_text=text2,maxlen=seq_length)
            tokenids.append(seq_tokenids)
            segment_ids.append(seq_segment_ids)


        token_ids = pad_sequences(tokenids, seq_length, padding='post', truncating='post')
        segment_ids = pad_sequences(segment_ids, seq_length, padding='post', truncating='post')
        token_ids = np.array(token_ids)
        segment_ids = np.array(segment_ids)
        return token_ids, segment_ids


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
            for (sentences, _) in tqdm.tqdm(gen.sample(), desc="Calculating sequence length"):
                assert len(sentences) == 2
                seq_lens.append(len(self.text_tokenizer.encode(text=sentences[0],second_text=sentences[1])[0]))
        if cover_rate == 1.0:
            target_index = -1
        else:
            target_index = int(cover_rate * len(seq_lens))
        sequence_length = sorted(seq_lens)[target_index]
        logger.debug(f'Calculated sequence length = {sequence_length}')
        return sequence_length



if __name__ == "__main__":
    pass

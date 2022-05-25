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


class DialogueSequenceProcessor(ABCSentenceProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(DialogueSequenceProcessor, self).to_dict()
        data['config'].update({
        })
        return data

    def __init__(self,
                 return_ner_masking=True,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        self.return_ner_masking = return_ner_masking
        super(DialogueSequenceProcessor, self).__init__(**kwargs)



    def update_length_info(self,embedding_max_position=512,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def transform(self,samples: TextSamplesVar,seq_length: int = None) :

        if seq_length is None and self.max_sentence_length is not None:
            seq_length = self.max_sentence_length/2

        if seq_length is None:
            seq_length = int(self.embedding_max_position/4)
        elif self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position




        ner_masking = []
        tokenids = []
        segment_ids = []

        for seq in samples:
            sub_tokens_id = []
            sub_segment_id = []
            sub_ner_masking = []
            start_position = 0
            for index, sub_seqn in enumerate(seq):
                if "$$"  in sub_seqn:
                    split_list = sub_seqn.split("$$")
                    sub_seqn = "".join(split_list)

                    start_entity = start_position+len(split_list[0])
                    end_entity = start_position+len(split_list[0])+len(split_list[1])
                    for i in range(start_entity,end_entity):
                        sub_ner_masking.append(i)
                    # sub_ner_masking.append(start_position+len(split_list[0]))
                    # sub_ner_masking.append(start_position+len(split_list[0])+len(split_list[1])-1)
                seq_tokenids,seq_segment_ids = self.text_tokenizer.encode(sub_seqn,maxlen=seq_length)
                if index == 0:
                    sub_tokens_id.extend(seq_tokenids)
                    sub_segment_id.extend(seq_segment_ids)
                    start_position += len(seq_tokenids)
                else:
                    sub_tokens_id.extend(seq_tokenids[1:])
                    sub_segment_id.extend(seq_segment_ids[1:])
                    start_position += len(seq_tokenids) - 1

            tokenids.append(sub_tokens_id)
            segment_ids.append(sub_segment_id)
            ner_masking.append(sub_ner_masking)



        token_ids = pad_sequences(tokenids, seq_length, padding='post', truncating='post')
        segment_ids = pad_sequences(segment_ids, seq_length, padding='post', truncating='post')
        ner_masking_ids = pad_sequences(ner_masking, max([len(i) for i in ner_masking]), padding='post', truncating='post')
        token_ids = np.array(token_ids)
        segment_ids = np.array(segment_ids)
        ner_masking_ids = np.array(ner_masking_ids)

        return token_ids,segment_ids,ner_masking_ids




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
        return 512



if __name__ == "__main__":
    pass

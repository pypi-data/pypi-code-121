# encoding: utf-8


import collections
import operator
from typing import Dict, List, Any, Optional, Union

import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nlp_tools.generators import CorpusGenerator
from nlp_tools.logger import logger
from nlp_tools.processors.abc_sentence_processor import ABCSentenceProcessor
from nlp_tools.types import TextSamplesVar
import tqdm
import re


class HierarchicalSequenceProcessor(ABCSentenceProcessor):
    """
    hierrarchical_attention_networks处理相关类，需要吧一段文本根据句号，逗号等分割城多个短句
    """



    def __init__(self,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(HierarchicalSequenceProcessor, self).__init__(**kwargs)



    def transform(self,samples: TextSamplesVar,seq_length: int = None,doc_length:int = None) :

        split_char = "，|。|！|？"
        split_samples = []

        for sample in samples:
            split_list = re.split(split_char,sample)
            split_list = [i for i in split_list if i.strip()!=""]

            split_samples.append(split_list)


        if seq_length is None and self.max_sentence_length is not None:
            seq_length = self.max_sentence_length
        #seq_length = 50

        if seq_length is None:
            seq_length = np.max([max([len(self.text_tokenizer.tokenize(i)) for i  in j]) for j in split_samples])

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position



        doc_length = 20


        tokenids = []
        for doc_seq in split_samples:
            item = []
            sub_doc_masking = []
            for seq in doc_seq:
                seq_tokenids,seq_segment_ids = self.text_tokenizer.encode(seq,maxlen=seq_length)
                if len(seq_tokenids) > seq_length:
                    seq_tokenids = seq_tokenids[:seq_length]
                else:
                    seq_tokenids += [0] * (seq_length - len(seq_tokenids))
                #seq_tokenids = pad_sequences(seq_tokenids, seq_length, padding='post', truncating='post')
                item.append(seq_tokenids)
                sub_doc_masking.append(1)



            if len(item) < doc_length:
                for _ in range(doc_length - len(item)):
                    item.append([0 for _ in range(seq_length)])
                    sub_doc_masking.append(0)
            tokenids.append(item)





        token_ids = np.array(tokenids)
        token_ids = np.reshape(token_ids, (-1, doc_length , seq_length))

        #segment_ids = np.zeros_like(token_ids)
        return token_ids


    def inverse_transform(self,
                          labels: Union[List[List[int]], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> List[List[str]]:
        raise NotImplementedError("暂时没有实现！！")


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
            for (sentence, _) in tqdm.tqdm(gen.sample(), desc="Calculating sequence length"):
                seq_lens.append(len(self.text_tokenizer.tokenize(sentence)))
        if cover_rate == 1.0:
            target_index = -1
        else:
            target_index = int(cover_rate * len(seq_lens))
        sequence_length = sorted(seq_lens)[target_index]
        logger.debug(f'Calculated sequence length = {sequence_length}')
        return sequence_length

    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length





if __name__ == "__main__":
    pass

# encoding: utf-8
from abc import ABC
from typing import Dict, List, Any, Optional, Union
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nlp_tools.generators import CorpusGenerator
from nlp_tools.processors.abc_sentence_processor import ABCSentenceProcessor
from nlp_tools.types import TextSamplesVar
from nlp_tools.utils import list_utils
import re


class DialogueSequenceProcessor(ABCSentenceProcessor, ABC):
    """Generic processors for the sequence samples."""

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

    def update_length_info(self, embedding_max_position=512, max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def transform(self, samples: TextSamplesVar, seq_length: int = None):
        ner_masking = []

        clean_seqs = []
        for seq in samples:
            sub_ner_masking = []
            start_position = 0
            new_seq = []

            # 每句话都是以D: 或者S:开头，代表相应的角色，现在默认删除，后面可以根据角色吧toke_type设置不同的
            seq = [re.sub("^.{0,1}\:", "", sentence) for sentence in seq]
            for index, sub_seq in enumerate(seq):
                if "$$" in sub_seq:
                    split_tokens = sub_seq.split("$$")
                    sub_seq = sub_seq.replace("$$","")
                    pre_tokenized_seq = []
                    for item in split_tokens:
                        pre_tokenized_seq.extend(self.text_tokenizer.tokenize(item))
                    tokenized_seq = self.text_tokenizer.tokenize(sub_seq)

                    # 如果两次分词结果不一样，说明$$之间的关键词有问题，直接pass(因为关键词是直接基于字符匹配的，可能匹配到部分)
                    if not list_utils.check_list_same(pre_tokenized_seq, tokenized_seq):
                        sub_ner_masking.append(0)
                    else:
                        start_entity = len(self.text_tokenizer.tokenize(split_tokens[0])) + start_position
                        if index == 0:
                            # 如果是第一个位置，则要加上[cls]这个特殊词的位置
                            start_entity += 1
                        if start_entity >= seq_length or start_entity + len(self.text_tokenizer.tokenize(split_tokens[1])) >= seq_length:
                            sub_ner_masking.append(0)
                        else:
                            for i in range(start_entity, start_entity + len(self.text_tokenizer.tokenize(split_tokens[1]))):
                                sub_ner_masking.append(i)

                tokenized_seq = self.text_tokenizer.tokenize(sub_seq, max_len=seq_length, add_special_tokens=True)
                if index != 0:
                    tokenized_seq = tokenized_seq[1:]

                start_position += len(tokenized_seq)
                new_seq.extend(tokenized_seq)
            ner_masking.append(sub_ner_masking)
            clean_seqs.append(new_seq)

        tokenizers_result = self.text_tokenizer.encode(clean_seqs, maxlen=seq_length,is_split_into_words=True,add_special_tokens=False)

        ner_masking_ids = pad_sequences(ner_masking, max([len(i) for i in ner_masking]), padding='post',
                                        truncating='post')
        ner_masking_ids = np.array(ner_masking_ids)
        if self.return_ner_masking:
            return tokenizers_result + [ner_masking_ids]
        else:
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
            cover_rate:

        Returns:

        """
        return 512


if __name__ == "__main__":
    pass

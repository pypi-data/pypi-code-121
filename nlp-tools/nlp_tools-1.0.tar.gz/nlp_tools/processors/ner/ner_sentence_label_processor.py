# encoding: utf-8


import collections
import operator
from typing import Dict, List, Any, Union

import numpy as np
import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nlp_tools.generators import CorpusGenerator
from nlp_tools.logger import logger
from nlp_tools.processors.abc_label_processor import ABCLabelProcessor
from nlp_tools.utils.ner_utils import get_entities
from tensorflow.keras.utils import to_categorical


class NerSentenceLabelProcessor(ABCLabelProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(NerSentenceLabelProcessor, self).to_dict()
        data['config'].update({
            'embedding_max_position': self.embedding_max_position,
            'max_sentence_length':self.max_sentence_length,
            "tag_mode":self.tag_mode,
            "return_one_hot":self.return_one_hot
        })
        return data

    def __init__(self,
                 tag_mode='BI',
                 return_onehot = False,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(NerSentenceLabelProcessor, self).__init__(**kwargs)
        self._initial_vocab_dic = {
            "O": 0
        }
        self.tag_mode = tag_mode
        self.return_one_hot = return_onehot

    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def build_vocab_generator(self,generators) -> None:
        if not self.vocab2idx:
            tag_set = set()
            vocab2idx = self._initial_vocab_dic
            for gen in generators:
                for (_, label_list) in tqdm.tqdm(gen.sample(), desc="Preparing label dict"):
                    ## ner任务下面，label 应该是一个list
                    assert type(label_list) == list
                    for sublabel in label_list:
                        label = sublabel[2]
                        if label not in tag_set:
                            tag_set.add(label)


            for label in list(set(tag_set)):
                if self.tag_mode == "BI":
                    vocab2idx["B-" + label] = len(vocab2idx)
                    vocab2idx["I-" + label] = len(vocab2idx)
                else:
                    raise ValueError("不支持的tag_mode")
            self.vocab2idx = vocab2idx
            self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])




    def transform(self,samples,seq_length=None):
        if not seq_length:
            seq_length = self.max_sentence_length

        if not seq_length:
            seq_length = self.embedding_max_position

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position

        labels_numpy = np.zeros((len(samples), seq_length))

        for index, sample_labels in enumerate(samples):
            for sub_label in sample_labels:
                (start_position, end_position, label_type) = sub_label
                if start_position >= seq_length:
                    continue

                if end_position >= seq_length:
                    continue

                labels_numpy[index, start_position] = self.vocab2idx["B-" + label_type]
                if self.tag_mode == "BI":
                    for sub_index in range(start_position +1,end_position+1):
                        labels_numpy[index, sub_index] = self.vocab2idx["I-" + label_type]
        if self.return_one_hot:
            labels_numpy = to_categorical(labels_numpy,num_classes=self.vocab_size)
        return labels_numpy

    def inverse_transform(self,
                          labels: Union[List[List[int]], np.ndarray],
                          lengths: List[int] = None,
                          mapping_list = None ):
        result = []
        for index, (label, sequece_length) in enumerate(zip(labels, lengths)):
            label = label[:sequece_length]
            if len(np.shape(label)) == 2:
                label = np.argmax(label,axis=-1)
            label = [self.idx2vocab[i] for i in label]

            entities = get_entities(label)

            # 将position映射为真实的句子中的index，因为之前由于分词以后，会影响index
            format_entities = []
            for (tagname,start,end) in entities:
                if mapping_list:
                    if mapping_list[index][start] and mapping_list[index][end]:
                        format_entities.append((mapping_list[index][start][0], mapping_list[index][end][-1], tagname))
                else:
                    format_entities.append((start + 1, end + 1, tagname))

            result.append(format_entities)
        return result





if __name__ == "__main__":
    pass

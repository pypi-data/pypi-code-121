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
from nlp_tools.types import TextSamplesVar


class GlobalPointerLabelProcessor(ABCLabelProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(GlobalPointerLabelProcessor, self).to_dict()
        data['config'].update({
            'embedding_max_position': self.embedding_max_position,
            'max_sentence_length':self.max_sentence_length
        })
        return data

    def __init__(self,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(GlobalPointerLabelProcessor, self).__init__(**kwargs)
        self._initial_vocab_dic = {
        }



    def update_length_info(self,embedding_max_position=None,max_sentence_length=None):
        self.embedding_max_position = embedding_max_position
        self.max_sentence_length = max_sentence_length

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        if not self.vocab2idx:
            vocab2idx = self._initial_vocab_dic
            token2count: Dict[str, int] = {}
            for gen in generators:
                for (_, label_list) in tqdm.tqdm(gen.sample(), desc="Preparing label dict"):
                    ## ner任务下面，label 应该是一个list
                    assert type(label_list) == list
                    for sublabel in label_list:
                        label = sublabel[2]
                        count = token2count.get(sublabel[2], 0)
                        token2count[label] = count + 1

            sorted_token2count = sorted(token2count.items(),
                                        key=operator.itemgetter(1),
                                        reverse=True)
            token2count = collections.OrderedDict(sorted_token2count)
            for token, token_count in token2count.items():
                vocab2idx[token] = len(vocab2idx)
            self.vocab2idx = vocab2idx
            self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])





    def transform(self,samples,seq_length=None) -> np.ndarray:
        if not seq_length:
            seq_length = self.max_sentence_length

        if not seq_length:
            seq_length = self.embedding_max_position

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position

        labels_numpy = np.zeros((len(samples),len(self.vocab2idx), seq_length, seq_length))
        for index, sample_labels in enumerate(samples):
            for sub_label in sample_labels:
                (start_position, end_position, label_type) = sub_label
                label2index = self.vocab2idx[label_type]

                if start_position >= seq_length:
                    continue

                if end_position >= seq_length:
                    continue

                labels_numpy[index,label2index,start_position,end_position] = 1
        return labels_numpy

    def inverse_transform(self, labels, lengths=None, mapping_list=None, threshold=0, return_max_entity=False):
        result = []
        if return_max_entity:
            for index,(scores ,sequece_length )in enumerate(zip(labels,lengths)):
                entities = []
                scores = scores[:,:sequece_length,:sequece_length]
                scores[:, [0, -1]] -= np.inf  # 去除添加的[cls]和【seq】这一行的判断
                scores[ :, :, [0, -1]] -= np.inf  # 去除每一行的首尾添加的[cls]和【seq】
                scores = np.transpose(scores,[1,2,0])
                max_scores = np.max(scores,axis=-1)
                for (start,end,l) in zip(*np.where(scores > threshold)):
                    if max_scores[start, end] == scores[start, end, l]:
                        if mapping_list:
                            entities.append(
                                (mapping_list[index][start][0], mapping_list[index][end][-1], self.idx2vocab[l])
                            )
                        else:
                            # 如果mapping为空，start,end都要减一，因为在tokenizer的时候增加了[cls]，所以这边位置要减1
                            entities.append(
                                (start - 1, end - 1, self.idx2vocab[l])
                            )
                result.append(entities)

        else:
            for index,(scores ,sequece_length )in enumerate(zip(labels,lengths)):
                entities = []
                scores = scores[:,:sequece_length,:sequece_length]
                scores[:, [0, -1]] -= np.inf  # 去除添加的[cls]和【seq】这一行的判断
                scores[ :, :, [0, -1]] -= np.inf  # 去除每一行的首尾添加的[cls]和【seq】
                for l, start, end in zip(*np.where(scores > threshold)):
                    if mapping_list:
                        entities.append(
                            (mapping_list[index][start][0], mapping_list[index][end][-1], self.idx2vocab[l])
                        )
                    else:
                        # 如果mapping为空，start,end都要减一，因为在tokenizer的时候增加了[cls]，所以这边位置要减1
                        entities.append(
                            (start - 1, end - 1, self.idx2vocab[l])
                        )
                result.append(entities)
        return result





if __name__ == "__main__":
    import numpy as np
    a = np.arange(48).reshape((3,4,4))
    a = a.astype(np.float64)
    print(a)
    b = np.where(a > 3)
    print(b)

    for l, start, end in zip(*np.where(a > 3)):
        print(l,start,end)

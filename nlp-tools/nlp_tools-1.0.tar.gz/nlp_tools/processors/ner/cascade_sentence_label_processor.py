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


class CascadeSentenceLabelProcessor(ABCLabelProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(CascadeSentenceLabelProcessor, self).to_dict()
        data['config'].update({
            'embedding_max_position': self.embedding_max_position,
            'max_sentence_length':self.max_sentence_length,
            "segment_mode":self.segment_mode
        })
        return data

    def __init__(self,
                 segment_mode='BIES',
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(CascadeSentenceLabelProcessor, self).__init__(**kwargs)
        self._initial_vocab_dic = {
            "O":0
        }
        self.segment_mode = segment_mode
        if self.segment_mode == "BIES":
            self.segment_labels = {
                "O":0,
                "B":1,
                "I":2,
                "E":3,
                "S":4,
            }
        else:
            self.segment_labels = {
                'O':0,
                "B":1,
                "I":2,
            }
        self.segmetn_idx_2_label = {v:k for k,v in self.segment_labels.items()}


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
                vocab2idx[label] = len(vocab2idx)
            self.vocab2idx = vocab2idx
            self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])




    def transform(self,samples,seq_length=None) -> np.ndarray:
        if not seq_length:
            seq_length = self.max_sentence_length

        if not seq_length:
            seq_length = self.embedding_max_position

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position

        labels_numpy = np.zeros((len(samples), seq_length))
        segment_numpy = np.zeros((len(samples), seq_length))

        for index, sample_labels in enumerate(samples):
            for sub_label in sample_labels:
                (start_position, end_position, label_type) = sub_label
                if start_position >= seq_length:
                    continue

                if end_position >= seq_length:
                    continue

                labels_numpy[index, start_position:end_position+1] = self.vocab2idx[ label_type]
                if self.segment_mode == 'BI':
                    segment_numpy[index,start_position] = self.segment_labels['B']
                    for i in range(start_position+1,end_position+1):
                        segment_numpy[index,i] = self.segment_labels['I']
                else:
                    if end_position - start_position == 0:
                        segment_numpy[index, start_position] = self.segment_labels['S']
                    else:
                        segment_numpy[index, start_position] = self.segment_labels['B']
                        for i in range(start_position + 1, end_position + 1):
                            segment_numpy[index,i] = self.segment_labels['I']
                        segment_numpy[index,end_position] = self.segment_labels['E']

        return (segment_numpy,labels_numpy)

    def inverse_transform(self,
                          labels_and_segment,
                          lengths: List[int] = None,
                          mapping_list = None,**kwargs ):
        preds,pred_labels = labels_and_segment

        preds = [[self.segmetn_idx_2_label[i] for i in p] for p in preds]
        pred_labels = [ [self.idx2vocab[i] for i in p] for p in pred_labels]

        # temp_labels =[]
        # for p,q in zip(preds,pred_labels):
        #     temp_labels.append(self.trans_label(p,q))
        temp_labels = self.trans_label(preds,pred_labels)

        result = []
        for index, (label, sequece_length) in enumerate(zip(temp_labels, lengths)):
            label = label[:sequece_length]
            if len(np.shape(label)) == 2:
                label = np.argmax(label,axis=-1)
            #label = [self.idx2vocab[i] for i in label]

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

    def trans_label(self,segment_labels_id, attr_labels_id):
        """
        答案拼接2种方式：
        例子：
        bmeo：[B, M, E]
        attr: [LOC, LOC, ORG]
        1. 实体词 bmeo 与 attr 的属性全都对应起来
        result: [B-LOC, M-LOC, E-ORG]
        2. 实体词 bmeo 的e所对应的attr作为该实体的attr
        result: [B-ORG, M-ORG, E-ORG]
        目前采用第一种
        """
        std_labels = []
        for index, bmeo_line in enumerate(segment_labels_id):
            bmeo_attr_label = []
            attr_line = attr_labels_id[index]
            for item in list(zip(bmeo_line, attr_line)):
                bmeo_id = item[0]
                attr_id = item[1]
                if bmeo_id == "O":
                    bmeo_attr = "O"
                else:
                    bmeo_attr = bmeo_id + "-" + attr_id
                bmeo_attr_label.append(bmeo_attr)
            std_labels.append(bmeo_attr_label)
        # print("std labels")
        # print(std_labels)
        return std_labels





if __name__ == "__main__":
    pass

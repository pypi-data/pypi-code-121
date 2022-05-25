# encoding: utf-8
from typing import Dict, List, Any, Union

import numpy as np
import tqdm

from nlp_tools.processors.abc_label_processor import ABCLabelProcessor
from nlp_tools.utils.ner_utils import get_entities
from nlp_tools.utils.ner_utils import span_extract_item



class SpanSentenceLabelProcessor(ABCLabelProcessor):
    """
    Generic processors for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(SpanSentenceLabelProcessor, self).to_dict()
        data['config'].update({
            'embedding_max_position': self.embedding_max_position,
            'max_sentence_length':self.max_sentence_length,
        })
        return data

    def __init__(self,
                 **kwargs: Any) -> None:
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(SpanSentenceLabelProcessor, self).__init__(**kwargs)
        self._initial_vocab_dic = {
            "O": 0
        }


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




    def transform(self,samples,seq_length):
        if not seq_length:
            seq_length = self.max_sentence_length

        if not seq_length:
            seq_length = self.embedding_max_position

        if self.embedding_max_position is not None and self.embedding_max_position < seq_length:
            seq_length = self.embedding_max_position

        labels_start = np.zeros((len(samples), seq_length))
        labels_end = np.zeros((len(samples), seq_length))

        for index, sample_labels in enumerate(samples):
            for sub_label in sample_labels:
                (start_position, end_position, label_type) = sub_label
                if start_position >= seq_length:
                    continue

                if end_position >= seq_length:
                    continue

                labels_start[index, start_position] = self.vocab2idx[label_type]
                labels_end[index,end_position] = self.vocab2idx[label_type]
        return (labels_start,labels_end)

    def inverse_transform(self,
                          labels: Union[List[List[int]], np.ndarray],
                          lengths: List[int] = None,
                          mapping_list = None,**kwargs ):
        result = []
        for index, (labels_start,labels_end, sequece_length) in enumerate(zip(labels[0],labels[1], lengths)):


            labels_start = labels_start[:sequece_length]
            labels_end = labels_end[:sequece_length]
            if len(np.shape(labels_start)) == 2:
                labels_start = np.argmax(labels_start,axis=-1)
                labels_end = np.argmax(labels_end, axis=-1)


            # 将position映射为真实的句子中的index，因为之前由于分词以后，会影响index
            format_entities = []

            entities = span_extract_item(labels_start,labels_end)
            for (tag_index,start,end) in entities:
                tagname = self.idx2vocab[tag_index]
                if mapping_list:
                    if mapping_list[index][start] and mapping_list[index][end]:
                        format_entities.append((mapping_list[index][start][0], mapping_list[index][end][-1], tagname))
                else:
                    format_entities.append((start + 1, end + 1, tagname))

            result.append(format_entities)
        return result





if __name__ == "__main__":
    pass

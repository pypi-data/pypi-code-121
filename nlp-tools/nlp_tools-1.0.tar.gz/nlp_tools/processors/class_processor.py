import collections
import operator
from typing import List, Union, Dict, Optional, Any, Tuple

import numpy as np
import tqdm

from nlp_tools.generators import CorpusGenerator
from nlp_tools.processors.abc_label_processor import ABCLabelProcessor
from nlp_tools.types import  TextSamplesVar
from nlp_tools.utils import MultiLabelBinarizer

class ClassificationProcessor(ABCLabelProcessor):

    def to_dict(self) -> Dict[str, Any]:
        data = super(ClassificationProcessor, self).to_dict()
        data['config']['label2id'] = self.vocab2idx
        return data

    def __init__(self,
                 multi_label: bool = False,
                 label2id = None,
                 **kwargs: Any) -> None:

        super(ClassificationProcessor, self).__init__(**kwargs)
        self.vocab2idx = label2id
        self.multi_label = multi_label
        self.multi_label_binarizer = MultiLabelBinarizer(self.vocab2idx)

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        if not self.vocab2idx:
            vocab2idx: Dict[str, int] = {}
            token2count: Dict[str, int] = {}
            for generator in generators:
                if self.multi_label:
                    for (_, label) in tqdm.tqdm(generator.sample(), desc="Preparing classification label vocab dict"):
                        for token in label:
                            count = token2count.get(token, 0)
                            token2count[token] = count + 1
                else:
                    for _, label in tqdm.tqdm(generator.sample(), desc="Preparing classification label vocab dict"):
                        count = token2count.get(label, 0)
                        token2count[label] = count + 1

            sorted_token2count = sorted(token2count.items(),
                                        key=operator.itemgetter(0))
            token2count = collections.OrderedDict(sorted_token2count)

            for token, token_count in token2count.items():
                if token not in vocab2idx:
                    vocab2idx[token] = len(vocab2idx)
            self.vocab2idx = vocab2idx
        self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])
        self.multi_label_binarizer = MultiLabelBinarizer(self.vocab2idx)

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        if self.multi_label:
            return batch_size, len(self.vocab2idx)
        else:
            return (batch_size,)

    def transform(self,
                  samples: TextSamplesVar,
                  *,
                  seq_length: int = None,
                  max_position: int = None,
                  segment: bool = False) -> np.ndarray:
        if self.multi_label:
            sample_tensor = self.multi_label_binarizer.transform(samples)
            return sample_tensor

        sample_tensor = [self.vocab2idx[i] for i in samples]
        return np.array(sample_tensor)

    def inverse_transform(self,  # type: ignore[override]
                          labels: Union[List[int], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> Union[List[List[str]], List[str]]:
        if self.multi_label:
            return self.multi_label_binarizer.inverse_transform(labels,
                                                                threshold=threshold)
        else:
            return [self.idx2vocab[i] for i in labels]


if __name__ == "__main__":
    pass

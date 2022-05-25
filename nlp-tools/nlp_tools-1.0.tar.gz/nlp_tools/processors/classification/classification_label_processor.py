import collections
import operator
from typing import List, Union, Dict, Optional, Any, Tuple

import numpy as np
import tqdm

from nlp_tools.generators import CorpusGenerator
from nlp_tools.processors.abc_label_processor import ABCLabelProcessor
from nlp_tools.types import  TextSamplesVar
from nlp_tools.utils import MultiLabelBinarizer
from tensorflow.keras.utils import to_categorical

class ClassificationLabelProcessor(ABCLabelProcessor):

    def to_dict(self) -> Dict[str, Any]:
        data = super(ClassificationLabelProcessor, self).to_dict()
        return data

    def __init__(self,label_smooth=False,
                 **kwargs: Any) -> None:
        self.label_smooth = label_smooth
        super(ClassificationLabelProcessor, self).__init__(**kwargs)



    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        vocab2idx: Dict[str, int] = {}
        token2count: Dict[str, int] = {}
        for generator in generators:
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
        return (batch_size,)

    def transform(self,
                  samples: TextSamplesVar,
                  *,
                  seq_length: int = None,
                  max_position: int = None,
                  segment: bool = False) -> np.ndarray:
        sample_tensor = [self.vocab2idx[i] for i in samples]

        sample_tensor = to_categorical(sample_tensor,num_classes=len(self.vocab2idx))
        if self.label_smooth:
            sample_tensor = self.smooth_labels(sample_tensor)
        return np.array(sample_tensor)

    def inverse_transform(self,
                          labels: Union[List[int], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> Union[List[List[str]], List[str]]:

        return [self.idx2vocab[i] for i in labels]

    def smooth_labels(self, labels, factor=0.2):
        # smooth the labels
        labels *= (1 - factor)
        labels += (factor / labels.shape[1])

        return labels



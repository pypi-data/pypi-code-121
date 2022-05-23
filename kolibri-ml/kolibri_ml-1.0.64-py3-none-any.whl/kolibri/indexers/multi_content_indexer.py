from typing import Dict, Any

import numpy as np

from kolibri.datasets import get_data
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.indexers.sequence_char_indexer import SequenceCharIndexer
from kolibri.indexers.sequence_indexer import SequenceIndexer


class MultiContentIndexer(BaseIndexer):

    def to_dict(self) -> Dict[str, Any]:
        data = super(MultiContentIndexer, self).to_dict()
        data['config'].update({
            'min_count': self.min_count,
            'content_indexers': [indexer.to_dict() for indexer in self.content_indexers]
        })
        return data

    def __init__(self, min_count=0, **kwargs):
        super(MultiContentIndexer, self).__init__(**kwargs)
        self.content_indexers = []
        self.min_count = min_count

    def build_vocab(self, x_data, y_data):

        for indexer in self.content_indexers:
            indexer.build_vocab(x_data, y_data)

    def transform(self, samples, **kwargs):
        samples_tensors = []
        for indexer in self.content_indexers:
            sample_tensor = []
            for sample in samples:
                trandformed = indexer.transform([sample])
                sample_tensor.append(trandformed[0])
            samples_tensors.append(np.array(sample_tensor))
        return samples_tensors

    def inverse_transform(self, labels, *, lengths=None, **kwargs):
        raise NotImplementedError

    def _override_load_model(self, data):
        self.min_count = data['config']['min_count']
        for l_i in data['config']['content_indexers']:
            self.content_indexers.append(load_data_object(l_i))


if __name__ == "__main__":
    corpus = get_data("snips_intent")
    mti = MultiContentIndexer()
    mti.add_indexer(corpus.X, corpus.y, SequenceIndexer(index=0))
    mti.add_indexer(corpus.X, corpus.y, SequenceCharIndexer(index=0))
    x = mti.transform(corpus.y)
    pass

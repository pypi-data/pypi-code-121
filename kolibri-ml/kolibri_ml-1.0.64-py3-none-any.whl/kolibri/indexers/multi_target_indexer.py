from typing import Dict, Any

import numpy as np

from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.indexers.label_indexer import LabelIndexer
from kolibri.indexers.sequence_indexer import SequenceIndexer


class MultiTargetIndexer(BaseIndexer):

    def to_dict(self) -> Dict[str, Any]:
        data = super(MultiTargetIndexer, self).to_dict()
        data['config'].update({
            'min_count': self.min_count,
            'label_indexers': [indexer.to_dict() for indexer in self.label_indexers]
        })
        return data

    def __init__(self, min_count=0, **kwargs):
        super(MultiTargetIndexer, self).__init__(**kwargs)
        self.label_indexers = []
        self.min_count = min_count

    def add_indexer(self, generators):
        x, y = generators[0][0]

        for i, target in enumerate(y):
            if isinstance(target, list):
                label_indexer = SequenceIndexer(build_vocab_from_labels=True, index=i)
            else:
                label_indexer = LabelIndexer(index=i)

            label_indexer.build_vocab_generator(generators)
            self.label_indexers.insert(0, label_indexer)

    def build_vocab(self, x_data, y_data):

        for indexer in self.label_indexers:
            indexer.build_vocab(x_data, y_data)

    def transform(self, samples, **kwargs):
        samples_tensors = []
        for indexer in self.label_indexers:
            sample_tensor = []
            for sample in samples:
                trandformed = indexer.transform([sample])
                sample_tensor.append(trandformed[0])
            samples_tensors.append(np.array(sample_tensor))
        return samples_tensors

    def inverse_transform(self, labels, *, lengths=None, **kwargs):
        invesed_labels = []

        for i, indexer in enumerate(self.label_indexers):
            invesed_labels.append(indexer.inverse_transform(labels[i]))

        return invesed_labels

    def _override_load_model(self, data):
        self.min_count = data['config']['min_count']
        for l_i in data['config']['label_indexers']:
            self.label_indexers.append(load_data_object(l_i))


if __name__ == "__main__":
    # corpus=SnipsIntentCorpus()
    # mti=MultiTargetIndexer()
    # mti.build_vocab()
    # x=mti.transform(corpus.y)
    pass

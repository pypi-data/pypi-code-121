import unittest

import numpy as np

from kolibri.data.text.corpus import SnipsIntentCorpus
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers import LabelIndexer, SequenceIndexer
from kolibri.indexers.multi_target_indexer import MultiTargetIndexer
from kolibri.tokenizer import WordTokenizer

tokenizer = WordTokenizer()


class TestMultiTargetIndexer(unittest.TestCase):
    def test_indexer(self):
        corpus = SnipsIntentCorpus()
        y_set = corpus.y[:10]
        x_set = corpus.X[:10]
        indexer = MultiTargetIndexer()
        indexer.label_indexers = [LabelIndexer(index=1), SequenceIndexer(build_vocab_from_labels=True, index=0)]
        indexer.build_vocab(x_set, y_set)
        transformed_idx = indexer.transform(y_set)

        info_dict = indexer.to_dict()

        p2: MultiTargetIndexer = load_data_object(info_dict)
        transformed_idx2 = p2.transform(y_set)
        i_transformed_idx = np.array(p2.inverse_transform(transformed_idx))
        assert (transformed_idx[0] == transformed_idx2[0]).all()
        assert (transformed_idx[1] == transformed_idx2[1]).all()
        for i in range(10):
            print(y_set[i][0], i_transformed_idx[1][i])
            assert y_set[i][0] == i_transformed_idx[1][i][:len(y_set[i][0])]
            assert y_set[i][1] == i_transformed_idx[0][i]

            # assert (idx[0]==transformed_idx2[i][0]).all()
            # assert idx[1] == transformed_idx2[i][1]
            # print(y_set[i][0], '\t', i_transformed_idx[i][0])
            # assert y_set[i]==i_transformed_idx[i]


if __name__ == "__main__":
    pass

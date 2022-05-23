import unittest

#from kolibri.data.text.corpus import SnipsIntentCorpus
from kolibri.datasets import get_data
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers import SequenceCharIndexer, SequenceIndexer
from kolibri.indexers.multi_content_indexer import MultiContentIndexer
from kolibri.tokenizers import WordTokenizer

tokenizer = WordTokenizer()


class TestMultiContentIndexer(unittest.TestCase):
    def test_indexer(self):
        corpus = get_data("snips_intent")
        y_set = corpus.y[:10]
        x_set = corpus.X[:10]
        indexer = MultiContentIndexer()
        indexer.content_indexers = [SequenceIndexer(index=0), SequenceCharIndexer(index=0)]
        indexer.build_vocab(x_set, y_set)
        transformed_idx = indexer.transform(y_set)

        info_dict = indexer.to_dict()

        p2: MultiContentIndexer = load_data_object(info_dict)
        transformed_idx2 = p2.transform(y_set)

        for i, idx in enumerate(transformed_idx):
            assert (idx[0] == transformed_idx2[i][0]).all()
            assert (idx[1] == transformed_idx2[i][1]).all()


if __name__ == "__main__":
    pass

import os
import random
import tempfile
import time
import unittest

from kolibri.datasets import get_data
from kolibri.backend.tensorflow.tasks.text.classification import BiGRU_Model
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers import SequenceIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)

from kolibri.tokenizers import WordTokenizer

sample_count = 50


class TestDefaultEmbedding(unittest.TestCase):

    def build_embedding(self):
        embedding = DefaultEmbedding()
        return embedding

    def test_base_cases(self):
        tokenizer = WordTokenizer()
        embedding = self.build_embedding()
        corpus = get_data('viva')[:500]
        x=corpus["en"]
        y = corpus['sector']
        x = tokenizer.transform(x)
        indexer = SequenceIndexer()
        indexer.build_vocab(x, y)
        embedding.setup_text_processor(indexer)

        samples = random.sample(x, sample_count)
        res = embedding.embed(samples)
        max_len = max([len(i) for i in x])

        if embedding.max_position is not None:
            max_len = embedding.max_position

        assert res.shape == (len(samples), max_len, embedding.embedding_size)

        # Test Save And Load
        embed_dict = embedding.to_dict()
        embedding2 = load_data_object(embed_dict)
        embedding2.setup_text_processor(indexer)
        assert embedding2.embed(samples).shape == (len(samples), max_len, embedding.embedding_size)

    def test_with_model(self):
        tokenizer = WordTokenizer()

        corpus = ConsumerComplaintsCorpus()

        x, y = corpus.get_data(nb_samples=500)
        x = tokenizer.transform(x)
        embedding = self.build_embedding()

        model = BiGRU_Model(embedding=embedding)
        model.build_model(x, y)
        model_summary = []
        embedding.embed_model.summary(print_fn=lambda x: model_summary.append(x))
        logger.debug('\n'.join(model_summary))

        model.fit(x, y, epochs=1)

        model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
        model.save(model_path)


if __name__ == "__main__":
    unittest.main()

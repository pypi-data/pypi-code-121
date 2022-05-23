import os
import unittest

from tensorflow.keras.utils import get_file

from kolibri.backend.tensorflow.embeddings import WordEmbedding
from kolibri.settings import DATA_PATH
from tests.dnn.text.test_embeddings.test_default_embedding import TestDefaultEmbedding

sample_w2v_path = os.path.join(get_file("text",
                                        "https://www.dropbox.com/s/0lducehaevowqpm/test.tar.gz?dl=1",
                                        cache_dir=DATA_PATH,
                                        cache_subdir='test',
                                        untar=True), 'sample_w2v.txt')


class TestWordEmbedding(TestDefaultEmbedding):

    def build_embedding(self):
        embedding = WordEmbedding(sample_w2v_path)
        return embedding


if __name__ == '__main__':
    unittest.main()

import unittest

import tests.dnn.text.test_classification.test_bi_lstm_model as base
from kolibri.backend.tensorflow.tasks.text.classification import BiGRU_Model
from kolibri.backend.tensorflow.embeddings import WordEmbedding
from tests.dnn.text.test_embeddings.test_word_embedding import sample_w2v_path


class TestBiGRU_Model(base.TestBiLSTM_Model):
    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 2
        cls.TASK_MODEL_CLASS = BiGRU_Model
        cls.w2v_embedding = WordEmbedding(sample_w2v_path)


if __name__ == "__main__":
    unittest.main()

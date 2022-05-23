import unittest

import tests.dnn.text.test_classification.test_bi_lstm_model as base
from kolibri.backend.tensorflow.tasks.text.classification import CNN_GRU_Model
from kolibri.backend.tensorflow.embeddings import WordEmbedding
from tests.dnn.text.test_embeddings.test_word_embedding import sample_w2v_path


class TestCNN_GRU_Model(base.TestBiLSTM_Model):
    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 1
        cls.TASK_MODEL_CLASS = CNN_GRU_Model
        cls.w2v_embedding = WordEmbedding(sample_w2v_path)


if __name__ == "__main__":
    unittest.main()

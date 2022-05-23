import unittest

import tests.dnn.text.test_classification.test_bi_lstm_model as base
from kolibri.backend.tensorflow.tasks.text.classification.cnn_attention_model import CNN_Attention_Model
from kolibri.backend.tensorflow.embeddings import WordEmbedding
from tests.dnn.text.test_embeddings.test_word_embedding import sample_w2v_path


class TestCnnAttention_Model(base.TestBiLSTM_Model):
    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 1
        cls.TASK_MODEL_CLASS = CNN_Attention_Model
        cls.w2v_embedding = WordEmbedding(sample_w2v_path)

    # def test_multi_label(self):
    #     super(TestCnnAttention_Model, self).test_multi_label()


if __name__ == "__main__":
    unittest.main()

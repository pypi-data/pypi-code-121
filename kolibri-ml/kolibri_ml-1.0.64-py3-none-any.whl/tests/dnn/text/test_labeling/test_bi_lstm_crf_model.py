import unittest

import tests.dnn.text.test_labeling.test_bi_lstm_model as base
from kolibri.backend.tensorflow.tasks.text.labeling import BiLSTM_CRF_Model


class TestCNN_LSTM_Model(base.TestBiLSTM_Model):

    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 1
        cls.TASK_MODEL_CLASS = BiLSTM_CRF_Model


if __name__ == "__main__":
    unittest.main()

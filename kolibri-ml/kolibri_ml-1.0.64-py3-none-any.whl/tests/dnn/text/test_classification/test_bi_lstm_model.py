import os
import tempfile
import time
import unittest

#from kolibri.data.text.corpus import ConsumerComplaintsCorpus
from kolibri.datasets import get_data
from kolibri.backend.tensorflow.tasks.text.classification import BiLSTM_Model
from kolibri.backend.tensorflow.embeddings import WordEmbedding
from kolibri.tokenizers import WordTokenizer
from tests.dnn.text.test_embeddings.test_word_embedding import sample_w2v_path


class TestBiLSTM_Model(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 2
        cls.TASK_MODEL_CLASS = BiLSTM_Model
        cls.w2v_embedding = WordEmbedding(sample_w2v_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.w2v_embedding = None

    def test_basic_use(self):
        tokenizer = WordTokenizer()
        model = self.TASK_MODEL_CLASS(sequence_length=20)
        model.hyper_parameters['epochs'] = self.EPOCH_COUNT
        corpus = get_data('kiva')[0:100]
        train_x=corpus["en"].values
        train_y = corpus["sector"].values
        valid_x, valid_y = train_x, train_y
        train_x = tokenizer.transform(train_x)
        valid_x = tokenizer.transform(valid_x)
        model.fit(train_x,
                  train_y,
                  x_validate=valid_x,
                  y_validate=valid_y)

        model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
        original_y = model.predict(train_x[50:70])
        model.save(model_path)

        # Make sure use sigmoid as activation function
        assert model.tf_model.layers[-1].activation.__name__ == 'softmax'

        del model
        new_model = self.TASK_MODEL_CLASS.load_model(model_path)
        new_model.tf_model.summary()
        new_y = new_model.predict(train_x[50:70])
        assert (new_y[0] == original_y[0]).all()

        report = new_model.evaluate(valid_x, valid_y)
        for key in ['precision', 'recall', 'f1-score', 'support', 'detail']:
            assert key in report

        # Make sure use sigmoid as activation function
        assert new_model.tf_model.layers[-1].activation.__name__ == 'softmax'

    # def test_multi_label(self):
    #     corpus=ConsumerComplaintsCorpus()
    #     model = self.TASK_MODEL_CLASS(sequence_length=20, multi_label=True)
    #     x, y = corpus.get_data(nb_samples=500)
    #     model.fit(x, y, epochs=self.EPOCH_COUNT)
    #
    #     model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
    #     original_y = model.predict(x[:20])
    #     model.save(model_path)
    #
    #     # Make sure use sigmoid as activation function
    #     assert model.tf_model.layers[-1].activation.__name__ == 'sigmoid'
    #     del model
    #
    #     new_model = self.TASK_MODEL_CLASS.load_model(model_path)
    #     new_model.tf_model.summary()
    #     new_y = new_model.predict(x[:20])
    #
    #     assert new_y == original_y
    #
    #     report = new_model.evaluate(x, y)
    #     for key in ['precision', 'recall', 'f1-score', 'support', 'detail']:
    #         assert key in report
    #
    #     # Make sure use sigmoid as activation function
    #     assert new_model.tf_model.layers[-1].activation.__name__ == 'sigmoid'

    def test_with_word_embedding(self):
        tokenizer = WordTokenizer()
        model = self.TASK_MODEL_CLASS(embedding=self.w2v_embedding)
        model.hyper_parameters['epochs'] = self.EPOCH_COUNT
        corpus = ConsumerComplaintsCorpus()
        train_x, train_y = corpus.get_data(nb_samples=500)
        valid_x, valid_y = train_x, train_y
        train_x = tokenizer.transform(train_x)
        valid_x = tokenizer.transform(valid_x)

        model.fit(train_x,
                  train_y,
                  x_validate=valid_x,
                  y_validate=valid_y)

        model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
        _ = model.predict(valid_x[:20])
        model.save(model_path)

        del model

        new_model = self.TASK_MODEL_CLASS.load_model(model_path)
        new_model.tf_model.summary()
        _ = new_model.predict(valid_x[:20])


if __name__ == '__main__':
    unittest.main()

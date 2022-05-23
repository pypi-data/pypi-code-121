import os
import tempfile
import time
import unittest
from typing import Type

from kolibri.backend.tensorflow.tasks.text.labeling import BiLSTM_Model, BaseLabelingModel
from kolibri.backend.tensorflow.embeddings import WordEmbedding
from tests.dnn.text.test_embeddings.test_word_embedding import sample_w2v_path


class TestBiLSTM_Model(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 1
        cls.TASK_MODEL_CLASS: Type[BaseLabelingModel] = BiLSTM_Model

    def test_basic_use(self):
        model = self.TASK_MODEL_CLASS()
        from kolibri.data.text.corpus import CONLL2003ENCorpus
        corpus = CONLL2003ENCorpus()

        train_x, train_y = corpus.get_data(nb_samples=500)

        model.fit(train_x,
                  train_y,
                  epochs=self.EPOCH_COUNT)

        model_path = os.path.join(tempfile.gettempdir(), str(time.time()))
        original_y = model.predict(train_x[:20])
        model.save(model_path)
        del model

        new_model = self.TASK_MODEL_CLASS.load_model(model_path)
        new_model.tf_model.summary()

        new_y = new_model.predict(train_x[:20])
        assert new_y == original_y

        report = new_model.evaluate(train_x, train_y)
        print(report)

    def test_with_word_embedding(self):
        w2v_embedding = WordEmbedding(sample_w2v_path)
        model = self.TASK_MODEL_CLASS(embedding=w2v_embedding, sequence_length=120)
        from kolibri.data.text.corpus import CONLL2003ENCorpus
        corpus = CONLL2003ENCorpus()

        train_x, train_y = corpus.get_data(nb_samples=500)
        valid_x, valid_y = train_x, train_y

        model.fit(train_x,
                  train_y,
                  x_validate=valid_x,
                  y_validate=valid_y,
                  epochs=self.EPOCH_COUNT)

    # def test_with_bert(self):
    #     bert_path = get_file('bert_sample_model',
    #                          "http://dropbox/bert_sample_model.tar.bz2",
    #                          cache_dir=DATA_PATH,
    #                          untar=True)
    #     embedding = BertEmbedding(model_folder=bert_path)
    #     model = self.TASK_MODEL_CLASS(embedding=embedding)
    #     train_x, train_y = TestMacros.load_labeling_corpus()
    #     valid_x, valid_y = train_x, train_y
    #
    #     model.fit(train_x,
    #               train_y,
    #               x_validate=valid_x,
    #               y_validate=valid_y,
    #               epochs=self.EPOCH_COUNT)
    #
    #     model.evaluate(valid_x, valid_y)
    #     model.evaluate(valid_x, valid_y, truncating=True)
    #     model.predict(valid_x)
    #     model.predict(valid_x, truncating=True)


if __name__ == '__main__':
    unittest.main()

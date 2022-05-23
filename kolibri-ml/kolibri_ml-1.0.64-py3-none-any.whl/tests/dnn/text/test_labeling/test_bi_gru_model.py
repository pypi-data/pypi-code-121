# encoding: utf-8

import tests.dnn.text.test_labeling.test_bi_lstm_model as base
from kolibri.backend.tensorflow.tasks.text.labeling import BiGRU_Model
from kolibri.tokenizer import WordTokenizer

tokenizer = WordTokenizer()


class TestBiGRU_Model(base.TestBiLSTM_Model):

    @classmethod
    def setUpClass(cls):
        cls.EPOCH_COUNT = 1
        cls.TASK_MODEL_CLASS = BiGRU_Model

    def test_basic_use(self):
        super(TestBiGRU_Model, self).test_basic_use()

    def test_predict_and_callback(self):
        from kolibri.data.text.corpus import CONLL2003ENCorpus
        from kolibri.backend.tensorflow.callbacks import EvalCallBack
        corpus = CONLL2003ENCorpus()
        train_x, train_y = corpus.get_data(nb_samples=500)
        valid_x, valid_y = corpus.get_data(nb_samples=100)

        model = BiGRU_Model(sequence_length=10)

        eval_callback = EvalCallBack(kolibri_model=model,
                                     x_data=valid_x[:200],
                                     y_data=valid_y[:200],
                                     truncating=True,
                                     step=1)

        model.fit(train_x[:300], train_y[:300],
                  valid_x[:200], valid_y[:200],
                  epochs=1,
                  callbacks=[eval_callback])
        response = model.predict(train_x[:200], truncating=True)
        lengths = [len(i) for i in response]
        assert all([(i <= 10) for i in lengths])

        response = model.predict(train_x[:200])
        lengths = [len(i) for i in response]
        assert not all([(i <= 10) for i in lengths])


if __name__ == "__main__":
    pass

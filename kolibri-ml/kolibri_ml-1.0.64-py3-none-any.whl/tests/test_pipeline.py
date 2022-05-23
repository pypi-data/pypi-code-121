import unittest

from kolibri.core.pipeline import Pipeline
from kolibri.tokenizers import SentenceTokenizer, WordTokenizer


class PipeLineConsumer():
    name='consumer'
    def fit(self, xt, yt, xv=None, yv=None):
        assert len(xt) == 2
        assert yt[0] == 'class1'
        assert yt[1] == 'class2'


class TestKolibriPipeline(unittest.TestCase):

    def test_fit_generator(self):
        train_x = ["This is a text with 2 sentences that should be splitted. This is the second sentence in this text",
                   "And this is a text with 2 sentences that should be splitted. And this is the second sentence in this text"]
        train_y = ["class1", "class2"]

        pipeline = Pipeline([('sentence_splitter', SentenceTokenizer()), ('word_tokenizer', WordTokenizer()),
                             ('consumer', PipeLineConsumer())])

        res = pipeline.fit(train_x, train_y)

        print(res)


if __name__ == "__main__":
    pass

import random
import unittest

from kolibri.data.text.corpus import ConsumerComplaintsCorpus
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers import SequenceIndexer, LabelIndexer
from kolibri.tokenizer import WordTokenizer

tokenizer = WordTokenizer()


class TestSequenceIndexer(unittest.TestCase):
    def test_text_indexer(self):
        corpus = ConsumerComplaintsCorpus()
        x_set, y_set = corpus.get_data(nb_samples=500)
        x_set = tokenizer.transform(x_set)
        x_samples = random.sample(x_set, 5)
        text_processor = SequenceIndexer(min_count=1)
        text_processor.build_vocab(x_set, y_set)
        text_idx = text_processor.transform(x_samples)

        text_info_dict = text_processor.to_dict()
        text_processor2: SequenceIndexer = load_data_object(text_info_dict)

        text_idx2 = text_processor2.transform(x_samples)
        sample_lengths = [len(i) for i in x_samples]

        assert (text_idx2 == text_idx).all()
        assert text_processor.inverse_transform(text_idx, lengths=sample_lengths) == x_samples
        assert text_processor2.inverse_transform(text_idx2, lengths=sample_lengths) == x_samples

    def test_label_indexer(self):
        corpus = ConsumerComplaintsCorpus()
        x_set, y_set = corpus.get_data(nb_samples=500)
        x_set = tokenizer.transform(x_set)
        text_processor = LabelIndexer(build_vocab_from_labels=True, min_count=1)
        text_processor.build_vocab(x_set, y_set)

        samples = random.sample(y_set, 20)

        text_idx = text_processor.transform(samples, )

        text_info_dict = text_processor.to_dict()

        text_processor2: LabelIndexer = load_data_object(text_info_dict)

        text_idx2 = text_processor2.transform(samples, )
        lengths = [len(i) for i in samples]
        assert (text_idx2 == text_idx).all()
        assert text_processor2.inverse_transform(text_idx, lengths=lengths) == samples
        assert text_processor2.inverse_transform(text_idx2, lengths=lengths) == samples


if __name__ == "__main__":
    pass

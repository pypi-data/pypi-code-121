# encoding: utf-8

import json
import os
from operator import itemgetter
from pathlib import Path

import pandas as pd
from tensorflow.keras.utils import get_file

from kolibri import settings as k
from kolibri.data.text.streams import DataStream
from kolibri.data.text.file_stream import FileStream
from kolibri.tokenizers import WordTokenizer

CORPUS_PATH = os.path.join(k.DATA_PATH, 'corpus')

Path(CORPUS_PATH).mkdir(exist_ok=True, parents=True)


class CONLL2003ENCorpus(FileStream):
    __corpus_name__ = 'conll2003_en'
    __zip_file__name = 'https://www.dropbox.com/s/73jma78ywqzvjyq/conll2003.tar?dl=1'

    def __init__(self, subset_name: str = 'train', task_name: str = 'ner'):

        corpus_path = get_file(self.__corpus_name__,
                               self.__zip_file__name,
                               cache_dir=CORPUS_PATH,
                               untar=True)

        if subset_name not in {'train', 'test', 'valid'}:
            raise ValueError()
        self.task_name = task_name
        self.filepath = os.path.join(corpus_path, f'{subset_name}.txt')
        self.data_index = ['pos', 'chunking', 'ner'].index(self.task_name) + 1
        super().__init__(self.filepath, content_col=0, target_cols=self.data_index, filetype='conll')
        if self.task_name not in {'pos', 'chunking', 'ner'}:
            raise ValueError()
        self.prepare()

    def _load_data(self):
        try:
            raw_data = self.read_function(self.filepath)
            self.n_samples = 0
            for line in raw_data:
                self.n_samples += 1
                for token in line:
                    self.target_values.append(itemgetter(*self.target_columns)(token))

            self.target_values = list(self.target_values)

            self.raw_data = self.read_function(self.filepath)

        except FileNotFoundError:
            raise FileNotFoundError("File {} does not exist.".format(self.filepath))
        pass

    def __iter__(self):

        for token in self.raw_data:
            yield [d[self.content_column] for d in token], [d[self.target_columns[0]] for d in token]


class Sentiment140Corpus(FileStream):
    """

    """

    __corpus_name__ = 'Sentiments140'
    __zip_file__name = "https://www.dropbox.com/s/egk8cwupfs05g00/Sentiments140.tar.gz?dl=1"

    def __init__(self, subset_name='sentiment140_sample'):
        self.corpus_path = get_file(self.__corpus_name__,
                                    self.__zip_file__name,
                                    cache_dir=k.DATA_PATH,
                                    untar=True)

        if subset_name not in {'sentiment140_sample', 'all'}:
            raise ValueError()

        self.file_path = os.path.join(self.corpus_path, f'{subset_name}.csv')

        super().__init__(filepath=self.file_path, content_col=' text', target_cols='label')
        self.prepare()

class CreditCardFraud(DataStream):
    """

    """

    __corpus_name__ = 'creditcard_fraud'
    __zip_file__name = "https://www.dropbox.com/s/7v4tm6lsjkxnvfk/creditcard_fraud.tgz?dl=1"

    def __init__(self, subset_name='creditcard'):
        self.corpus_path = get_file(self.__corpus_name__,
                                    self.__zip_file__name,
                                    cache_dir=k.DATA_PATH,
                                    untar=True)

        if subset_name not in {'creditcard'}:
            raise ValueError()

        self.file_path = os.path.join(self.corpus_path, f'{subset_name}.csv')
        data=pd.read_csv(self.file_path)
        columns=[ c for c in data.columns if c not in ['Class', 'Time']]

        super().__init__(data=data[columns], y=data['Class'].values)
        self.prepare()


class ConsumerComplaintsCorpus(FileStream):
    """

    """

    __corpus_name__ = 'consumer_complaints'
    __zip_file__name = "https://www.dropbox.com/s/8a1pm3gg9e5szso/consumer_complaints.tar.gz?dl=1"

    def __init__(self, subset_name='sample'):
        self.corpus_path = get_file(self.__corpus_name__,
                                    self.__zip_file__name,
                                    cache_dir=k.DATA_PATH,
                                    untar=True)

        if subset_name not in {'sample', 'validate', 'train', 'test'}:
            raise ValueError()

        self.file_path = os.path.join(self.corpus_path, f'{subset_name}.csv')

        super().__init__(filepath=self.file_path, content_col='Consumer_complaint', target_cols=['Product'])
        self.prepare()


class SnipsIntentCorpus(DataStream):
    """
    SNIPS dataset_train class

    Args:
            path (str): dataset_train path
            sentence_length (int, optional): max sentence length
            word_length (int, optional): max word length
    """

    __corpus_name__ = 'snips_intents'
    __zip_file__name = "https://www.dropbox.com/s/somo7vz6p23e2aq/snips_intent.tgz?dl=1"

    train_files = [
        "AddToPlaylist/train_AddToPlaylist_full.json",
        "BookRestaurant/train_BookRestaurant_full.json",
        "GetWeather/train_GetWeather_full.json",
        "PlayMusic/train_PlayMusic_full.json",
        "RateBook/train_RateBook_full.json",
        "SearchCreativeWork/train_SearchCreativeWork_full.json",
        "SearchScreeningEvent/train_SearchScreeningEvent_full.json",
    ]
    test_files = [
        "AddToPlaylist/validate_AddToPlaylist.json",
        "BookRestaurant/validate_BookRestaurant.json",
        "GetWeather/validate_GetWeather.json",
        "PlayMusic/validate_PlayMusic.json",
        "RateBook/validate_RateBook.json",
        "SearchCreativeWork/validate_SearchCreativeWork.json",
        "SearchScreeningEvent/validate_SearchScreeningEvent.json",
    ]
    files = ["train", "test"]

    def __init__(self, subset_name: str = 'train', task_name: str = 'ner'):

        corpus_path = get_file(self.__corpus_name__,
                               self.__zip_file__name,
                               cache_dir=CORPUS_PATH,
                               untar=True)

        if subset_name not in {'train', 'test'}:
            raise ValueError()
        self.task_name = task_name

        self.dataset_root = corpus_path
        data_set_raw = self._load_dataset(subset_name)
        data_set_raw = pd.DataFrame(data_set_raw, columns=['Content', 'Entities', 'Intent'])
        super().__init__(data=data_set_raw[['Content']], y=data_set_raw[['Entities', 'Intent']])
        self.prepare()

    def _load_dataset(self, dataset):
        """returns a tuple of train/test with 3-tuple of tokens, tags, intent_type"""
        if dataset == 'train':
            _data = self._load_intents(self.train_files)
        else:
            _data = self._load_intents(self.test_files)

        data = [(t, l, i) for i in sorted(_data) for t, l in _data[i]]

        return data

    def _load_intents(self, files):
        data = {}
        for f in sorted(files):
            fname = os.path.join(self.dataset_root, f)
            intent = f.split(os.sep)[0]
            with open(fname, encoding="utf-8", errors="ignore") as fp:
                fdata = json.load(fp)
            entries = self._parse_json([d["data"] for d in fdata[intent]])
            data[intent] = entries
        return data

    def _parse_json(self, data):
        tokenizer = WordTokenizer()
        sentences = []
        for s in data:
            tokens = []
            tags = []
            for t in s:
                new_tokens = tokenizer.tokenize(t["text"].strip())
                tokens += new_tokens
                ent = t.get("entity", None)
                if ent is not None:
                    tags += self._create_tags(ent, len(new_tokens))
                else:
                    tags += ["O"] * len(new_tokens)
            sentences.append((tokens, tags))
        return sentences

    @staticmethod
    def _create_tags(tag, length):
        labels = ["B-" + tag]
        if length > 1:
            for _ in range(length - 1):
                labels.append("I-" + tag)
        return labels


if __name__ == "__main__":
    corpus = SnipsIntentCorpus()

    for d in corpus.X:
        print(list(d))

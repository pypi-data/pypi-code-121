from typing import Tuple, List
from nlp_tools import macros as k
import os
CORPUS_PATH = os.path.join(k.DATA_PATH, 'corpus')

class DataReader(object):

    @staticmethod
    def read_conll_format_file(file_path: str,
                               text_index: int = 0,
                               label_index: int = 1) -> Tuple[List[List[str]], List[List[str]]]:
        """
        Read conll format data_file
        Args:
            file_path: path of target file
            text_index: index of text data, default 0
            label_index: index of label data, default 1

        Returns:

        """
        x_data, y_data = [], []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            x, y = [], []
            for line in lines:
                rows = line.split(' ')
                if len(rows) == 1:
                    x_data.append(x)
                    y_data.append(y)
                    x = []
                    y = []
                else:
                    x.append(rows[text_index])
                    y.append(rows[label_index])
        return x_data, y_data

from nlp_tools.corpus.ner.corpus_loader import ChineseDailyNerCorpus
from nlp_tools.corpus.classify.corpus_loader import SMP2018ECDTCorpus
from nlp_tools.corpus.classify.dialogue_corpus_loader import DialogueCorpusLoader
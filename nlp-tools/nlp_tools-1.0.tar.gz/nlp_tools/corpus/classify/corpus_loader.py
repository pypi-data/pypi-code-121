from tensorflow.keras.utils import get_file
from typing import Tuple, List
from nlp_tools import macros as k
import os
from nlp_tools.corpus import DataReader
from nlp_tools import utils
import logging
import pandas as pd

class SMP2018ECDTCorpus(object):
    """
    https://worksheets.codalab.org/worksheets/0x27203f932f8341b79841d50ce0fd684f/

    This dataset is released by the Evaluation of Chinese Human-Computer Dialogue Technology (SMP2018-ECDT)
    tasks 1 and is provided by the iFLYTEK Corporation, which is a Chinese human-computer dialogue dataset.
    sample::

              label           query
        0   weather        今天东莞天气如何
        1       map  从观音桥到重庆市图书馆怎么走
        2  cookbook          鸭蛋怎么腌？
        3    health         怎么治疗牛皮癣
        4      chat             唠什么
    """

    __corpus_name__ = 'SMP2018ECDTCorpus'
    __zip_file__name = 'http://s3.bmio.net/kashgari/SMP2018ECDTCorpus.tar.gz'

    @classmethod
    def load_data(cls,
                  subset_name: str = 'train',
                  shuffle: bool = True,
                  cutter: str = 'char') -> Tuple[List[List[str]], List[str]]:
        """
        Load dataset as sequence classification format, char level tokenized

        features: ``[['听', '新', '闻', '。'], ['电', '视', '台', '在', '播', '什', '么'], ...]``

        labels: ``['news', 'epg', ...]``

        Samples::
            train_x, train_y = SMP2018ECDTCorpus.load_data('train')
            test_x, test_y = SMP2018ECDTCorpus.load_data('test')

        Args:
            subset_name: {train, test, valid}
            shuffle: should shuffle or not, default True.
            cutter: sentence cutter, {char, jieba}

        Returns:
            dataset_features and dataset labels
        """

        corpus_path = get_file(cls.__corpus_name__,
                               cls.__zip_file__name,
                               cache_dir=k.DATA_PATH,
                               untar=True)

        if cutter not in ['char', 'jieba', 'none']:
            raise ValueError('cutter error, please use one onf the {char, jieba}')

        df_path = os.path.join(corpus_path, f'{subset_name}.csv')
        df = pd.read_csv(df_path)
        if cutter == 'jieba':
            try:
                import jieba
            except ModuleNotFoundError:
                raise ModuleNotFoundError(
                    "please install jieba, `$ pip install jieba`")
            x_data = [list(jieba.cut(item)) for item in df['query'].to_list()]
        elif cutter == 'char':
            x_data = [list(item) for item in df['query'].to_list()]
        else:
            x_data = [item for item in df['query'].to_list()]
        y_data = df['label'].to_list()

        if shuffle:
            x_data, y_data = utils.unison_shuffled_copies(x_data, y_data)
        logging.debug(f"loaded {len(x_data)} samples from {df_path}. Sample:\n"
                      f"x[0]: {x_data[0]}\n"
                      f"y[0]: {y_data[0]}")
        return x_data, y_data


if __name__ == "__main__":
    a, b = SMP2018ECDTCorpus.load_data(cutter='none')
    print(a[:2])
    print(b[:2])
    print("Hello world")
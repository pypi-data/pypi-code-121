import logging
import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import TimeSeriesSplit
from pandas.testing import assert_index_equal

TRAIN_FEATURE_KEY = "train_feature"
TRAIN_TARGET_KEY = "train_target"
TEST_FEATURE_KEY = "test_feature"
TEST_TARGET_KEY = "test_target"

logger = logging.getLogger(__file__)

def shuffle_df(data: pd.DataFrame, target_col: str, rand_state: int = None):
    targets = data[[target_col]]
    features = data[data.columns[~data.columns.isin([target_col])]]

    assert len(features.columns) > 1, "no column left for feature"

    if rand_state is None:
        rand_state = np.random.randint(1000)

    features_shuf_ind, targets_shuf_ind = shuffle(features.index, targets.index, random_state=rand_state)

    features_shuf = features.loc[features_shuf_ind]
    targets_shuf = targets.loc[targets_shuf_ind]

    all_shuf = data.loc[features_shuf_ind]

    return features_shuf, targets_shuf, all_shuf, rand_state


class CustomTsCv:
    """
      in addition to sklearn time series can shuffle train data in blocks
    """
    def __init__(self, train_n: int, test_n: int, sample_n: int, train_shuffle_block_size: int = None):
        split_n = int((sample_n + 1) / test_n) - 1
        print(split_n)
        assert split_n > 1, "split is 1"
        self.split_n = split_n
        self.train_n = train_n
        self.test_n = test_n
        self.sample_n = sample_n
        self.train_shuffle_block_size = train_shuffle_block_size


        if train_shuffle_block_size is not None:
            assert train_n % train_shuffle_block_size == 0, "train data is not devidable in shuffle block size"

        self.train_shuffle_block_size = train_shuffle_block_size
        self.tscv = TimeSeriesSplit(max_train_size=train_n, test_size=test_n, n_splits=split_n)

    def split(self, X, y, groups=None):
        counter = 0
        for tr, ts in self.tscv.split(X=X, y=y, groups=groups):
            if counter == 0:
                counter = counter + 1
                yield tr, tr # to be inline with cross_val_predict expected cv
                             # google: "cross_val_predict only works for partitions TimeSeriesSplit"

            final_tr = tr
            final_ts = ts

            if self.train_shuffle_block_size is not None:
                if len(final_tr) % self.train_shuffle_block_size == 0:
                    np.random.shuffle(final_tr.reshape((-1, self.train_shuffle_block_size)))
                else:
                    logger.warning(f"train shuffle cant be done in this itt: final_tr: {len(final_tr)}")



            yield final_tr, final_ts

    def get_n_splits(self, X, y, groups=None):
        return self.tscv.n_splits + 1 # it is for first split that train returns (check out counter in split function)


def calculate_confidence_interval(statistics: pd.DataFrame,
                                  alpha: float = 5.0,
                                  ignore_small_instances: bool = False) -> pd.DataFrame:
    """
    to calculate statistical intervals based on trials
    :param statistics: any estimations coming from running trials (e.g. accuracy, error, ...).
        - dataframe, columns: statistics, row: trials (samples)
    :param alpha: p-value
    :param ignore_small_instances: for too small values, this method cant work, if True, the answer might not be reliable
    :return: dataframe: columns: lower/higher ci, index: statistic name from input statistics
    """
    if not ignore_small_instances:
        assert len(statistics) < 100, "number of trials is too low to build any confidence level"

    # calculate lower percentile (e.g. 2.5)
    lower_p = alpha / 2.0
    # calculate upper percentile (e.g. 97.5)
    upper_p = (100 - alpha) + (alpha / 2.0)

    cis = statistics.quantile([lower_p / 100.0, upper_p / 100.0]).transpose()
    cis.columns = [f"Lower_{lower_p}", f"Upper_{upper_p}"]
    return cis


# class CvTsDfUtil:
#     @staticmethod
#     def get_split_len(fold_result: dict):
#         return len(fold_result[TEST_FEATURE_KEY])
#
#     @staticmethod
#     def get_train(fold_result: dict, ind: int):
#         return fold_result[TRAIN_FEATURE_KEY][ind], fold_result[TRAIN_TARGET_KEY][ind]
#
#     @staticmethod
#     def get_test(fold_result: dict, ind: int):
#         return fold_result[TEST_FEATURE_KEY][ind], fold_result[TEST_TARGET_KEY][ind]

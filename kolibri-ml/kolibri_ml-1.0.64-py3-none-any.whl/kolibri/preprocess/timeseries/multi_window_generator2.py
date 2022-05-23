from math import ceil
import pandas as pd
from kolibri.preprocess.timeseries.window_generator import WindowGenerator
import tensorflow as tf
from kolibri.preprocess.timeseries.time_series_from_array import timeseries_dataset_from_array
import numpy as np
from tqdm import tqdm

class MultiWindowGenerator(WindowGenerator):
    """Base class for sliding and expanding window splitter."""

    defaults = {
        "fixed": {
            "target": None,
            "dropnan": True,
            "shuffle": False,
            "seed": None,
            "batch-size": 256,
            "buffer-size": 150,
            "train-ratio": 0.6,
            "val-ratio": 0.8,
            "group": [],
            "timestamp": [],
            "univariate": False,
            "test-timesteps": 1,
            "horizon": 1,
            "window-strategy": "fixed"
        },
        "tunable": {
            "window_length": {
                "value": None,
            }
        }

    }

    def __init__(self, data, configs={}):
        super(MultiWindowGenerator, self).__init__(data, configs)
        self.data = data

        self.seed = self.get_parameter("seed")

        self.nb_test_steps = self.get_parameter("test-timesteps")

        self.window_strategy = self.get_parameter("window-strategy")

    def split_dataset(self, by_instance=True):
        if self.get_parameter("dropnan"):
            self.data = self.data.fillna(0)

        self.data = pd.DataFrame(self.data.groupby(self.get_parameter("group")))

        self.train_data = None
        self.test_data = None
        self.val_data = None

        train_ratio = self.get_parameter("train-ratio")
        val_ratio = self.get_parameter("val-ratio")


        for group in tqdm(self.data[1]):


            n = len(group) - self.window_length
            if n <= 0:
                continue
            train_limit = ceil(n * train_ratio)
            val_limit = max(train_limit, ceil(n * val_ratio))
            group = group.sort_values(by=self.get_parameter("timestamp"), ascending=True)

            self.train_df = group[0:train_limit + self.window_length]
            self.train_df=self.train_df.set_index(self.get_parameter("group")+ [self.get_parameter("timestamp")])
            if self.column_indices is None:
                if self.train_df is not None:
                    self.column_indices = {name: i for i, name in
                                           enumerate(self.train_df.columns)}
            data = np.array(self.train_df.values, dtype=np.float32)

            if data.size>1:

                train_df = timeseries_dataset_from_array(
                    data=data,
                    targets=None,
                    sequence_length=self.total_window_size,
                    sequence_stride=1,
                    shuffle= self.shuffle)
                # train_df=[w for w in train_df.map(self.split_window)]
                train_df=self.split_window(train_df)#[self.split_window(w) for w in train_df]
                if self.train_data is None:
                    self.train_data=train_df
                else:
                    self.train_data=(np.concatenate([self.train_data[0], train_df[0]], 0), np.concatenate([self.train_data[1], train_df[1]], 0))



            if val_limit>train_limit:
                self.val_df = group[train_limit:val_limit+self.window_length]
                self.val_df = self.val_df.set_index(self.get_parameter("group")+ [self.get_parameter("timestamp")])
                data = np.array(self.val_df.values, dtype=np.float32)

                if data.size>1:

                    val_df = timeseries_dataset_from_array(
                        data=data,
                        targets=None,
                        sequence_length=self.total_window_size,
                        sequence_stride=1,
                        shuffle= self.shuffle)
                    val_df=self.split_window(val_df)
                    if self.val_data is None:
                        self.val_data = val_df
                    else:
                        self.val_data = (tf.concat([self.val_data[0], val_df[0]], 0),
                                         tf.concat([self.val_data[1], val_df[1]], 0))


                if val_ratio > 0 and val_ratio < 1 and val_limit<n + self.window_length:
                    self.test_df = group[val_limit:]
                    self.test_df = self.test_df.set_index(self.get_parameter("group")+ [self.get_parameter("timestamp")])
                    data = np.array(self.test_df.values, dtype=np.float32)

                    if len(data)>1:
                        test_df = timeseries_dataset_from_array(
                            data=data,
                            targets=None,
                            sequence_length=self.total_window_size,
                            sequence_stride=1,
                            shuffle= self.shuffle)
                        if len(test_df)==0:
                            continue
                        test_df=self.split_window(test_df)
                        if len(test_df)>0:
                            if self.test_data is None:
                                self.test_data = test_df
                            else:
                                self.test_data = (tf.concat([self.test_data[0], test_df[0]], 0),
                                                  tf.concat([self.test_data[1], test_df[1]], 0))


        return

    @property
    def train(self):
        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")
        train_data_multi = tf.data.Dataset.from_tensor_slices(self.train_data)
        train_data_multi = train_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE)#.repeat()

        return train_data_multi

    @property
    def val(self):
        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")

        train_data_multi = tf.data.Dataset.from_tensor_slices(self.val_data)
        train_data_multi = train_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE)#.repeat()

        return train_data_multi

    @property
    def test(self):
        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")

        train_data_multi = tf.data.Dataset.from_tensor_slices(self.test_data)
        train_data_multi = train_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE)#.repeat()

        return train_data_multi

from math import ceil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from kolibri.core.component import Component
import tensorflow as tf
from kolibri.utils.timeseries_functions import roll_time_series
from tensorflow.keras.preprocessing.sequence import pad_sequences

class MultiWindowGenerator(Component):
    """Base class for sliding and expanding window splitter."""

    defaults = {
        "fixed": {
            "target": None,
            "dropnan": True,
            "shuffle": False,
            "seed": None,
            "batch-size": 32,
            "buffer-size": 150,
            "timestamp-test":1,
            "timestamp-val":1,
            "group": [],
            "timestamp": [],
            "univariate": False,
            "horizon": 1,
            "n_jobs":4
        },
        "tunable": {
            "min-window-history": {
                "value": 4
            },
            "max-window-history": {
                "value": 8
            }
        }

    }

    def __init__(self, data, configs={}):
        super(MultiWindowGenerator, self).__init__(configs)
        self.data = data

        self.seed = self.get_parameter("seed")

        self.nb_test_steps = self.get_parameter("test-timesteps")

        self.window_strategy = self.get_parameter("window-strategy")

        self._extra_columns=list(filter(None,[self.get_parameter("group"), self.get_parameter("timestamp"), "id", "id_sort"]))

        if self.data is not None:
            self.column_indices = {name: i for i, name in
                                   enumerate(self.data.columns)}
        # Work out the label column indices.
        self.targets = self.get_parameter("target")

        # Work out the window parameters.
        self.window_length = self.get_parameter("max-window-history")
        self.horizon = self.get_parameter("horizon")
        self.shift = self.get_parameter("shift", 1)
        self.shuffle = self.get_parameter("shuffle")
        self.column_indices=None
        if self.targets is not None:
            self.label_columns_indices = {name: i for i, name in
                                          enumerate(self.targets)}

        self.total_window_size = self.window_length + self.horizon

        self.input_slice = slice(0, self.window_length)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.horizon
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]
        self.split_dataset()

        if self.column_indices is None:
            columns = [col for col in self._train_df.columns if col not in self._extra_columns]
            if self._train_df is not None:
                self.column_indices = {name: i for i, name in
                                       enumerate(columns)}


    def __repr__(self):
        return '\n'.join([
            f'Total window size: {self.total_window_size}',
            f'Input indices: {self.input_indices}',
            f'Label indices: {self.label_indices}',
            f'Label column name(s): {self.targets}'])

    def split_window(self, features):
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]


        if self.targets is not None:
            labels = np.stack(
                [labels[:, :, self.column_indices[name]] for name in self.targets],
                axis=-1)


        return inputs, labels

    def plot(self, model=None, plot_col='Gross_Total', max_subplots=3):
        inputs, labels = self.example
        plt.figure(figsize=(12, 8))
        plot_col_index = self.column_indices[plot_col]
        max_n = min(max_subplots, len(inputs))
        for n in range(max_n):
            plt.subplot(max_n, 1, n + 1)
            plt.ylabel(f'{plot_col} [normed]')
            plt.plot(self.input_indices, inputs[n, :, plot_col_index],
                     label='Inputs', marker='.', zorder=-10)

            if self.targets:
                label_col_index = self.label_columns_indices.get(plot_col, None)
            else:
                label_col_index = plot_col_index

            if label_col_index is None:
                continue

            plt.scatter(self.label_indices, labels[n, :, label_col_index],
                        edgecolors='k', label='Labels', c='#2ca02c', s=64)
            if model is not None:
                predictions = model(inputs)
                plt.scatter(self.label_indices, predictions[n, :, label_col_index],
                            marker='X', edgecolors='k', label='Predictions',
                            c='#ff7f0e', s=64)

            if n == 0:
                plt.legend()

        plt.xlabel('Time')
        return plt



    def split_dataset(self):
        if self.get_parameter("dropnan"):
            self.data = self.data.fillna(0)

        self.df_rolled = roll_time_series(self.data, column_id=self.get_parameter("group"), column_sort=self.get_parameter("timestamp"), n_jobs=self.get_parameter("n_jobs"),
                                     max_timeshift=self.get_parameter("max-window-history")+self.horizon-1, min_timeshift=self.get_parameter("min-window-history")+self.horizon-1).drop(columns=[self.get_parameter("group"), self.get_parameter("timestamp")])

        self.df_rolled[['id_group', 'id_sort']] = pd.DataFrame(self.df_rolled['id'].tolist(), index=self.df_rolled.index)
        timestamps=sorted(self.data[self.get_parameter("timestamp")].unique())
        valid_timestamp=None
        test_timestamp=None

        if len(timestamps)>3:
            valid_timestamp=timestamps[-2]
            test_timestamp=timestamps[-1]
        elif len(timestamps)==2:
            valid_timestamp=timestamps[-1]




        if valid_timestamp is not None:
            self._valid_df=self.df_rolled[self.df_rolled["id_sort"] == valid_timestamp]

        if test_timestamp is not None:
            self._test_df=self.df_rolled[self.df_rolled["id_sort"] == test_timestamp]

        if test_timestamp is not None:
            self._train_df=self.df_rolled[self.df_rolled["id_sort"] < test_timestamp]
        elif valid_timestamp is not None:
            self._valid_df = self.df_rolled[self.df_rolled["id_sort"] < valid_timestamp]
        else:
            self._train_df=self.df_rolled


        print("*")

    def _get_array_values(self, ds, drop_ids=None):

        values = ds.groupby(["id", "id_sort"])
        colums_to_drop=["id", "id_sort", "id_group"]
        dtypes='float32'
        if drop_ids is not None:
            colums_to_drop=drop_ids
            dtypes='object'
        if self.get_parameter('max-window-history')==self.get_parameter('min-window-history'):
            values = np.array(
                [values.get_group(group).drop(columns=colums_to_drop) for group in values.groups])
        else:
            values = pad_sequences(np.array(
                [values.get_group(group).drop(columns=colums_to_drop).values for group in values.groups]), dtype=dtypes)

#            tf.keras.preprocessing.sequence.pad_sequences(
#                sequences, maxlen=None, dtype='int32', padding='pre',
#                truncating='pre', value=0.0
#            )
        return values


    @property
    def train(self):

        if not hasattr(self,"train_values"):

            self.train_values=self.split_window(self._get_array_values(self._train_df))


        return  self.train_values


    @property
    def train_ds(self):

        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")

        train_data_multi = tf.data.Dataset.from_tensor_slices(self.train)
        train_data_multi = train_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return train_data_multi

    @property
    def val(self):


        if not hasattr(self, "val_values"):

            self.val_values=self.split_window(self._get_array_values(self._valid_df))

        return self.val_values

    @property
    def val_ds(self):
        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")


        val_data_multi = tf.data.Dataset.from_tensor_slices(self.val)
        val_data_multi = val_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return val_data_multi


    @property
    def test(self):
        if not hasattr(self, "test_values"):
            self.test_values=self.split_window(self._get_array_values(self._test_df))
        return self.test_values


    @property
    def test_ds(self):
        BUFFER_SIZE=self.get_parameter("buffer-size")
        BATCH_SIZE=self.get_parameter("batch-size")

        test_data_multi = tf.data.Dataset.from_tensor_slices(self.test)
        test_data_multi = test_data_multi.batch(BATCH_SIZE).cache().shuffle(BUFFER_SIZE).repeat()

        return test_data_multi


    @property
    def num_features(self):
        return len(self._train_df.columns) - len(self._extra_columns)

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, '_example', None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train_ds))
            # And cache it for next time
            self._example = result

        return result

    @property
    def train_df(self):
        return self._train_df.drop(columns=["id", "id_sort", "id_group"])

    @property
    def test_df(self):
        if hasattr(self, "test_df_"):
            return self.test_df_
        else:
            test_values=self._get_array_values(self._test_df, drop_ids=["id"])
            self.test_df_ = pd.DataFrame(test_values[:, self.labels_slice, :].reshape(-1, test_values.shape[2]),
                                         columns=list(self.train_df.columns) + ["id_group", "id_sort"])
        return self.test_df_

    @property
    def val_df(self):
        if hasattr(self, "val_df_"):
            return self.val_df_
        else:
            val_values=self._get_array_values(self._valid_df, drop_ids=["id"])
            self.val_df_ = pd.DataFrame(val_values[:, self.labels_slice, :].reshape(-1, val_values.shape[2]),
                                         columns=list(self.train_df.columns) + ["id_group", "id_sort"])
        return self.val_df_

    def process_timestep(self, df, history_df=None, ovrride_timestamps=False):

        if self.data is None:
            self.data=history_df

        if self.data is None or len(self.data.index)<1:
            raise Exception("History data set is empty of Null")

        if self.get_parameter("timestamp") not in df.columns or self.get_parameter("timestamp") not in self.data.columns:
            raise Exception("Timestamp column: "+self.get_parameter("timestamp")+" not found in the provided dataframe")

        history_window_length=self.get_parameter("max-window-history")
        timestamps=sorted(self.data[self.get_parameter("timestamp")].unique())[:-history_window_length]
        self.data=self.data[self.data[self.get_parameter("timestamp")].isin(timestamps)]
        new_time_steps=sorted(df[self.get_parameter("timestamp")].unique())[:-history_window_length]

        if new_time_steps[0]<=timestamps[-1] and not ovrride_timestamps:
            raise Exception("The provided timestep already exist in history")

        if len(self.data.columns.intersection(df.columns)) != self.data.shape[1]:
            raise Exception("History and the provided dataset does nbot have the same columns")

        self.data=pd.concat([self.data, df[self.data.columns.intersection(df.columns)]])

        self.df_predict = roll_time_series(self.data, column_id=self.get_parameter("group"), column_sort=self.get_parameter("timestamp"),
                                     max_timeshift=self.get_parameter("max-window-history")+self.horizon-1, min_timeshift=self.get_parameter("min-window-history")+self.horizon-1).drop(columns=[self.get_parameter("group"), self.get_parameter("timestamp")])

        self.df_predict[['id_group', 'id_sort']] = pd.DataFrame(self.df_rolled['id'].tolist(), index=self.df_rolled.index)
        predict_values=self.split_window(self._get_array_values(self.df_predict))

        return predict_values

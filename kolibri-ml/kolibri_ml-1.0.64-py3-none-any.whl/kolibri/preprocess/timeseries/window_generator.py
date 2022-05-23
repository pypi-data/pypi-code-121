
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from kolibri.core.component import Component
from math import ceil, floor


class WindowGenerator(Component):
    defaults = {
        "fixed": {
            "target": None,
            "dropnan": True,
            "shuffle": False,
            "group": [],
            "train_ratio": 0.7,
            "val_ratio": 0.9,
            "timestamp": [],
            "test-timesteps": 1,
            "horizon": 1,
            "shift": 1,
            "split_column": None,
            "batch_size": 64
        },
        "tunable": {
            "window_length": {
                "value": 4,
            }
        }

    }

    def __init__(self, data, configs):
        # Store the raw data.
        super().__init__(configs)
        self.data = data
        if self.data is not None:
            self.column_indices = {name: i for i, name in
                                   enumerate(self.data.columns)}
        # Work out the label column indices.
        self.targets = self.get_parameter("target")
        # Work out the window parameters.
        self.window_length = self.get_parameter("window_length")
        self.horizon = self.get_parameter("horizon")
        self.shift = self.get_parameter("shift", 1)
        self.shuffle = self.get_parameter("shuffle")
        self.column_indices=None
        if self.targets is not None:
            self.label_columns_indices = {name: i for i, name in
                                          enumerate(self.targets)}

        self.total_window_size = self.window_length + self.shift

        self.input_slice = slice(0, self.window_length)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.horizon
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]

        self.split_dataset(self.get_parameter("split_column") != None)


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
            labels = tf.stack(
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

    def make_dataset(self, data):
        ds=[]
        if data is None or len(data)<=1:
            return ds
        data = np.array(data, dtype=np.float32)

        if data.size>0:

            ds = tf.keras.preprocessing.timeseries_dataset_from_array(
                data=data,
                targets=None,
                sequence_length=self.total_window_size,
                sequence_stride=1,
                shuffle= self.shuffle,
                batch_size=32, )

            ds = ds.map(self.split_window)

        return ds

    @property
    def train(self):
        return self.make_dataset(self.train_data)

    @property
    def val(self):
        return self.make_dataset(self.val_data)

    @property
    def test(self):
        return self.make_dataset(self.test_data)

    @property
    def num_features(self):
        return self.train_data.shape[1]

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, '_example', None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train))
            # And cache it for next time
            self._example = result

        return result

    def split_dataset(self, by_instance=True):
        self.train_data = None
        self.test_data = None
        self.val_data = None

        train_ratio = self.get_parameter("train_ratio")
        val_ratio = self.get_parameter("val_ratio")
        split_var = self.get_parameter("split_column")
        if self.get_parameter("dropnan"):
            self.data = self.data.fillna(0)

        if by_instance and self.get_parameter("split_column") is not None:
            individuals = self.data[split_var].unique()
            n = len(individuals)
            individuals_train = individuals[0:int(n * train_ratio)]
            individuals_val = individuals[int(n * train_ratio):int(n * val_ratio)]
            individuals_test = individuals[int(n * val_ratio):]

            self.train_data = self.data[self.data[split_var].isin(individuals_train)]
            self.val_data = self.data[self.data[split_var].isin(individuals_val)]
            self.train_data = self.train_data.set_index(
                [self.get_parameter("timestamp"), self.get_parameter("split_column")])
            self.val_data = self.val_data.set_index([self.get_parameter("timestamp"), self.get_parameter("split_column")])
            if self.train_data is not None:
                self.column_indices = {name: i for i, name in
                                       enumerate(self.train_data.columns)}
            if val_ratio > 0:
                self.test_data = self.data[self.data[split_var].isin(individuals_test)]
                self.test_data = self.test_data.set_index(
                    [self.get_parameter("timestamp"), self.get_parameter("split_column")])

        elif by_instance == False:
            n = len(self.data) - self.window_length
            if n <= 0:
                return
            train_limit = ceil(n * train_ratio)
            val_limit = max(train_limit, ceil(n * val_ratio))

            self.data = self.data.sort_values(by=self.get_parameter("timestamp"))
            self.train_data = self.data[0:train_limit + self.window_length]
            self.val_data = self.data[train_limit - self.window_length:val_limit]

            self.train_data = self.train_data.set_index([self.get_parameter("timestamp")] + self.get_parameter("group"))
            self.val_data = self.val_data.set_index([self.get_parameter("timestamp")] + self.get_parameter("group"))

            if val_ratio > 0 and val_ratio < 1:
                self.test_data = self.data[val_limit - self.window_length:]
                self.test_data = self.test_data.set_index([self.get_parameter("timestamp")] + self.get_parameter("group"))

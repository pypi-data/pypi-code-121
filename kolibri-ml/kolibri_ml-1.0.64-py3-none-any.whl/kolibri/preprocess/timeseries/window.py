import numpy as np
import pandas as pd
from kolibri.core.component import Component
from pandas import concat


class WindowGenerator(Component):
    """Base class for sliding and expanding window splitter."""

    defaults = {
        "fixed": {
            "target": None,
            "dropnan": True,
            "shuffle": False,
            "seed": None,
            "start_index": 0,
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
        super(WindowGenerator, self).__init__(parameters=configs)
        self.data = data

        self.data = pd.DataFrame(self.data.groupby(self.get_parameter("group")))

        self.window_length = self.get_parameter("window_length")

        self.targets = [self.get_parameter("target")]

        self.horizon = self.get_parameter("horizon")

        self.shuffle = self.get_parameter("shuffle")

        self.seed = self.get_parameter("seed")

        self.nb_test_steps = self.get_parameter("test-timesteps")

        self.window_strategy = self.get_parameter("window-strategy")

        self.shift=1

        self.sampling_rate=1

        self._test_data_features = []
        self._test_data_target = []
        self._test_data_keys = []

    def _series_to_timeseries(self, data, keys, targets):

        end_index = len(data)

        test_features_values = []
        test_target_values = []
        test_keys_values = []

        nb_test_steps = self.nb_test_steps
        if end_index <= self.window_length + self.shift:
            nb_test_steps = 0

        num_seqs = end_index - self.horizon - (self.window_length * self.sampling_rate) - nb_test_steps - self.shift + 1

        # Generate start positions
        start_positions = np.arange(self.shift + nb_test_steps, num_seqs + self.shift + nb_test_steps, self.step_length)
        target_values = []
        target_keys = []
        test_keys_values = []
        if self.targets is not None:
            target_values = [data[i - self.shift][targets] for i in start_positions]
            target_keys = [data[i - self.shift][keys] for i in start_positions]
            if len(start_positions) > 0:
                test_target_values = [data[i - self.shift][targets] for i in range(self.shift, start_positions[0])]
                test_keys_values = [data[i - self.shift][keys] for i in range(self.shift, start_positions[0])]
        if self.shuffle:
            if self.seed is None:
                self.seed = np.random.randint(1e6)
            rng = np.random.RandomState(self.seed)
            rng.shuffle(start_positions)

        indices_map = lambda i, positions: range(  # pylint: disable=g-long-lambda
            positions[i - self.shift - nb_test_steps],
            positions[i - self.shift - nb_test_steps] + self.window_length * self.sampling_rate,
            self.sampling_rate)

        features_col = [i for i in range(np.shape(data)[1]) if i not in keys]
        if self.get_parameter("univariate"):
            features_col = targets

        features_train = [data[i][:, features_col] for i in [indices_map(i, start_positions) for i in start_positions]]
        if len(start_positions) > 0:
            test_features_values = [data[i][:, features_col] for i in
                                    [indices_map(i, range(self.shift, start_positions[0], self.step_length)) for i in
                                     range(self.shift, start_positions[0], self.step_length)]]
        # else:
        #     features_train = [data[i] for i in [indices_map(i, start_positions) for i in start_positions]]
        #     if len(start_positions) >0:
        #         test_features_values = [data[i] for i in [indices_map(i, range(self.shift, start_positions[0], self.step_length) )for i in range(self.shift, start_positions[0], self.step_length)]]
        if (len(test_features_values) == len(test_target_values)) and len(test_features_values) > 0:
            self._test_data_features.extend(test_features_values)
            self._test_data_target.extend(test_target_values)
            self._test_data_keys.extend(test_keys_values)
        if self.targets is not None:
            return zip(target_keys, features_train, target_values)
        else:
            return iter(target_keys, features_train)

    def _series_to_timeseries_train(self, data, keys, targets):
        dataset={'train': zip([],[],[]),
                 'test': zip([],[],[])}

        end_index = len(data)
        if end_index<self.window_length+self.horizon:
            return dataset

        start = self.window_length
        end = end_index - self.horizon
        nb_test_steps=end-(self.nb_test_steps+start)
        if (self.window_length+self.horizon)>=end_index:
            nb_test_steps=end-start

        X=[]
        y=[]
        key=[]
        for i in range(start, end):
            indices = range(i - self.window_length, i)
            features_col = [i for i in range(np.shape(data)[1]) if i not in keys]
            if self.get_parameter("univariate"):
                features_col = targets
            X.append(data[indices][:,features_col])
            key.append(data[indices][:,keys])



            if self.targets is not None:
                indicey = range(i, i  + self.horizon)

                y.append(data[indicey][:,targets])


        dataset['train']=zip(key[:nb_test_steps], X[:nb_test_steps], y[:nb_test_steps])
        dataset['test']=zip(key[nb_test_steps:], X[nb_test_steps:], y[nb_test_steps:])

        return dataset


    def _series_to_timeseries_predict(self, data, keys, targets):
        dataset={'predict': zip([],[],[])}

        end_index = len(data)
        if end_index<self.window_length+1:
            return dataset

        start = self.window_length
        end = end_index

        X=[]
        y=[]
        key=[]
        for i in range(start, end):
            indices = range(i - self.window_length, i)
            features_col = [i for i in range(np.shape(data)[1]) if i not in keys]
            if self.get_parameter("univariate"):
                features_col = targets
            X.append(data[indices][:,features_col])
            key.append(data[indices][:,keys])



            if self.targets is not None:
                indicey = range(i , i + 1)

                y.append(data[indicey][:,targets])

        pred_index=end_index-self.window_length-1
        dataset['predict']=zip(key[pred_index:], X[pred_index:], y[pred_index])


        return dataset
    @property
    def datasets(self):
        dataset={'train':[],
                 'test':[],
                 'predict':[]}
        for group in self.data[1]:
            group = group.sort_values(by=self.get_parameter("timestamp"), ascending=True)

            targets = [group.columns.get_loc(c) for c in self.targets if c in group]
            keys = [group.columns.get_loc(c) for c in self.get_parameter("group") + [self.get_parameter("timestamp")] if
                    c in group]
            d=self._series_to_timeseries(group.values, keys, targets)
            data= self._series_to_timeseries_train(group.values, keys, targets)
            dataset['train'].extend(list(data['train']))
            dataset['test'].extend(list(data['test']))
            dataset['predict'].extend(list(self._series_to_timeseries_predict(group.values, keys, targets)['predict']))
        return dataset

    @property
    def train(self):

        for group in self.data[1]:
            group = group.sort_values(by=self.get_parameter("timestamp"), ascending=False)

            targets = [group.columns.get_loc(c) for c in self.targets if c in group]
            keys = [group.columns.get_loc(c) for c in self.get_parameter("group") + [self.get_parameter("timestamp")] if
                    c in group]

            for (keys, feature, label) in self._series_to_timeseries_train(group.values, keys, targets):
                yield np.array(keys), np.array(feature), np.array(label)

    @property
    def test(self):
        if len(self._test_data_features) != len(self._test_data_target):
            raise ValueError("Features array and target arrays cannot have different lengths")

        return zip(self._test_data_keys, self._test_data_features, self._test_data_target)

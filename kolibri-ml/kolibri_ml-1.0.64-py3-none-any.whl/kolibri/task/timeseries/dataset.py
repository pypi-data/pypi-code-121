import math
import warnings
import random

from typing import List
from typing import Optional
import pandas as pd


from typing import Union
from copy import deepcopy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DatetimeIndex

from kolibri.logger import get_logger
from sklearn.model_selection import TimeSeriesSplit

tslogger=get_logger(__name__)

class TimeSeriesData():
    """TimeSeriesData is the main class to handle your time series data.
    It prepares the series for exploration analyzing, implements feature generation with Transforms
    and generation of future points.

    Notes
    -----
    TimeSeriesData supports custom indexing and slicing method.
    It maybe done through these interface: TimeSeriesData[timestamp, segment, column]
    If at the start of the period dataset contains NaN those timestamps will be removed.


    """

    idx = pd.IndexSlice

    defaults={
        'frequency': None,
        'inferred-freq': None,
        'timestamp':None,
        "group":[],
        "segment":None,
        "target":None,
        "features":None,
        "split-type": "by-time-series",
        "normalize-group":[],
        "normalization-method": "zscore",
        "aggfunc":'sum',
        "instance-col":[]
    }

    def __init__(self, df, config={}):
        """Init TimeSeriesData.

        Parameters
        ----------
        df:
            dataframe with timeseries
        config:
            configuration object

        """

        self.defaults.update(config)

        self.segment=self.defaults["segment"]
        self.group_cols=self.defaults["group"]
        self.target=self.defaults["target"]

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Data should be a Pandas dataframe. recieved: "+type(df))

        if not isinstance(self.defaults.get("normalize-group", []), list):
            raise ValueError("'normalize-group' config error. Expected list, got "+type(self.defaults.get("normalize-group", [])))

        for gr in self.defaults.get("normalize-group", []):
            if gr not in df.columns:
                raise ValueError("Column "+gr+" does not exist in the provided dataframe")
        self.timestamp=self.defaults['timestamp']

        if len(self.defaults["normalize-group"])>0:
            self.normalizers={}
            from kolibri.preprocess.tabular import Normalizer
            grouped=df.groupby(self.defaults["normalize-group"])

            for group in grouped:
                normlizer = Normalizer(self.defaults)

                df_group=df.iloc[group[1].index]
                df.loc[group[1].index,self.defaults['target']]=normlizer.fit_transform(df_group)[self.defaults['target']]
                self.normalizers[group[0]]=deepcopy(normlizer)



        if df is not None:
            self.df=self._to_timeseries_dataset(df.copy(deep=True))


    def __repr__(self):
        return self.df.__repr__()

    def _repr_html_(self):
        return self.df._repr_html_()

    def __getitem__(self, item):
        if isinstance(item, slice) or isinstance(item, str):
            df = self.df.loc[self.idx[item]]
        elif len(item) == 2 and item[0] is Ellipsis:
            df = self.df.loc[self.idx[:], self.idx[:, item[1]]]
        elif len(item) == 2 and item[1] is Ellipsis:
            df = self.df.loc[self.idx[item[0]]]
        else:
            df = self.df.loc[self.idx[item[0]], self.idx[item[1], item[2]]]
        first_valid_idx = df.first_valid_index()
        df = df.loc[first_valid_idx:]
        return df

    def _index_timestamp(self, df):
        self.timestamp=self.defaults["timestamp"]
        if self.timestamp is not None:
            if self.timestamp not in df.columns:
                raise ValueError("column "+self.timestamp+" not in the Dataframe")
            else:
                try:
                    df[self.timestamp]=pd.to_datetime(df[self.timestamp])
                    df=df.set_index(self.timestamp)
                except:
                    pass
        return df

    def make_future(self, future_steps: int):
        """Return new TimeSeriesData with future steps.

        Parameters
        ----------
        future_steps:
            number of timestamp in the future to build features for.

        Returns
        -------
        :
            dataset with features in the future.

        Examples
        --------
        >>> from etna.datasets import generate_const_df
        >>> df = generate_const_df(
        ...    periods=30, start_time="2021-06-01",
        ...    n_groups=2, scale=1
        ... )
        >>> df_regressors = pd.DataFrame({
        ...     "timestamp": list(pd.date_range("2021-06-01", periods=40))*2,
        ...     "regressor_1": np.arange(80), "regressor_2": np.arange(80) + 5,
        ...     "segment": ["segment_0"]*40 + ["segment_1"]*40
        ... })
        >>> df_ts_format = TimeSeriesData.to_dataset(df)
        >>> df_regressors_ts_format = TimeSeriesData.to_dataset(df_regressors)
        >>> ts = TimeSeriesData(df_ts_format, "D", df_exog=df_regressors_ts_format)
        >>> ts.make_future(4)
        segment      segment_0                      segment_1
        feature    regressor_1 regressor_2 target regressor_1 regressor_2 target
        timestamp
        2021-07-01          30          35    nan          70          75    nan
        2021-07-02          31          36    nan          71          76    nan
        2021-07-03          32          37    nan          72          77    nan
        2021-07-04          33          38    nan          73          78    nan
        """
        max_date_in_dataset = self.df.index.max()
        future_dates = pd.date_range(
            start=max_date_in_dataset, periods=future_steps + 1, freq=self.freq, closed="right"
        )

        new_index = self.raw_df.index.append(future_dates)
        df = self.raw_df.reindex(new_index)
        df.index.name = "timestamp"

        future_dataset = df.tail(future_steps).copy(deep=True)
        future_dataset = future_dataset.sort_index(axis=1, level=(0, 1))
        future_ts = TimeSeriesData(future_dataset)
        return future_ts

    @property
    def segments(self) -> List[str]:

        return self.df.columns.get_level_values("segment").unique().tolist()


    @property
    def groups(self) -> List[str]:
        for col in self.group_cols:
            if col not in self.df.index.names:
                raise ValueError("Unknown Inexing issue")

        return self.df.index.get_level_values(0).unique().tolist()

    def plot( self, n_segments = 10, group=None, segments= None, seed= 1):
        """Plot of random or chosen segments.

        Parameters
        ----------
        n_segments:
            number of random segments to plot
        segments:
            segments to plot
        seed:
            seed for local random state
        """
        if not segments:
            segments = self.segments
        rnd_state = np.random.RandomState(seed)
        if self.group_cols !=[]:
            if group is None:
                group=rnd_state.choice(self.groups, size=1)[0]
        k = min(n_segments, len(segments))
        columns_num = min(2, k)
        rows_num = math.ceil(k / columns_num)
        _, ax = plt.subplots(rows_num, columns_num, figsize=(20, 5 * rows_num), squeeze=False)
        ax = ax.ravel()

        for i, segment in enumerate(sorted(rnd_state.choice(segments, size=k, replace=False))):
            try:
                df_slice = self.df[self.df.index.get_level_values(self.group_cols[0])==group][segment, self.target]
                ax[i].plot(df_slice.index.get_level_values(self.timestamp).tolist(), df_slice.values)
                ax[i].set_title(segment)
            except:
                pass

        plt.show()


    @staticmethod
    def to_flatten(df):
        """Return pandas DataFrame with flatten index.

        Parameters
        ----------
        df:
            DataFrame in ETNA format.

        Returns
        -------
        pd.DataFrame
            with TimeSeriesData data

        Examples
        --------
        >>> from etna.datasets import generate_const_df
        >>> df = generate_const_df(
        ...    periods=30, start_time="2021-06-01",
        ...    n_groups=2, scale=1
        ... )
        >>> df.head(5)
            timestamp    segment  target
        0  2021-06-01  segment_0    1.00
        1  2021-06-02  segment_0    1.00
        2  2021-06-03  segment_0    1.00
        3  2021-06-04  segment_0    1.00
        4  2021-06-05  segment_0    1.00
        >>> df_ts_format = TimeSeriesData.to_dataset(df)
        >>> TimeSeriesData.to_flatten(df_ts_format).head(5)
           timestamp  target    segment
        0 2021-06-01     1.0  segment_0
        1 2021-06-02     1.0  segment_0
        2 2021-06-03     1.0  segment_0
        3 2021-06-04     1.0  segment_0
        4 2021-06-05     1.0  segment_0
        """
        aggregator_list = []
        category = []
        segments = df.columns.get_level_values("segment").unique().tolist()
        for segment in segments:
            if df[segment].select_dtypes(include=["category"]).columns.to_list():
                category.extend(df[segment].select_dtypes(include=["category"]).columns.to_list())
            aggregator_list.append(df[segment].copy())
            aggregator_list[-1]["segment"] = segment
        df = pd.concat(aggregator_list)
        df = df.reset_index()
        category = list(set(category))
        df[category] = df[category].astype("category")
        df.columns.name = None
        return df

    def to_pandas(self, flatten: bool = False) -> pd.DataFrame:
        """Return pandas DataFrame.

        Parameters
        ----------
        flatten:
            If False return pd.DataFrame with multiindex
            if True with flatten index

        Returns
        -------
        pd.DataFrame
            with TimeSeriesData data

        Examples
        --------
        >>> from etna.datasets import generate_const_df
        >>> df = generate_const_df(
        ...    periods=30, start_time="2021-06-01",
        ...    n_groups=2, scale=1
        ... )
        >>> df.head(5)
            timestamp    segment  target
        0  2021-06-01  segment_0    1.00
        1  2021-06-02  segment_0    1.00
        2  2021-06-03  segment_0    1.00
        3  2021-06-04  segment_0    1.00
        4  2021-06-05  segment_0    1.00
        >>> df_ts_format = TimeSeriesData.to_dataset(df)
        >>> ts = TimeSeriesData(df_ts_format, "D")
        >>> ts.to_pandas(True).head(5)
           timestamp  target    segment
        0 2021-06-01     1.0  segment_0
        1 2021-06-02     1.0  segment_0
        2 2021-06-03     1.0  segment_0
        3 2021-06-04     1.0  segment_0
        4 2021-06-05     1.0  segment_0
        >>> ts.to_pandas(False).head(5)
        segment    segment_0 segment_1
        feature       target    target
        timestamp
        2021-06-01      1.00      1.00
        2021-06-02      1.00      1.00
        2021-06-03      1.00      1.00
        2021-06-04      1.00      1.00
        2021-06-05      1.00      1.00
        """
        if not flatten:
            return self.df.copy()
        return self.to_flatten(self.df)


    def _to_timeseries_dataset(self, df):
        """Convert pandas dataframe to DateTimeData format.
        """

        if not isinstance(self.group_cols, list):
            raise ValueError("'groups_cols' config error. Expected list, got "+type(self.defaults["group"]))

        index=self.group_cols
        index.append(self.timestamp)
#        df=pd.DataFrame(df.groupby(by=index+[self.segment]).sum()).reset_index()

        df[self.timestamp] = pd.to_datetime(df[self.timestamp])
#        df1 = df.pivot(index=index, columns=self.segment)
        df=pd.pivot_table(df, index=index, columns=self.segment, fill_value=0, aggfunc='sum')
        if df.columns.nlevels>1:
            df = df.reorder_levels([1, 0], axis=1)
            df.columns.names = ["segment", "feature"]
        df = df.sort_index(axis=1, level=(0, 1))

        return df

    def _find_all_borders(
        self,
        train_start=None,
        train_end=None,
        test_start=None,
        test_end=None,
        test_size=None,
    ):
        """Find borders for train_test_split if some values wasn't specified."""
        if test_end is not None and test_start is not None and test_size is not None:
            warnings.warn(
                "test_size, test_start and test_end cannot be applied at the same time. test_size will be ignored"
            )

        if test_end is None:
            if test_start is not None and test_size is not None:
                test_start_idx = self.df.index.get_loc(test_start)
                if test_start_idx + test_size > len(self.df.index):
                    raise ValueError(
                        f"test_size is {test_size}, but only {len(self.df.index) - test_start_idx} available with your test_start"
                    )
                test_end_defined = self.df.index[test_start_idx + test_size]
            elif test_size is not None and train_end is not None:
                test_start_idx = self.df.index.get_loc(train_end)
                test_start = self.df.index[test_start_idx + 1]
                test_end_defined = self.df.index[test_start_idx + test_size]
            else:
                test_end_defined = self.df.index.max()
        else:
            test_end_defined = test_end

        if train_start is None:
            train_start_defined = self.df.index.min()
        else:
            train_start_defined = train_start

        if train_end is None and test_start is None and test_size is None:
            raise ValueError("At least one of train_end, test_start or test_size should be defined")

        if test_size is None:
            if train_end is None:
                test_start_idx = self.df.index.get_loc(test_start)
                train_end_defined = self.df.index[test_start_idx - 1]
            else:
                train_end_defined = train_end

            if test_start is None:
                train_end_idx = self.df.index.get_loc(train_end)
                test_start_defined = self.df.index[train_end_idx + 1]
            else:
                test_start_defined = test_start
        else:
            if test_start is None:
                test_start_idx = self.df.index.get_loc(test_end_defined)
                test_start_defined = self.df.index[test_start_idx - test_size + 1]
            else:
                test_start_defined = test_start

            if train_end is None:
                test_start_idx = self.df.index.get_loc(test_start_defined)
                train_end_defined = self.df.index[test_start_idx - 1]
            else:
                train_end_defined = train_end

        if np.datetime64(test_start_defined) < np.datetime64(train_end_defined):
            raise ValueError("The beginning of the test goes before the end of the train")

        return train_start_defined, train_end_defined, test_start_defined, test_end_defined

    def train_test_split(
        self,
        train_start = None,
        train_end = None,
        test_start = None,
        test_end = None,
        test_size = None,
    ):
        """Split given df with train-test timestamp indices or size of test set.
        In case of inconsistencies between test_size and (test_start, test_end), test_size is ignored

        Parameters
        ----------
        train_start:
            start timestamp of new train dataset, if None first timestamp is used
        train_end:
            end timestamp of new train dataset, if None previous to test_start timestamp is used
        test_start:
            start timestamp of new test dataset, if None next to train_end timestamp is used
        test_end:
            end timestamp of new test dataset, if None last timestamp is used
        test_size:
            number of timestamps to use in test set

        Returns
        -------
        train, test:
            generated datasets

        Examples
        --------
        >>> from etna.datasets import generate_ar_df
        >>> pd.options.display.float_format = '{:,.2f}'.format
        >>> df = generate_ar_df(100, start_time="2021-01-01", n_segments=3)
        >>> df = TSDataset.to_dataset(df)
        >>> ts = TSDataset(df, "D")
        >>> train_ts, test_ts = ts.train_test_split(
        ...     train_start="2021-01-01", train_end="2021-02-01",
        ...     test_start="2021-02-02", test_end="2021-02-07"
        ... )
        >>> train_ts.df.tail(5)
        segment    segment_0 segment_1 segment_2
        feature       target    target    target
        timestamp
        2021-01-28     -2.06      2.03      1.51
        2021-01-29     -2.33      0.83      0.81
        2021-01-30     -1.80      1.69      0.61
        2021-01-31     -2.49      1.51      0.85
        2021-02-01     -2.89      0.91      1.06
        >>> test_ts.df.head(5)
        segment    segment_0 segment_1 segment_2
        feature       target    target    target
        timestamp
        2021-02-02     -3.57     -0.32      1.72
        2021-02-03     -4.42      0.23      3.51
        2021-02-04     -5.09      1.02      3.39
        2021-02-05     -5.10      0.40      2.15
        2021-02-06     -6.22      0.92      0.97
        """
        train_start_defined, train_end_defined, test_start_defined, test_end_defined = self._find_all_borders(
            train_start, train_end, test_start, test_end, test_size
        )

        if pd.Timestamp(test_end_defined) > self.df.index.max():
            warnings.warn(f"Max timestamp in df is {self.df.index.max()}.")
        if pd.Timestamp(train_start_defined) < self.df.index.min():
            warnings.warn(f"Min timestamp in df is {self.df.index.min()}.")

        train_df = self.df[train_start_defined:train_end_defined][self.raw_df.columns]  # type: ignore
        train_raw_df = self.raw_df[train_start_defined:train_end_defined]  # type: ignore
        train = TimeSeriesData(df=train_df,config= self.defaults)
        train.raw_df = train_raw_df

        test_df = self.df[test_start_defined:test_end_defined][self.raw_df.columns]  # type: ignore
        test_raw_df = self.raw_df[train_start_defined:test_end_defined]  # type: ignore
        test = TimeSeriesData(df=test_df, config=self.defaults)
        test.raw_df = test_raw_df

        return train, test

    @property
    def index(self) -> pd.core.indexes.datetimes.DatetimeIndex:
        """Return TSDataset timestamp index.

        Returns
        -------
        pd.core.indexes.datetimes.DatetimeIndex
            timestamp index of TSDataset
        """
        return self.df.index

    @property
    def columns(self) -> pd.core.indexes.multi.MultiIndex:
        """Return columns of self.df.

        Returns
        -------
        pd.core.indexes.multi.MultiIndex
            multiindex of dataframe with target and features.
        """
        return self.df.columns

    @property
    def loc(self) -> pd.core.indexing._LocIndexer:
        """Return self.df.loc method.

        Returns
        -------
        pd.core.indexing._LocIndexer
            dataframe with self.df.loc[...]
        """
        return self.df.loc

    def isnull(self) -> pd.DataFrame:
        """Return dataframe with flag that means if the correspondent object in self.df is null.

        Returns
        -------
        pd.Dataframe
            is_null dataframe
        """
        return self.df.isnull()

    def head(self, n_rows: int = 5):
        """Return the first `n` rows.

        Mimics pandas method.

        This function returns the first `n` rows for the object based
        on position. It is useful for quickly testing if your object
        has the right type of data in it.
        For negative values of `n`, this function returns all rows except
        the last `n` rows, equivalent to ``df[:-n]``.

        Parameters
        ----------
        n_rows:
            number of rows to select.

        Returns
        -------
        pd.DataFrame
            the first `n` rows or 5 by default.
        """
        return self.df.head(n_rows)

    def tail(self, n_rows: int = 5) -> pd.DataFrame:
        """Return the last `n` rows.

        Mimics pandas method.

        This function returns last `n` rows from the object based on
        position. It is useful for quickly verifying data, for example,
        after sorting or appending rows.
        For negative values of `n`, this function returns all rows except
        the first `n` rows, equivalent to ``df[n:]``.

        Parameters
        ----------
        n_rows:
            number of rows to select.

        Returns
        -------
        pd.DataFrame
            the last `n` rows or 5 by default.

        """
        return self.df.tail(n_rows)

    def describe(
        self,
        percentiles: Optional[List[float]] = None,
        include: Optional[Union[str, List[np.dtype]]] = None,
        exclude: Optional[Union[str, List[np.dtype]]] = None,
        datetime_is_numeric: bool = False,
    ) -> pd.DataFrame:
        """Generate descriptive statistics.

        Mimics pandas method.

        Descriptive statistics include those that summarize the central
        tendency, dispersion and shape of a
        dataset's distribution, excluding ``NaN`` values.

        Parameters
        ----------
        percentiles : list-like of numbers, optional
            The percentiles to include in the output. All should
            fall between 0 and 1. The default is
            ``[.25, .5, .75]``, which returns the 25th, 50th, and
            75th percentiles.
        include : 'all', list-like of dtypes or None (default), optional
            A white list of data types to include in the result. Ignored
            for ``Series``. Here are the options:
            - 'all' : All columns of the input will be included in the output.
            - A list-like of dtypes : Limits the results to the
              provided data types.
              To limit the result to numeric types submit
              ``numpy.number``. To limit it instead to object columns submit
              the ``numpy.object`` data type. Strings
              can also be used in the style of
              ``select_dtypes`` (e.g. ``df.describe(include=['O'])``). To
              select pandas categorical columns, use ``'category'``
            - None (default) : The result will include all numeric columns.
        exclude : list-like of dtypes or None (default), optional,
            A black list of data types to omit from the result. Ignored
            for ``Series``. Here are the options:
            - A list-like of dtypes : Excludes the provided data types
              from the result. To exclude numeric types submit
              ``numpy.number``. To exclude object columns submit the data
              type ``numpy.object``. Strings can also be used in the style of
              ``select_dtypes`` (e.g. ``df.describe(include=['O'])``). To
              exclude pandas categorical columns, use ``'category'``
            - None (default) : The result will exclude nothing.
        datetime_is_numeric : bool, default False
            Whether to treat datetime dtypes as numeric. This affects statistics
            calculated for the column. For DataFrame input, this also
            controls whether datetime columns are included by default.

        Returns
        -------
        pd.DataFrame
            Summary statistics of the TSDataset provided.

        """
        return self.df.describe(percentiles, include, exclude, datetime_is_numeric)
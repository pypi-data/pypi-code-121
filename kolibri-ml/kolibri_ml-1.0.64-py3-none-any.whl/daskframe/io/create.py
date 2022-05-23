from typing import Union
import warnings
from abc import abstractmethod

import pandas as pd
#from daskframe.base.basedaskframe import BaseDaskFrame
#from daskframe.helpers.types import *
from kdmt.infer import is_dict, is_tuple
from daskframe.dataframe import DaskFrame
from daskframe.converter import pandas_to_dask_dataframe
class Create:
    def __init__(self):
        pass


    @staticmethod
    def df(*args, **kwargs):
        return DaskFrame(*args, **kwargs)

    def _dictionary(self, dict):

        new_dict = {}

        for key, values in dict.items():
            if is_tuple(key):
                dtype = None
                nulls = False
                if len(key) == 4:
                    name, dtype, nulls, force_dtype = key
                if len(key) == 3:
                    name, dtype, nulls = key
                elif len(key) == 2:
                    name, dtype = key
            else:
                name = key
                dtype = None
                nulls = False

            new_dict[(name, dtype, nulls, False)] = values

        return new_dict

    @property
    def _pd(self):
        return pd

    def _dfd_from_dict(self, dict) -> 'InternalDataFrameType':
        pd_dict = {}
        for (name, dtype, nulls, force_dtype), values in dict.items():
            dtype = self.op.constants.COMPATIBLE_DTYPES.get(dtype, dtype) if force_dtype else None
            pd_series = self._pd.Series(values, dtype=dtype)
            pd_dict.update({name: pd_series})
        return self._pd.DataFrame(pd_dict)

    def _df_from_dfd(self, dfd, n_partitions=1, *args, **kwargs):
        return DaskFrame(pandas_to_dask_dataframe(dfd, n_partitions), *args, **kwargs)

    def dataframe(self, data: Union[dict, 'InternalDataFrameType'] = None, force_data_types=False,
                  n_partitions: int = 1, *args, **kwargs) -> 'DataFrameType':
        """Creates a dataframe using a dictionary or a Pandas DataFrame

        Creates a dataframe using the form
        `{"Column name": ["value 1", "value 2"], ...}` or 
        `{("Column name", "str", True, True): ["value 1", "value 2"]}`,
        where the tuple uses the form `(str, str, boolean, boolean)` for 
        `(name, data type, allow nulls, force data type in creation)`. You can
        also pass 2-length and 3-length tuples.
        :param data: A pandas dataframe or dictionary to construct the dataframe.
        :param force_data_types: Force every data type passed to data.
        :param n_partitions: Number of partitions (For distributed engines only)
        :return: BaseDaskFrame
        """

        if data is None and len(kwargs):
            data = kwargs
            kwargs = {}

        data_dict = None

        if is_dict(data):
            data_dict = self._dictionary(data)
            data = self._dfd_from_dict(data_dict)

        df = self._df_from_dfd(data, n_partitions=n_partitions, *args, **kwargs)

        return df


    def from_append(self, daskframes):
        if len(daskframes)==0:
            return None

        result_data=daskframes[0].data
        for df in daskframes[1:]:
            if not isinstance(df, BaseDaskFrame):
                raise ValueError
            result_data=result_data.append(df.data)

        return self.df(result_data)
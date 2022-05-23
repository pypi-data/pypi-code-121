from daskframe.io.create import Create
from daskframe.dataframe import DaskFrame

from daskframe.helpers.converter import pandas_to_dask_dataframe


class Create(Create):
    
    def _df_from_dfd(self, dfd, n_partitions=1, *args, **kwargs):
        return DaskFrame(pandas_to_dask_dataframe(dfd, n_partitions), *args, **kwargs, op=self.op)

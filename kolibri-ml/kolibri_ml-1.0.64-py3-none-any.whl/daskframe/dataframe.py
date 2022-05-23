import pandas as pd
import dask.dataframe as dd
from kdmt.lists import val_to_list
import numpy as np
from daskframe.io.save import Save
#from daskframe.pandas_dataframe import PandasDataFrame
from daskframe.converter import pandas_to_dask_dataframe
from abc import ABC
import dask.array as da
from tabulate import tabulate
from kdmt.jupyter import isnotebook, print_html
from collections.abc import Iterable


class DaskFrame(ABC):

    def __init__(self, data):
        data = self._compatible_data(data)
        self.data = data
        self.buffer = None
        self.updated = None
        self.meta = {}
        self.le = None

    @property
    def root(self):
        return self

    def _assign(self, kw_columns: dict):

        dfd = self.root.data

        fix_indices = False

        for key in kw_columns:
            kw_column = kw_columns[key]

            if isinstance(kw_column, (list,)):
                kw_column = pd.Series(kw_column)

            if isinstance(kw_column, pd.Series):
                # TO-DO: A Pandas Series should be assignable to a Dask DataFrame
                kw_column = dd.from_pandas(kw_column, npartitions=dfd.npartitions)

            if isinstance(kw_column, (np.ndarray, da.Array)):
                kw_column = dd.from_array(kw_column)

            if isinstance(kw_column, (dd.Series, dd.DataFrame)):

                if dfd.known_divisions and not kw_column.known_divisions:
                    kw_column = kw_column.reset_index(drop=True)
                elif not dfd.known_divisions and kw_column.known_divisions:
                    dfd = dfd.reset_index(drop=True)
                    fix_indices = True

                # print("kw_column.compute()")
                # print(kw_column.to_frame().reset_index(drop=False).compute())
                # print(dfd.reset_index(drop=False).compute())

                if isinstance(kw_column, dd.DataFrame):
                    if key in kw_column:
                        # the incoming series has the same column key
                        kw_column = kw_column[key]
                    else:
                        # the incoming series has no column key
                        kw_column = kw_column[list(kw_column.columns)[0]]
                else:
                    kw_column.name = key

            kw_columns[key] = kw_column

        if fix_indices:
            for key in kw_columns:
                kw_column = kw_columns[key]
                if isinstance(kw_column, dd.Series) and not kw_column.known_divisions:
                    kw_columns[key] = kw_column.reset_index(drop=True)

        kw_columns = {str(key): kw_column for key, kw_column in kw_columns.items()}

        return dfd.assign(**kw_columns)


    def new(self, dfd):
        df = self.__class__(dfd)
        return df

    @staticmethod
    def _compatible_data(data):
        if isinstance(data, (pd.DataFrame, pd.Series)):
            data = pandas_to_dask_dataframe(data)
        
        if isinstance(data, dd.Series):
            data = data.to_frame()

        return data

    def _base_to_dfd(self, pdf, n_partitions):
        return pandas_to_dask_dataframe(pdf, n_partitions)

    @property
    def rows(self):
        from daskframe.rows import Rows
        return Rows(self)

    @property
    def cols(self):
        from daskframe.columns import Columns
        return Columns(self)

    def unstack(self, index=None, level=-1):
            """
            Return reshaped DataFrame organized by given index / column values.
            :param index: Column(s) to use as index.
            :param level: Column(s) to unstack.
            :return:
            """
            if isinstance(index, list) and len(index) > 1:
                index_col = '_'.join(index)
                self = self.cols.nest(index, separator="_", output_col=index_col, drop=False)
            dfd = self.root.data

            dfd = dfd.set_index(index_col)

            #        dfd = dfd.unstack(level=level, fill_value=None).reset_index()

            def _join(val):
                if isinstance(val, Iterable):
                    return list(filter(lambda l: l, val))[-1]
                else:
                    return str(val)

            dfd.columns = dfd.columns.map(_join).str.strip('_')

            return self.root.new(dfd)

    def pivot(self, col, groupby, agg="first", values=None):
        """
        Return reshaped DataFrame organized by given index / column values.
        :param col: Column to use to make new frame's columns.
        :param groupby: Column to use to make new frame's index.
        :param agg: Aggregation to use for populating new frame's values.
        :param values: Column to use for populating new frame's values.
        :return:
        """

        df = self.root

        if values is not None:
            agg = ( agg, values)

        groupby = val_to_list(groupby)
        by = groupby + [col]
        if values is None:
            agg = (agg, col)

        return df.cols.groupby(by=by, agg=agg).unstack(by)

    def display(self, limit=10, cols=None, title=None, truncate=True, plain_text=False, highlight=[]):
        # TODO: limit, columns, title, truncate
        df = self

        if isnotebook() and not plain_text:
            print_html(df.table(limit, cols, title, truncate, highlight))

        else:
            print(df.ascii(limit, cols))

    def print(self, limit=10, cols=None):
        print(self.ascii(limit, cols))

    def table(self, limit=None, cols=None, title=None, truncate=True, highlight=[]):
        df = self
        try:
            if isnotebook():
                # TODO: move the html param to the ::: if is_notebook() and engine.output is "html":

                print_html(df.table_html(title=title, limit=limit, cols=cols, truncate=truncate, highlight=highlight))
                return

        except NameError as e:
            print(e)

        return df.ascii(limit, cols)

    def ascii(self, limit=10, cols=None):
        df = self
        if not cols:
            cols = "*"

        limit = min(limit, df.rows.approx_count())
        return tabulate(df.rows.limit(limit + 1).cols.select(cols).to_pandas(),
                        headers=[f"""{i}\n({j})""" for i,
                                 j in df.cols.data_types(tidy=False).items()],
                        tablefmt="simple",
                        showindex="never")+"\n"


    @property
    def save(self):
        return Save(self)

    def show(self, n=10):
        """
        :return:
        """
        return self.data.head(n=n)

    @property
    def functions(self):
        from daskframe.dask_functions import DaskFunctions
        return DaskFunctions(self)


    def partitions(self):
        return self.data.npartitions


    def to_pandas(self):
        return self.data.compute()
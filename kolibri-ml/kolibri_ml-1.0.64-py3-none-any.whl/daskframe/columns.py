import numpy as np
import dask.array as da
import dask.dataframe as dd
from daskframe.utils import parse_columns
from abc import ABC
from daskframe.utils import format_dict
from kdmt.lists import val_to_list
from kdmt.infer import is_dict
import regex as re
from functools import reduce

MAX_BUCKETS=32




class Columns(ABC):

    def __init__(self, root):
        self.root = root
        self.F = self.root.functions


    def names(self):
        return list(self.root.data.columns)
    def keep(self, cols=None, regex=None):
        """
        Drop a list of columns
        :param cols: "*", column name or list of column names to be processed.
        :param regex: Regex expression to select the columns
        :return:
        """
        df = self.root
        dfd = df.data
        _cols = parse_columns(df, "*")
        if regex:
            # r = re.compile(regex)
            cols = [c for c in _cols if re.match(regex, c)]

        cols = parse_columns(df, cols)
#        check_column_numbers(cols, "*")

        dfd = dfd.drop(columns=list(set(_cols) - set(cols)))

        return self.root.new(dfd)


    def append(self, dfs):
        """

        :param dfs:
        :return:
        """

        dfs = val_to_list(dfs)

        df = self.root
        dfd = dd.concat([df.data.reset_index(drop=True), *[_df.data.reset_index(drop=True) for _df in dfs]], axis=1)
        return self.root.new(dfd)
        # return dfd

    def reverse(self, cols="*", output_cols=None):
        """
        Reverse values as strings
        :param cols: '*', list of columns names or a single column name.
        :return:
        """
        df = self.root
        return df.cols.apply(cols, "reverse", func_return_type=str,
                             filter_col_by_dtypes=STRING_TYPES,
                             output_cols=output_cols, mode="vectorized")

    @staticmethod
    def astype(*args, **kwargs):
        pass

    def data_types(self, cols="*", tidy=True):
        """
        Return the column(s) data type as string
        :param columns: Columns to be processed
        :return: {col_name: data_type}
        """
        df = self.root
        cols = parse_columns(df, cols)
        data_types = ({k: str(v) for k, v in dict(df.data.dtypes).items()})
        return format_dict({col_name: data_types[col_name] for col_name in cols}, tidy=tidy)

    def select(self, cols="*", regex=None, data_type=None, invert=False, accepts_missing_cols=False):
        """
        Select columns using index, column name, regex to data type
        :param cols: "*", column name or list of column names to be processed.
        :param regex: Regular expression to filter the columns
        :param data_type: Data type to be filtered for
        :param invert: Invert the selection
        :param accepts_missing_cols:
        :return:
        """

        df = self.root
        cols = parse_columns(df, cols if regex is None else regex, is_regex=regex is not None,
                             filter_by_column_types=data_type, invert=invert,
                             accepts_missing_cols=accepts_missing_cols)

        dfd = df.data
        if cols is not None:
            dfd = dfd[cols]
        return self.root.new(dfd)

    @staticmethod
    def to_timestamp(cols, date_format=None, output_cols=None):
        pass

    def nest(self, cols="*", separator="", output_col=None, shape="string", drop=False):
        df = self.root

        dfd = df.data

        if output_col is None:
            output_col = name_col(cols)

        cols = parse_columns(df, cols)

        output_ordered_columns = df.cols.names()

        # cudfd do nor support apply or agg join for this operation
        if shape == "vector" or shape == "array":
            dfd = dfd.assign(**{output_col: dfd[cols].values.tolist()})

        elif shape == "string":
            dfds = [dfd[input_col].astype(str) for input_col in cols]
            dfd = dfd.assign(**{output_col: reduce((lambda x, y: x + separator + y), dfds)})

        if output_col not in output_ordered_columns:
            col_index = output_ordered_columns.index(cols[-1]) + 1
            output_ordered_columns[col_index:col_index] = [output_col]

        if drop is True:
            for input_col in cols:
                if input_col in output_ordered_columns and input_col != output_col:
                    output_ordered_columns.remove(input_col)

        return self.root.new(dfd).cols.select(output_ordered_columns)

    def groupby(self, by, agg):
        """
        This helper function aims to help managing columns name in the aggregation output.
        Also how to handle ordering columns because dask can order columns
        :param by: Column names
        :param agg: List of tuples with the form [("agg", "col")]
        :return:
        """
        df = self.root.data
        compact = {}

        agg_names = None

        if is_dict(agg):
            agg_names = list(agg.keys())
            agg = list(agg.values())

        agg = val_to_list(agg, convert_tuple=False)

        for col_agg in agg:
            if is_dict(col_agg):
                col_agg = list(col_agg.items())[::-1]
            _agg, _col = col_agg
            compact.setdefault(_col, []).append(_agg)

        df = df.groupby(by=by).agg(compact).reset_index()
        agg_names = agg_names or [a[0] + "_" + a[1] for a in agg]
        df.columns = (val_to_list(by) + agg_names)
        df.columns = [str(c) for c in df.columns]
        return self.root.new(df)

    def _series_to_pandas(self, series):
        return series.compute()

    def names(self):
        return list(self.root.data.columns)

    def hist(self, cols="*", buckets=MAX_BUCKETS, compute=True):
        df = self.root
        cols = parse_columns(df, cols)

        result = {}

        for col_name in cols:
            series = self.F.to_float(df.data[col_name])
            result[col_name] = da.histogram(series, bins=buckets, range=[series.min(), series.max()])

        @self.F.delayed
        def format_hist(_cols):
            
            _result = {}
            for col_name in _cols:

                _count, _bins = _cols[col_name]

                dr = {}
                for i in range(len(_count)):
                    key = (float(_bins[i]), float(_bins[i + 1]))
                    if np.isnan(key[0]) and np.isnan(key[1]):
                        continue
                    dr[key] = dr.get(key, 0) + int(_count[i])

                r = [{"lower": k[0], "upper": k[1], "count": count} for k, count in dr.items()]
                if len(r):
                    _result[col_name] = r

            return {"hist": _result}

        result = format_hist(result)

        if compute:
            result = self.F.compute(result)

        return result

"""
Dataframe wrapper. Standardizes interfaces across multiple
implementations of dataframes including pandas, Spark RDD, 
and even dictionaries..
"""
import os, sys, json, glob, copy, time
import numpy as np
import pandas as pd

from datetime import datetime

__all__ = ["DataFrame", "PandasDataFrame", "DictDataFrame"]


class DataFrame(object):
    @staticmethod
    def supported(filename):
        raise Exception("Unsupported")

    @staticmethod
    def read(spec, state):
        """
        Load the tables...
        """
        return state

    @staticmethod
    def duplicate(df):
        raise Exception("Unsupported")


class PandasDataFrame(DataFrame):
    @staticmethod
    def rename(df, columns):
        return df.rename(columns=columns)

    @staticmethod
    def unstack(df, level, **kwargs):
        return df.unstack(level, **kwargs)

    @staticmethod
    def sort_values(df, columns, **kwargs):
        return df.sort_values(columns, **kwargs)

    @staticmethod
    def to_datetime(df, column, **kwargs):
        df[column] = pd.to_datetime(df[column], **kwargs)
        return df

    @staticmethod
    def apply(df, func, **kwargs):
        return df.apply(func, **kwargs)

    @staticmethod
    def drop(df, columns):
        return df.drop(columns, axis=1, inplace=False)

    @staticmethod
    def reset_index(df, **kwargs):
        return df.reset_index(**kwargs)

    @staticmethod
    def groupby(df, columns):
        return df.groupby(columns)

    @staticmethod
    def apply_column(df, column, func, inplace=True, **kwargs):
        if inplace:
            df[column] = df[column].apply(func, **kwargs)
            return df
        else:
            return df[column].apply(func, **kwargs)

    @staticmethod
    def apply_row(df, func):
        df = df.apply(func, axis=1)
        return df

    @staticmethod
    def mean(df):
        return df.mean()

    @staticmethod
    def std(df):
        return df.std()

    @staticmethod
    def dtypes(df):
        return df.dtypes

    @staticmethod
    def shape(df):
        return df.shape

    @staticmethod
    def columns(df):
        return df.columns

    @staticmethod
    def head(df, num=5):
        return df.head(num)

    @staticmethod
    def slice(df, columns):
        return df[columns]

    @staticmethod
    def fillna(df, column, value):
        df[column] = df[column].fillna(value)
        return df

    @staticmethod
    def astype(df, column, value):
        df[column] = df[column].astype(value)
        return df

    @staticmethod
    def merge(left, right, **kwargs):
        return pd.merge(left, right, **kwargs)

    @staticmethod
    def nlargest(df, n, columns, **kwargs):
        return df.nlargest(n, columns, **kwargs)

    @staticmethod
    def slice_columns(df, columns):
        return df[columns]

    @staticmethod
    def tolist(df, transpose=False):
        return df.values.tolist()

    @staticmethod
    def rank(df, column, **kwargs):
        return df[column].rank(**kwargs)

    @staticmethod
    def get_schema(df, table_name):
        return pd.io.sql.get_schema(df, table_name)

    @staticmethod
    def get_generic_dtype(df, c):
        d = df.dtypes[c]
        d = str(d)
        if (d not in ["int64", "float64", "int8", "bool", "category"]) and (
            not d.startswith("datetime")
        ):
            d = "str"
        return d


class DictDataFrame(DataFrame):

    pass

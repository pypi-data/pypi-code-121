import pandas as pd
import numpy as np


def tprint(arg):
    """Prints the contents of a variable/object along with its type."""
    print(arg, type(arg))


def count(iterable, value):
    """Returns an integer of the number of occurences of a value in an iterable."""
    count = 0
    for item in iterable:
        if item == value:
            count += 1
    return int(count)


def reverse_dict(dic: dict):
    """Reverses the keys and values in a dictionary."""
    # Check that values are single items
    accepted_types = [str, int, float]
    for value in dic.values():
        if type(value) not in accepted_types:
            raise Exception("Dictionary values must be single, immutable objects.")

    new_dict = {}
    for key, val in dic.items():
        new_dict[val] = key
    return new_dict


def remove_nan_df_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Removes any rows from a DataFrame that contain
    np.nan values. Returns a new DataFrame."""
    nan_indexes = []
    for index, row in df.iterrows():
        if any(np.isnan(row)):
            nan_indexes.append(index)
    return df.drop(labels=nan_indexes)

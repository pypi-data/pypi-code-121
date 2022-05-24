"""
dict_key: allows you to use a dict as a key for selecting a row in a pandas dataframe.

Author: Erel Segal-Halevi
Since: 2022-05
"""

import pandas

def dict_to_row(df: pandas.DataFrame, key:dict):
    """
    >>> df = pandas.DataFrame({'a': [1,4,1], 'b': [2,5,5], 'c':[3,6,9], 'z':[123, 456, 159]})
    >>> dict_to_row(df, {"a":1, "b":2, "c":3})
    {'a': 1, 'b': 2, 'c': 3, 'z': 123}
    >>> dict_to_row(df, {"a":1, "b":2, "c":9}) is None
    True
    """
    for k,v in key.items():
        df = df[df[k]==v]
    if df.empty:
        return None
    else:
        return df.iloc[0].to_dict()

if __name__=="__main__":
    import doctest
    print(doctest.testmod())


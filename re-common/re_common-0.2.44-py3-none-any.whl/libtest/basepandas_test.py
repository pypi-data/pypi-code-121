import time

from pandas._libs.tslibs.timestamps import Timestamp


def test_dataform_to_numpy():
    import pandas as pd
    import numpy as np
    dicts = {'A': 1.,
             'B': pd.Timestamp('20130102'),
             'C': pd.Series(1, index=list(range(4)), dtype='float32'),
             'D': np.array([3] * 4, dtype='int32'),
             'E': pd.Categorical(["test", "train", "test", "train"]),
             'F': 'foo'}
    from re_common.baselibrary.utils.basepandas import BasePandas
    bp = BasePandas()
    startTime = time.time()
    df = bp.dicts_to_dataform(dicts)
    # 数据类型一致时速度会很快
    print(bp.dataform_to_numpy(df))
    endTime = time.time()
    print(endTime - startTime)
    dicts = {'A': [1.0, Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo'],
             'B': [Timestamp('2013-01-02 00:00:00'), Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo'],
             'C': [1.0, Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo'],
             'D': [3, Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo'],
             'E': ['test', Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo'],
             'F': ['foo', Timestamp('2013-01-02 00:00:00'), 1.0, 3, 'test', 'foo']}


    startTime = time.time()
    df = bp.dicts_to_dataform(dicts)
    # 数据类型一致时速度会很快
    print(bp.dataform_to_numpy(df))
    endTime = time.time()
    print(endTime - startTime)

test_dataform_to_numpy()

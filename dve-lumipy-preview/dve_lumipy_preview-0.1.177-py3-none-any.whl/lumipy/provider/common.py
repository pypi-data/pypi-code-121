from distutils.util import strtobool
from typing import Dict, List, Any

import pandas as pd
from pandas import DataFrame

from lumipy.query.expression.sql_value_type import SqlValType


def table_dict_to_df(table_dict: Dict[str, List[Any]]) -> DataFrame:

    dtypes = table_dict['_DTYPES']
    df = DataFrame({k: v for k, v in table_dict.items() if k != '_DTYPES'})

    for dtype in dtypes:

        col = dtype['Name']
        dtype = SqlValType[dtype['Type']]

        if dtype == SqlValType.Int:
            df[col] = df[col].astype(int)
        elif dtype == SqlValType.Double:
            df[col] = df[col].astype(float)
        elif dtype == SqlValType.DateTime:
            df[col] = pd.to_datetime(df[col], utc=True)
        elif dtype == SqlValType.Date:
            df[col] = pd.to_datetime(df[col], utc=True)
        elif dtype == SqlValType.Boolean:
            df[col] = df[col].apply(lambda x: bool(strtobool(str(x))))

    return df


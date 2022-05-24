import os
import traceback
import re
from functools import reduce
from hestia_earth.utils.storage._s3_client import _get_s3_client
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.table import pivot_csv


def _remove_dups(df): return df.loc[:, ~df.columns.duplicated(keep='first')]


def _filter_columns(column: str):
    return all([
        '-' not in column,
        '@id' not in column,
        'source' not in column,
        'defaultSource' not in column,
        'aggregated' not in column,
        'Version' not in column,
        'dataPrivate' not in column,
        '.name' not in column,
    ])


def _term_name(term_id: str):
    term = download_hestia(term_id)
    return f"{term.get('name')} ({term.get('units')})" if term else _capitalize(term_id)


def _column_dot(column: str):
    col_parts = column.split('.')
    return ' > '.join(map(_capitalize, col_parts))


def _capitalize(column: str):
    return _column_dot(column) if '.' in column else column[0].upper() + re.sub(r'(\w)([A-Z])', r'\1 \2', column[1:])


def _rename_columns(df):
    def _rename(col: str):
        col_parts = col.split('.')
        column = '.'.join(col_parts[1:])
        if column.endswith('.value'):
            term_id = col_parts[-2]
            column = _term_name(term_id)
        else:
            column = _capitalize(column)
        return {col: column}

    columns = list(df.columns)
    new_columns = reduce(lambda prev, curr: {**prev, **_rename(curr)}, columns, {})
    return df.rename(columns=new_columns)


def _read_csv(bucket: str, node_type: str):
    index_col = f'{node_type[0].lower() + node_type[1:]}.id'

    def read(filepath: str):
        try:
            df = pivot_csv(_get_s3_client().get_object(Bucket=bucket, Key=filepath).get('Body'))
            # use `id` field for index to merge frames
            df.set_index(index_col, inplace=True)
            df.index.name = _capitalize(index_col)
            df = _remove_dups(df)
            cols = list(filter(_filter_columns, df.columns))
            return df[cols]
        except Exception:
            stack = traceback.format_exc()
            print(stack)
            return None
    return read


def _combine_frames(csv_frames: list):
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        raise ImportError("Run `pip install pandas~=1.2.0` to use this functionality")
    df = pd.concat(csv_frames, axis=0).replace('-', np.nan).replace('', np.nan).dropna(axis=1, how='all')
    return _rename_columns(df)


def run(bucket: str, node_type: str, product_id: str):
    """
    Combine aggregated files into a single one.

    Parameters
    ----------
    bucket: str
        The bucket where the files are located.
    node_type: str
        Either 'Cycle' or 'ImpactAssessment'.
    product_id: str
        The `@id` of the product to combine the data.

    Returns
    -------
    list
        A dataframe combining all the aggregations.
    """
    prefix = '-'.join([node_type.lower(), product_id])
    files = _get_s3_client().list_objects(Bucket=bucket, Prefix=os.path.join('aggregation', prefix)).get('Contents', [])
    csv_files = [f['Key'] for f in files if f['Key'].endswith('.csv') and 'region' not in f['Key']]
    csv_frames = list(map(_read_csv(bucket, node_type), csv_files))
    csv_frames = [f for f in csv_frames if f is not None]
    return _combine_frames(csv_frames) if len(csv_frames) > 0 else None

# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import os
import typing
import numpy as np
import pandas as pd

from shapelets import Shapelets
from shapelets.model import Sequence
from shapelets.services import read_series_from_file

small_data_1 = [1.1, 2.2, 8.8, 2.2, 5.5]
small_data_2 = [2.1, 4.2, 10.8, 22.2, -5.5]
medium_data = [2.1, 4.2, 10.8, 22.2, -5.5, 2.1, 4.2, 13.8, 2.2, -0.5, 2.1, 4.2, 11.8, 22.2, -5.5]


def load_sequence_from_file(client: Shapelets, pkl_path: str, name: str) -> Sequence:
    pandas_df = pd.read_pickle(pkl_path)
    return client.create_sequence(pandas_df, name, starts=np.datetime64("2012-01-01"), every=300000)


def create_small_df(data: typing.List[float]) -> pd.DataFrame:
    freq = pd.tseries.offsets.DateOffset(microseconds=3600000000)
    return pd.DataFrame(data, index=pd.date_range("2019-01-10 20:08", periods=len(data), freq=freq))


def load_small_sequence1(client: Shapelets) -> Sequence:
    return client.create_sequence(create_small_df(small_data_1), "small_sequence1")


def load_small_sequence2(client: Shapelets) -> Sequence:
    return client.create_sequence(create_small_df(small_data_2), "small_sequence2")


def load_medium_sequence(client: Shapelets) -> Sequence:
    return client.create_sequence(create_small_df(medium_data), "medium_sequence")


_LOADED_SEQUENCES = None


def load_random_series(client: Shapelets) -> pd.DataFrame:
    global _LOADED_SEQUENCES
    if _LOADED_SEQUENCES:
        return _LOADED_SEQUENCES

    # this method will be called from integration tests within module
    # integration_tests, thus to find a file the path is relative to
    # the CWD, which is integration_tests
    csv_file = f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}resources{os.sep}test_data{os.sep}random_series.csv"
    index_col = "TIME"
    sep = ","
    collections_by_name = {col.name: col for col in client.get_collections()}
    col_name = _file_name_no_ext(csv_file)
    col_description = f"source: {col_name}.csv, index col: {index_col}, sep: {sep}"
    sequences_df, starts, every = read_series_from_file(csv_file, index_col, sep=sep)
    # delete the collection if it already exists
    existing_col = collections_by_name.get(col_name)
    if not existing_col:
        col_ref = client.create_collection(col_name, col_description)
        sequences = []
        for seq in sequences_df:
            seq_ref = client.create_sequence(seq, seq.columns[0], starts, every, col_ref)
            sequences.append(seq_ref)
    else:
        sequences = client.get_collection_sequences(existing_col)
    _LOADED_SEQUENCES = sequences
    return sequences


def _file_name_no_ext(file_name: str) -> str:
    last_sep_idx = file_name.rfind(os.sep)
    dot_idx = file_name.rfind(".")
    return file_name[last_sep_idx + 1:dot_idx]

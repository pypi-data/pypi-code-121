# Standard library imports
from datetime import datetime

# Third party imports
import pandas as pd
import pytest


@pytest.fixture
def conftest_basic_dataframe():
    data = {
        "inty_integers": [1, 2, 3] * 7,
        "floaty_floats": [1.234_523_45, 2.456_234, None] * 7,
        "stringy_strings": ["rabbit", "leopard", None] * 7,
        "datie_dates": [datetime(2020, 1, 1), datetime(2021, 2, 3), None] * 7,
        "all_nulls": [None, None, None] * 7,
        "mostly_nulls": [None, None, None] * 6 + [None, None, "Not Null"],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def ct_df_check_infer_dtypes():
    data = {
        "inty_integers": [1, 2, 3, 4, 5],
        "inty_integers_w_nulls": [1, 2, 3, None, None],
        "floaty_floats": [1.234_523_45, 2.456_234, 3.5, 4.33, 3.44],
        "stringy_strings": ["rabbit", "leopard", "a", "b", "c"],
        "stringy_strings_w_nulls": ["rabbit", "leopard", "a", None, None],
        "datie_dates": [
            datetime(2020, 1, 1),
            datetime(2021, 2, 3),
            datetime(2021, 2, 13),
            datetime(2021, 4, 13),
            datetime(2021, 3, 13),
        ],
        "datie_dates_null": [
            datetime(2020, 1, 1),
            datetime(2021, 2, 3),
            datetime(2021, 2, 13),
            None,
            None,
        ],
        "boolie_bools": [False, True, True, False, True],
        "boolie_bools_null": [False, None, True, None, None],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def conftest_check_agg_dataframe():
    data = {
        "unique_vals": [1, 2, 3],
        "unique_with_nulls": [1.234_523_45, 2.456_234, None],
        "duplicates": ["rabbit", "leopard", "rabbit"],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def conftest_check_agg_dataframe_too_big():
    data = {"unique_vals": list(range(200))}
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def ct_df_override_dtypes():
    data = {
        "stringy_dates": [
            "2021-01-01",
            "2021-02-02",
            "2021-02-03",
            "2021-02-04",
            "2021-02-05",
        ],
        "inty_integers_w_nulls": [1, 2, 3, None, None],
        "floaty_integers": [1.0, 2.0, 3.0, 4.0, 3.0],
        "string_not_dates": [
            "2021-01-01",
            "2021-02-02",
            "2021-02-03",
            "2021-02-04",
            "xyz-yan",
        ],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def ct_df_calculate_meta_dtypes():
    data = {
        "temporal_t": [
            "2021-01-01",
            "2021-02-02",
            "2021-02-03",
            "2021-02-04",
            "2021-02-05",
        ],
        "integers_b": [0, 1, 1, 0, 1],
        "integers_q": [1.0, 1, 3.0, 4.0, 3.0],
        "integers_k": [1, 2, 3, 4, 5],
        "floaties_q": [1.2, 2.3, 2.2, 4.5, 5.6],
        "nominal_lc": ["A", "B", "B", "A", "B"],
        "nominal_hc": ["A", "A", "B", "C", "D"],
        "nominal_k": ["A", "B", "C", "D", "E"],
    }
    df = pd.DataFrame(data)
    return df

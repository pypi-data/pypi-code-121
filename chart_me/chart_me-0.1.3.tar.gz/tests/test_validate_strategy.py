"""Taking inspiration from PyJanitor on testing Pandas Stuff"""
from cmath import exp
from ctypes.wintypes import FLOAT
from unittest import result
import chart_me.validate_strategy_configs as vsc
import pytest

def test_column_does_not_exist_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, 'col_no_exist')
    with pytest.raises(vsc.ColumnDoesNotExistsError):
        c_validator.validate_column()

def test_column_is_all_null_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, 'all_nulls')
    with pytest.raises(vsc.ColumnAllNullError):
        c_validator.validate_column()

def test_column_is_mostly_null_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, 'mostly_nulls')
    with pytest.raises(vsc.ColumnTooManyNullsError):
        c_validator.validate_column()

@pytest.mark.parametrize("col_names", ['inty_integers', 'floaty_floats', 'stringy_strings', 'datie_dates'])
def test_columns_are_valid(conftest_basic_dataframe, col_names):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, col_names)
    assert c_validator.validate_column()



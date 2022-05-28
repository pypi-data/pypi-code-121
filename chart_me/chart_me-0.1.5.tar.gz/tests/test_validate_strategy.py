"""Taking inspiration from PyJanitor on testing Pandas Stuff"""

# Third party imports
import pytest

# chart_me imports
import chart_me.data_validation_strategy as vsc
import chart_me.errors as e


def test_column_does_not_exist_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, "col_no_exist")
    with pytest.raises(e.ColumnDoesNotExistsError):
        c_validator.validate_column()


def test_column_is_all_null_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, "all_nulls")
    with pytest.raises(e.ColumnAllNullError):
        c_validator.validate_column()


def test_column_is_mostly_null_error(conftest_basic_dataframe):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, "mostly_nulls")
    with pytest.raises(e.ColumnTooManyNullsError):
        c_validator.validate_column()


@pytest.mark.parametrize(
    "col_names", ["inty_integers", "floaty_floats", "stringy_strings", "datie_dates"]
)
def test_columns_are_valid(conftest_basic_dataframe, col_names):
    df = conftest_basic_dataframe
    c_validator = vsc.ValidateColumnStrategyDefault(df, col_names)
    assert c_validator.validate_column()

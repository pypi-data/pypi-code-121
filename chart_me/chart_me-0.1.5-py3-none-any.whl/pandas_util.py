"""Collection of panda manipulations - leverage prior to charts

    This big idea is to keep pandas operations isolated from visuals
    keep Altair logic very simple if possible

"""
# Standard library imports
from typing import Dict, List, Union

# Third party imports
import pandas as pd


# TODO document function signature
def pd_group_me(
    df: pd.DataFrame,
    cols: Union[List[str], str],
    agg_dict: Dict,
    is_temporal: bool = False,
    make_long_form=False,
) -> pd.DataFrame:
    """A generic function to do group by aggregation in pandas

    helpful url: https://jamesrledoux.com/code/group-by-aggregate-pandas
    WARNING: Hard code logic to return var_name to "measures"

    Args:
        df: data
        cols: grouping columns
        agg_dict: aggregation dictionary: e.g. {'Age': ['mean', 'min', 'max']}
        is_temporal: boolean flag used to set 'order' by Dates versus Counts
        make_long_form: leverages reset_index and defaults

    Returns:
        pd.DataFrame: Returns tidy dataframe with default names
    """
    df = df.groupby(cols).agg(agg_dict).reset_index()
    key_cols = [f"{k}-{i}" for k in agg_dict.keys() for i in agg_dict[k]]
    sort_key = [key_cols][0]

    df.columns = ([cols] if isinstance(cols, str) else cols) + key_cols
    if is_temporal:
        df = df.sort_values([cols] if isinstance(cols, str) else cols, ascending=True)
    else:
        df = df.sort_values(sort_key, ascending=False)
    if make_long_form:
        df = pd.melt(
            df,
            id_vars=cols,
            var_name="measures",
            value_name=next(iter(agg_dict.keys())),
        )
        df["measures"] = df["measures"].str.split("-").str[-1]
    return df


def pd_truncate_date(df: pd.DataFrame, col: str) -> pd.Series:
    """Utility to make dates YY--MM--01 to Strings

    Helpful urls: https://predictivehacks.com/?all-tips=how-to-truncate-dates-to-month-in-pandas # noqa: E501
    Helpful urls: https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.to_period.html # noqa: E501

    Args:
        df: dataframe
        col: column name of date to truncate

    Returns:
        pd.Series: returns a Series of "string" datatypes
    """
    return df[col].dt.to_period("M").astype(str)

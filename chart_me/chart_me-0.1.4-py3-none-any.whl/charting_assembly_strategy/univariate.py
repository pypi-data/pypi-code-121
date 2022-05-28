"""Default implementation for single variable charting

This module contains all the logic to go from Metadata to actual charts
See supporting documentation that discusses the rules engine.

    Typical usage example:

    charts = assemble_univariate_charts(df, [col1], infered_data_types)
"""
# Standard library imports
from typing import List, Union

# Third party imports
import altair as alt
import pandas as pd

# chart_me imports
from chart_me.datatype_infer_strategy import ChartMeDataTypeMetaType, InferedDataTypes


def assemble_univariate_charts(
    df: pd.DataFrame, cols: List[str], infered_data_types: InferedDataTypes, **kwargs
) -> List[Union[alt.Chart, alt.HConcatChart]]:
    """Delegated Function to Manage Univariate Use Cases

    Args:
        df: dataframe
        cols: a single column name in a list
        infered_data_types: An instance of InferedDataTypes object

    Returns:
        List of altair charts or compounds charts

    Raises:
        ValueError if called with more then one column
    """
    if len(cols) != 1:
        raise ValueError("Only suport single column")
    col_name = cols[0]
    col_MT = infered_data_types.chart_me_data_types_meta[col_name]
    return_charts = []
    if col_MT == ChartMeDataTypeMetaType.QUANTITATIVE:
        return_charts.append(build_histogram(df, col_name))
    elif col_MT == ChartMeDataTypeMetaType.KEY:
        return_charts.append(build_hbar_agg(df.head(), col_name, "count()"))
    elif col_MT != ChartMeDataTypeMetaType.TEMPORAL:
        # chart_me imports
        from chart_me.pandas_util import pd_group_me

        agg_dict = {f"{col_name}": ["count"]}
        df = pd_group_me(df, col_name, agg_dict)
        return_charts.append(build_hbar_agg(df.head(), col_name, df.columns[-1]))
    elif col_MT == ChartMeDataTypeMetaType.TEMPORAL:
        # chart_me imports
        from chart_me.pandas_util import pd_group_me, pd_truncate_date

        temp_col_name = f"{col_name}_ym_temp"
        df[temp_col_name] = pd_truncate_date(df, col_name)
        agg_dict = {temp_col_name: ["count"]}
        df_a = pd_group_me(df, temp_col_name, agg_dict, is_temporal=True)
        print(df_a)
        print(df_a.columns)
        return_charts.append(build_vbar_agg(df_a, temp_col_name, df_a.columns[-1]))
        del df[temp_col_name]

    else:
        raise NotImplementedError(f"unknown handling of metatype-{str(col_MT)}")
    return return_charts


def build_hbar_agg(df: pd.DataFrame, col_name: str, agg_name: str) -> alt.Chart:
    """An implementation of horizontal bar chart"""
    chart = alt.Chart(df).mark_bar().encode(x=f"{agg_name}:Q", y=f"{col_name}:O")
    return chart


def build_vbar_agg(df: pd.DataFrame, col_name: str, agg_name: str) -> alt.Chart:
    """An implementation of vertical bar chart"""
    chart = alt.Chart(df).mark_bar().encode(x=f"{col_name}:O", y=f"{agg_name}:Q")
    return chart


def build_histogram(df: pd.DataFrame, col_name: str) -> alt.Chart:
    """An implementation of histogram chart"""
    chart = (
        alt.Chart(df).mark_bar().encode(alt.X(f"{col_name}:Q", bin=True), y="count()")
    )
    return chart

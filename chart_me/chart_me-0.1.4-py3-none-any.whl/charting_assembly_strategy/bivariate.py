"""Default implementation for bivariate variable charting

This module contains all the logic to go from Metadata to actual charts
See supporting documentation that discusses the rules engine.

    Typical usage example:

    charts = assemble_bivariate_charts(df, [col1, col2], infered_data_types)
"""
# Standard library imports
from typing import List, Union

# Third party imports
import altair as alt
import pandas as pd

# chart_me imports
from chart_me.datatype_infer_strategy import ChartMeDataTypeMetaType, InferedDataTypes
from chart_me.pandas_util import pd_group_me, pd_truncate_date


def assemble_bivariate_charts(
    df: pd.DataFrame, cols: List[str], infered_data_types: InferedDataTypes, **kwargs
) -> List[Union[alt.Chart, alt.HConcatChart]]:
    """Delegated Function to Manage Bivariate Use Cases

    Args:
        df: dataframe
        cols: a list of two columns
        infered_data_types: An instance of InferedDataTypes object

    Returns:
        List of altair charts or compounds charts

    Raises:
        ValueError if called with len of cols != 2
    """
    if len(cols) == 1:
        raise ValueError("This module only supports two valid columns")
    col_name1 = cols[0]
    col_name2 = cols[1]
    merged_meta_types = {
        ChartMeDataTypeMetaType.CATEGORICAL_HIGH_CARDINALITY: ChartMeDataTypeMetaType.KEY,  # noqa: E501
        ChartMeDataTypeMetaType.BOOLEAN: ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,  # noqa: E501
    }
    col_MT1 = merged_meta_types.get(
        infered_data_types.chart_me_data_types_meta[col_name1],
        infered_data_types.chart_me_data_types_meta[col_name1],
    )
    col_MT2 = merged_meta_types.get(
        infered_data_types.chart_me_data_types_meta[col_name2],
        infered_data_types.chart_me_data_types_meta[col_name2],
    )
    preagg_fl = (
        infered_data_types.preaggregated
    )  # doesn't impact behavior for univariate/bivariate
    return_charts = []

    if set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.QUANTITATIVE, ChartMeDataTypeMetaType.QUANTITATIVE]
    ):
        return_charts.append(build_scatter_plot(df, col_name1, col_name2))

    elif set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.QUANTITATIVE, ChartMeDataTypeMetaType.KEY]
    ):
        col_name_x, col_name_y = (
            [col_name2, col_name1]
            if col_MT1 == ChartMeDataTypeMetaType.KEY
            else [col_name1, col_name2]
        )
        return_charts.append(build_hbar_value(df.head(), col_name_x, col_name_y))

    elif set([col_MT1, col_MT2]) == set(
        [
            ChartMeDataTypeMetaType.QUANTITATIVE,
            ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
        ]
    ):
        col_name_n, col_name_q = (
            [col_name1, col_name2]
            if col_MT1 == ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY
            else [col_name2, col_name1]
        )
        if not preagg_fl:
            return_charts.append(build_facet_histogram(df, col_name_n, col_name_q))
        agg_dict = {f"{col_name_q}": ["count", "min", "max", "mean", "median"]}
        df = pd_group_me(df, col_name_n, agg_dict, make_long_form=True)
        # return_charts.insert(0, df)
        # TODO how to store manipulated dataframes to pass back to user
        return_charts.append(
            build_facet_hbars(
                df,
                col_name_facet="measures",
                col_name_y=col_name_n,
                col_name_x=col_name_q,
            )
        )
    elif set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.QUANTITATIVE, ChartMeDataTypeMetaType.TEMPORAL]
    ):
        col_name_t, col_name_q = (
            [col_name1, col_name2]
            if col_MT1 == ChartMeDataTypeMetaType.TEMPORAL
            else [col_name2, col_name1]
        )
        col_name_t_m_y = f"{col_name_t}_m_y"
        df[col_name_t_m_y] = pd_truncate_date(df, col_name_t)
        agg_dict = {col_name_q: ["count", "min", "max", "mean", "median"]}
        df = pd_group_me(
            df, col_name_t_m_y, agg_dict, is_temporal=True, make_long_form=True
        )
        return_charts.append(
            build_hconcat_temp_charts(df, col_name_t_m_y, col_name_q, "measures")
        )
    elif set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.KEY, ChartMeDataTypeMetaType.KEY]
    ):
        df["quantity"] = 1
        df["label"] = df[col_name1].astype(str) + "-" + df[col_name2].astype(str)
        return_charts.append(
            build_hbar_value(df.head(n=20), col_name_x="quantity", col_name_y="label")
        )
    elif set([col_MT1, col_MT2]) == set(
        [
            ChartMeDataTypeMetaType.KEY,
            ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
        ]
    ):
        col_name_n, col_name_k = (
            [col_name1, col_name2]
            if col_MT1 == ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY
            else [col_name2, col_name1]
        )
        agg_dict = {col_name_k: ["count", "nunique"]}
        df = pd_group_me(df, col_name_n, agg_dict, make_long_form=True)
        return_charts.append(
            build_facet_hbars(
                df,
                col_name_facet="measures",
                col_name_y=col_name_n,
                col_name_x=col_name_k,
            )
        )
    elif set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.KEY, ChartMeDataTypeMetaType.TEMPORAL]
    ):
        col_name_t, col_name_k = (
            [col_name1, col_name2]
            if col_MT1 == ChartMeDataTypeMetaType.TEMPORAL
            else [col_name2, col_name1]
        )
        col_name_t_m_y = f"{col_name_t}_m_y"
        df[col_name_t_m_y] = pd_truncate_date(df, col_name_t)
        agg_dict = {col_name_k: ["count", "nunique"]}
        df = pd_group_me(
            df, col_name_t_m_y, agg_dict, is_temporal=True, make_long_form=True
        )
        return_charts.append(
            build_hconcat_temp_charts(df, col_name_t_m_y, col_name_k, "measures")
        )
    elif set([col_MT1, col_MT2]) == set(
        [
            ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
            ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
        ]
    ):
        df["_counts_"] = 1
        df = pd_group_me(
            df,
            cols=[col_name1, col_name2],
            agg_dict={"_counts_": ["sum"]},
            make_long_form=True,
        )
        return_charts.append(build_heatmap(df, col_name1, col_name2, "_counts_"))
    elif set([col_MT1, col_MT2]) == set(
        [
            ChartMeDataTypeMetaType.CATEGORICAL_LOW_CARDINALITY,
            ChartMeDataTypeMetaType.TEMPORAL,
        ]
    ):
        col_name_t, col_name_n = (
            [col_name1, col_name2]
            if col_MT1 == ChartMeDataTypeMetaType.TEMPORAL
            else [col_name2, col_name1]
        )
        col_name_t_m_y = f"{col_name_t}_m_y"
        df[col_name_t_m_y] = pd_truncate_date(df, col_name_t)
        df["_counts_"] = 1
        df = pd_group_me(
            df,
            cols=[col_name_t_m_y, col_name_n],
            agg_dict={"_counts_": ["sum"]},
            make_long_form=True,
        )
        return_charts.append(
            build_hconcat_temp_lc_charts(df, col_name_t_m_y, col_name_n, "_counts_")
        )
    elif set([col_MT1, col_MT2]) == set(
        [ChartMeDataTypeMetaType.TEMPORAL, ChartMeDataTypeMetaType.TEMPORAL]
    ):
        col_name_t_m_y1, col_name_t_m_y2 = [f"{col_name1}_m_y", f"{col_name2}_m_y"]
        df[col_name_t_m_y1] = pd_truncate_date(df, col_name1)
        df[col_name_t_m_y2] = pd_truncate_date(df, col_name2)
        df["__day_diff__"] = (df[col_name1] - df[col_name2]).dt.days
        # chart_me imports
        from chart_me.charting_assembly_strategy.univariate import build_histogram

        return_charts.append(build_histogram(df, "__day_diff__"))
        df["_counts_"] = 1
        df = pd_group_me(
            df,
            cols=[col_name_t_m_y1, col_name_t_m_y2],
            agg_dict={"_counts_": ["sum"]},
            make_long_form=True,
        )
        return_charts.append(
            build_heatmap(df, col_name_t_m_y1, col_name_t_m_y2, "_counts_")
        )

    else:
        raise NotImplementedError(
            f"unknown handling of metatype-{str(col_MT1)}-{str(col_MT2)}"
        )
    return return_charts


def build_scatter_plot(df: pd.DataFrame, col_name1: str, col_name2: str) -> alt.Chart:
    """An implementation of scatter plot"""
    chart = alt.Chart(df).mark_point().encode(x=f"{col_name1}:Q", y=f"{col_name2}:Q")
    return chart


def build_hbar_value(df: pd.DataFrame, col_name_x: str, col_name_y: str) -> alt.Chart:
    """An implementation of horizontal bar chart"""
    chart = alt.Chart(df).mark_bar().encode(x=f"{col_name_x}:Q", y=f"{col_name_y}:O")
    return chart


def build_facet_histogram(
    df: pd.DataFrame, col_name_facet: str, col_name_hist_q: str
) -> alt.Chart:
    """An implementation of histogram faceted by nominal variable"""
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X(f"{col_name_hist_q}:Q", bin=True),
            y="count()",
            facet=alt.Facet(f"{col_name_facet}:O", columns=4),
        )
    )
    return chart


def build_facet_hbars(
    df: pd.DataFrame, col_name_facet: str, col_name_y: str, col_name_x: str
) -> alt.Chart:
    """An implementation of horizontal bar graph faceted by nominal variable"""
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=f"{col_name_x}:Q",
            y=f"{col_name_y}:O",
            facet=alt.Facet(f"{col_name_facet}:O", columns=2),
        )
        .resolve_scale(x="independent")
    )
    return chart


def build_hconcat_temp_charts(
    df: pd.DataFrame, col_name_y_m, col_name_q, col_name_measure: str = "measures"
) -> alt.HConcatChart:
    """An implementation of horizontal bar graph faceted by nominal variable

    WARNING: Function assumes processing through pd_group_me to separate count
    from other aggregations
    """
    df_cnt = df[df[col_name_measure] == "count"]
    df_msr = df[df[col_name_measure] != "count"]

    chart1 = (
        alt.Chart(df_cnt).mark_bar().encode(x=f"{col_name_y_m}:O", y=f"{col_name_q}:Q")
    )
    chart2 = (
        alt.Chart(df_msr)
        .mark_line()
        .encode(x=f"{col_name_y_m}:O", y=f"{col_name_q}:Q", color="measures")
    )
    return alt.hconcat(chart1, chart2)


def build_heatmap(
    df: pd.DataFrame, col_name_x: str, col_name_y: str, col_name_q: str
) -> alt.Chart:
    """An implementation of heatmap"""
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(x=f"{col_name_x}:O", y=f"{col_name_y}:O", color=f"{col_name_q}:Q")
    )
    return chart


def build_hconcat_temp_lc_charts(
    df: pd.DataFrame, col_name_t_y_m: str, col_name_n: str, col_name_q: str
) -> alt.HConcatChart:
    """An implementation that returns two charts to trend nominal and relative values

    chart 1-> bar trend chart
    chart 2-> stacked bar chart
    """
    chart1 = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=f"{col_name_t_y_m}:O", y=f"{col_name_q}:Q", color=col_name_n)
    )

    chart2 = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=f"{col_name_t_y_m}:O",
            y=alt.Y(f"{col_name_q}:Q", stack="normalize"),
            color=col_name_n,
        )
    )

    return alt.hconcat(chart1, chart2)

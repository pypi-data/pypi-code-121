import numpy as np
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from commodutil import dates
from commodutil import transforms

from commodplot import commodplottransform as cpt
from commodplot import commodplotutil as cpu
from commodplot.commodplotutil import default_line_col, year_col_map

hovertemplate_default = "%{y:.2f}: <i>%{text}</i>"


def get_year_line_col(year):
    """
    Given a year, calculate a consistent line colour across charts
    """
    delta = get_year_line_delta(year)
    return year_col_map.get(delta, default_line_col)


def get_sequence_line_col(seqno: int):
    """
    Given a sequence number select the colour from default plotly palette
    Required for line plot where history and forward should be same color
    :param seqno:
    :return:
    """
    if seqno <= len(plotly.colors.qualitative.Plotly):
        return plotly.colors.qualitative.Plotly[seqno]


def line_visible(year, visible_line_years=None):
    """
    Determine the number of year lines to be visible in seasonal plot
    :param year:
    :param years_to_include:
    :return:
    """
    delta = get_year_line_delta(year)
    if delta is None:
        return None
    if visible_line_years:
        visible_line_years = visible_line_years * -1  # number of years to go back
    else:
        visible_line_years = -5  # default to 5
    # 3 represents number of years in the future to show
    return None if visible_line_years <= delta <= 3 else "legendonly"


def get_year_line_delta(year):
    if isinstance(year, str) and year.isnumeric():
        year = int(year)

    delta = year - dates.curyear
    return delta


def get_year_line_width(year):
    delta = get_year_line_delta(year)
    if delta == 0:
        return 3

    return 2


def clean_seas_df_for_min_max_average(seas, range):
    """
    Given a seasonalised dataframe, clean to handle missing data
    :param seas:
    :return:
    """
    seas = seas.dropna(how="all", axis=1)
    seasf = seas.rename(columns=dates.find_year(seas))

    # only consider when we have full(er) data for a given range
    fulldata = pd.DataFrame(seasf.isna().sum())  # count non-na values
    if (
        not (fulldata == 0).all().iloc[0]
    ):  # line below doesn't apply when we have full data for all columns
        fulldata = fulldata[
            fulldata.apply(lambda x: np.abs(x - x.mean()) / x.std() < 1.5).all(axis=1)
        ]  # filter columns with high emtply values
    seasf = seasf[fulldata.index]  # use these column names only

    if isinstance(range, int):
        end_year = dates.curyear - 1
        start_year = end_year - (range - 1)
    else:
        start_year, end_year = range[0], range[1]

    r = seasf[[x for x in seasf.columns if x >= start_year and x <= end_year]]
    return r


def min_max_mean_range(seas, shaded_range):
    """
    Calculate min and max for seas
    If an int eg 5, then do curyear -1 and curyear -6
    If list then do the years in that list eg 2012-2019
    :param seas:
    :param shaded_range:
    :return:
    """
    r = clean_seas_df_for_min_max_average(seas, shaded_range)

    res = r.copy()
    res["min"] = res.min(1)
    res["max"] = res.max(1)
    res["mean"] = res.mean(1)
    res = res[["min", "max", "mean"]]

    if len(r.columns) >= 2:
        rangeyr = int(len(r.columns))  # end_year - start_year
    else:
        rangeyr = None
    return res, rangeyr


def shaded_range_traces(seas, shaded_range, showlegend=True):
    """
    Given a dataframe, calculate the min/max for every day of the year
    and return this as a trace for the min/max shaded area
    :param seas:
    :param shaded_range:
    :param showlegend:
    :return:
    """
    r, rangeyr = min_max_mean_range(seas, shaded_range)
    if isinstance(shaded_range, int):
        name = "%syr" % rangeyr
    else:
        name = "%s-%s" % (str(shaded_range[0])[-2:], str(shaded_range[1])[-2:])

    if rangeyr is not None:
        traces = []
        max_trace = go.Scatter(
            x=r.index,
            y=r["max"].values,
            fill=None,
            name="%s Max" % name,
            mode="lines",
            line_color="lightsteelblue",
            line_width=0.1,
            showlegend=showlegend,
            legendgroup="min",
        )
        traces.append(max_trace)
        min_trace = go.Scatter(
            x=r.index,
            y=r["min"].values,
            fill="tonexty",
            name="%s Min" % name,
            mode="lines",
            line_color="lightsteelblue",
            line_width=0.1,
            showlegend=showlegend,
            legendgroup="max",
        )
        traces.append(min_trace)
        return traces


def average_line_trace(seas, average_line):
    """
    Given a dataframe, calculate the mean for every day of the year
    and return this as a trace for the average line
    :param seas:
    :param average_line:
    :return:
    """
    r, rangeyr = min_max_mean_range(seas, average_line)
    trace = go.Scatter(
        x=r.index,
        y=r["mean"].values,
        fill=None,
        name="%syr Avg" % rangeyr,
        mode="lines",
        line_width=0.4,
        line_color="darkslategray",
        line=dict(dash="dash"),
        showlegend=True,
        legendgroup="avg",
    )
    return trace


def timeseries_to_seas_trace(
    seas, text, dash=None, showlegend=True, visible_line_years=None
):
    """
    Given a dataframe of reindexed data, generate traces for every year
    :param seas:
    :param text:
    :param dash:
    :param showlegend:
    :return:
    """
    traces = []
    for col in seas.columns:
        trace = go.Scatter(
            x=seas.index,
            y=seas[col],
            hoverinfo="y",
            name=str(col),
            hovertemplate=hovertemplate_default,
            text=text,
            visible=line_visible(col, visible_line_years),
            line=dict(
                color=get_year_line_col(col), dash=dash, width=get_year_line_width(col)
            ),
            showlegend=showlegend,
            legendgroup=str(col),
        )
        traces.append(trace)

    return traces


def timeseries_to_reindex_year_trace(
    dft, text, dash=None, current_select_year=None, showlegend=True
):
    traces = []
    colyearmap = cpu.dates.find_year(dft)

    for col in dft.columns:
        colyear = colyearmap[col]
        width = 1.2
        if current_select_year:  # for current year+ makes lines bolder
            if isinstance(current_select_year, str):
                current_select_year = colyearmap[current_select_year]
            if colyear >= current_select_year:
                width = 2.2
        trace = go.Scatter(
            x=dft.index,
            y=dft[col],
            hoverinfo="y",
            name=str(col),
            hovertemplate=hovertemplate_default,
            text=text,
            visible=line_visible(colyear),
            line=dict(color=get_year_line_col(colyear), dash=dash, width=width),
            showlegend=showlegend,
            legendgroup=str(col),
        )
        traces.append(trace)

    return traces


def seas_plot_traces(df, fwd=None, **kwargs):
    """
    Generate traces for a timeseries that is being turned into a seasonal plot.
    Gererate yearlines for both historical and forward (if provided) and the shaded range
    :param df:
    :param fwd:
    :param kwargs:
    :return:
    """
    res = {}
    histfreq = kwargs.get("histfreq", None)
    if histfreq is None:
        histfreq = cpu.infer_freq(df)
    seas = cpt.seasonalise(df, histfreq=histfreq)

    text = seas.index.strftime("%b")
    if histfreq in ["B", "D", "W"]:
        text = seas.index.strftime("%d-%b")

    showlegend = kwargs.get("showlegend", None)
    visible_line_years = kwargs.get("visible_line_years", None)

    # shaded range
    shaded_range = kwargs.get("shaded_range", None)
    if shaded_range is not None:
        res["shaded_range"] = shaded_range_traces(
            seas, shaded_range, showlegend=showlegend
        )

    # average line
    average_line = kwargs.get("average_line", None)
    if average_line is not None:
        res["average_line"] = average_line_trace(seas, average_line)

    # historical / solid lines
    res["hist"] = timeseries_to_seas_trace(
        seas, text, showlegend=showlegend, visible_line_years=visible_line_years
    )

    # fwd / dotted lines
    if fwd is not None:
        fwdfreq = pd.infer_freq(fwd.index)
        # for charts which are daily, resample the forward curve into a daily series
        if histfreq in ["B", "D"] and fwdfreq in ["MS", "ME"]:
            fwd = transforms.format_fwd(
                fwd, df.index[-1]
            )  # only applies for forward curves
        fwdseas = cpt.seasonalise(fwd, histfreq=fwdfreq)

        res["fwd"] = timeseries_to_seas_trace(
            fwdseas, text, showlegend=showlegend, dash="dot"
        )

    return res


def reindex_plot_traces(df, **kwargs):
    """
    Generate traces for a timeseries that is being turned into a reindex year plot.
    Gererate yearlines for both historical and the shaded range
    :param df:
    :param kwargs:
    :return:
    """
    res = {}
    showlegend = kwargs.get("showlegend", None)
    current_select_year = kwargs.get("current_select_year", None)

    text = df.index.strftime("%d-%b")

    shaded_range = kwargs.get("shaded_range", None)
    if shaded_range is not None:
        res["shaded_range"] = shaded_range_traces(
            df, shaded_range, showlegend=showlegend
        )

    # historical / solid lines
    res["hist"] = timeseries_to_reindex_year_trace(
        df, text, current_select_year=current_select_year, showlegend=showlegend
    )

    return res


def timeseries_trace(series: pd.Series, **kwargs) -> go.Scatter:
    """
    Return a standard timeseries trace for use in a plotly figure
    :param series: Pandas timeseries of data
    :param kwargs: kwargs for various formatting options
    :return:
    """
    series = series.dropna()

    # name
    name = series.name
    if not isinstance(name, str):
        name = str(name)

    # hover text formatting
    hover_date_format = kwargs.get("hover_date_format", "%d-%b-%y")

    t = go.Scatter(
        x=series.index,
        y=series.values,
        hoverinfo="y",
        name=name,
        hovertemplate=kwargs.get("hovertemplate", hovertemplate_default),
        text=series.index.strftime(hover_date_format),
        visible=kwargs.get("visible"),
        line=dict(
            width=kwargs.get("width"),
            color=kwargs.get("color"),
            dash=kwargs.get("dash"),
        ),
        legendgroup=str(kwargs.get("legendgroup")),
        showlegend=kwargs.get("showlegend"),
    )
    return t


def timeseries_trace_by_year(
    series: pd.Series, colyear: int, promptyear: int = None, **kwargs
) -> go.Scatter:
    """
    Return a timeseries trace with formatting applied for a given year
    Use the standardised colors for relative years. Eg current year = black
    Make current and future year lines thicker
    :param series: Pandas timeseries of data
    :param colyear: The year represented by this timeseries (if label is different)
    :param promptyear: Year to use when calculating forward years, eg if end of 2020, then make 2021 the prompt year
    :param kwargs:
    :return:
    """
    width = None
    if promptyear:  # for current year+ makes lines bolder
        if colyear >= promptyear:
            width = 2.2

    visible = line_visible(colyear, visible_line_years=kwargs.get("visible_line_years"))
    color = get_year_line_col(colyear)

    t = timeseries_trace(
        series,
        colyear=colyear,
        promptyear=promptyear,
        width=width,
        visible=visible,
        color=color,
        legendgroup=kwargs.get("legendgroup"),
        showlegend=kwargs.get("showlegend"),
    )
    return t


def line_plot_traces(df, fwd=None, **kwargs):
    """
    Generate traces for a timeseries. If historic and forward values are passed,
    then show solid lines followed by forward lines
    :param df:
    :param kwargs:
    :return:
    """
    traces = []
    colyearmap = cpu.dates.find_year(df)
    colcount = 0
    for col in df.columns:
        colyear = colyearmap[col]
        if isinstance(colyear, int) or (
            isinstance(colyear, str) and colyear.isnumeric()
        ):
            trace = timeseries_trace_by_year(
                df[col], colyear, legendgroup=col
            )  # , text, **kwargs)
        else:
            trace = timeseries_trace(
                df[col], legendgroup=col, color=get_sequence_line_col(colcount)
            )  #

        traces.append(trace)

        if fwd is not None and col in fwd.columns:
            f = fwd[col]
            fwdfreq = pd.infer_freq(f.index)
            if fwdfreq in ["MS", "ME"]:
                f = transforms.format_fwd(
                    f, df.index[-1]
                )  # only applies for forward curves
            if isinstance(colyear, int) or (
                isinstance(colyear, str) and colyear.isnumeric()
            ):
                trace = timeseries_trace_by_year(
                    f,
                    colyear,
                    legendgroup=col,
                    showlegend=False,
                )  # , text, **kwargs)
            else:
                trace = timeseries_trace(
                    f,
                    dash="dash",
                    legendgroup=col,
                    showlegend=False,
                    color=get_sequence_line_col(colcount),
                )
            traces.append(trace)

        colcount = colcount + 1

    return traces

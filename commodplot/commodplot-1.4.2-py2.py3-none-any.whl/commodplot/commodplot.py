import itertools

import cufflinks as cf
import pandas as pd
import plotly as py
import plotly.graph_objects as go
from commodutil import dates
from commodutil import transforms
from plotly.subplots import make_subplots

from commodplot import commodplottrace as cptr
from commodplot import commodplotutil as cpu

preset_margins = {"l": 0, "r": 0, "t": 40, "b": 0}


def seas_line_plot(df, fwd=None, **kwargs):
    """
    Given a DataFrame produce a seasonal line plot (x-axis - Jan-Dec, y-axis Yearly lines)
    Can overlay a forward curve on top of this
    """

    fig = go.Figure()
    traces = cptr.seas_plot_traces(df, fwd, **kwargs)
    if "shaded_range" in traces and traces["shaded_range"]:
        for trace in traces["shaded_range"]:
            fig.add_trace(trace)

    if "average_line" in traces:
        fig.add_trace(traces["average_line"])

    if "hist" in traces:
        for trace in traces["hist"]:
            fig.add_trace(trace)

    if "fwd" in traces:
        for trace in traces["fwd"]:
            fig.add_trace(trace)

    fig.layout.xaxis.tickvals = pd.date_range(
        start=str(dates.curyear), periods=12, freq="MS"
    )

    title = cpu.gen_title(df, **kwargs)
    legend = go.layout.Legend(font=dict(size=10), traceorder="reversed")
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "x")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b",
        yaxis_title=yaxis_title,
        legend=legend,
        hovermode=hovermode,
        margin=preset_margins,
    )

    return fig


def seas_line_subplot(rows, cols, df, fwd=None, **kwargs):
    """
    Generate a plot with multiple seasonal subplots.
    :param rows:
    :param cols:
    :param dfs:
    :param fwds:
    :param kwargs:
    :return:
    """
    fig = make_subplots(
        cols=cols,
        rows=rows,
        specs=[[{"type": "scatter"} for x in range(0, cols)] for y in range(0, rows)],
        subplot_titles=kwargs.get("subplot_titles", None),
    )

    chartcount = 0
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            # print(row, col)
            if chartcount > len(df):
                chartcount += 1
                continue

            dfx = df[df.columns[chartcount]]
            fwdx = None
            if fwd is not None and len(fwd) > chartcount:
                fwdx = fwd[fwd.columns[chartcount]]

            showlegend = True if chartcount == 0 else False

            traces = cptr.seas_plot_traces(
                dfx, fwd=fwdx, showlegend=showlegend, **kwargs
            )

            for trace_set in ["shaded_range", "hist", "fwd"]:
                if trace_set in traces:
                    for trace in traces[trace_set]:
                        fig.add_trace(trace, row=row, col=col)

            chartcount += 1

    legend = go.layout.Legend(font=dict(size=10))
    fig.update_xaxes(
        tickvals=pd.date_range(start=str(dates.curyear), periods=12, freq="MS"),
        tickformat="%b",
    )
    title = kwargs.get("title", "")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b",
        legend=legend,
        margin=preset_margins,
    )
    return fig


def seas_box_plot(hist, fwd=None, **kwargs):
    hist = transforms.monthly_mean(hist)
    hist = hist.T

    data = []
    monthstr = {
        x.month: x.strftime("%b")
        for x in pd.date_range(start="2018", freq="M", periods=12)
    }
    for x in hist.columns:
        trace = go.Box(name=monthstr[x], y=hist[x])
        data.append(trace)

    fwdl = transforms.seasonailse(fwd)
    fwdl.index = fwdl.index.strftime("%b")
    for col in fwdl.columns:
        ser = fwdl[col].copy()
        trace = go.Scatter(
            name=col,
            x=ser.index,
            y=ser,
            line=dict(color=cptr.get_year_line_col(col), dash="dot"),
        )
        data.append(trace)

    fig = go.Figure(data=data)
    title = kwargs.get("title", "")
    fig.update_layout(title=title, title_x=0.01, margin=preset_margins)

    return fig


def seas_table_plot(hist, fwd=None):
    df = cpu.seas_table(hist, fwd)

    colsh = list(df.columns)
    colsh.insert(0, "Period")

    cols = [df[x] for x in df]
    cols.insert(0, list(df.index))
    fillcolor = ["lavender"] * 12
    fillcolor.extend(["aquamarine"] * 4)
    fillcolor.extend(["darkturquoise"] * 2)
    fillcolor.append("dodgerblue")

    figm = go.Figure(
        data=[
            go.Table(
                header=dict(values=colsh, fill_color="paleturquoise", align="left"),
                cells=dict(values=cols, fill_color=[fillcolor], align="left"),
            )
        ]
    )
    return figm


def table_plot(df, **kwargs):
    row_even_colour = kwargs.get("row_even_colour", "lightgrey")
    row_odd_color = kwargs.get("row_odd_colour", "white")

    # include index col as part of plot
    indexname = "" if df.index.name is None else df.index.name
    colheaders = [indexname] + list(df.columns)
    headerfill = ["white" if x == "" else "grey" for x in colheaders]

    cols = [df[x] for x in df.columns]
    # apply red/green to formatted_cols
    fcols = kwargs.get("formatted_cols", [])
    font_color = [
        ["red" if str(y).startswith("-") else "green" for y in df[x]]
        if x in fcols
        else "black"
        for x in colheaders
    ]

    if isinstance(df.index, pd.DatetimeIndex):  # if index is datetime, format dates
        df.index = df.index.map(lambda x: x.strftime("%d-%m-%Y"), 1)
    cols.insert(0, df.index)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=colheaders,
                    fill_color=headerfill,
                    align="center",
                    font=dict(color="white", size=12),
                ),
                cells=dict(
                    values=cols,
                    line=dict(color="#506784"),
                    fill_color=[[row_odd_color, row_even_colour] * len(df)],
                    align="right",
                    font_color=font_color,
                ),
            )
        ]
    )
    return fig


def forward_history_plot(df, title=None, **kwargs):
    """
    Given a dataframe of a curve's pricing history, plot a line chart showing how it has evolved over time
    """
    df = df.rename(columns={x: pd.to_datetime(x) for x in df.columns})
    df = df[sorted(list(df.columns), reverse=True)]  # have latest column first
    df = df.rename(
        columns={x: cpu.format_date_col(x, "%d-%b-%y") for x in df.columns}
    )  # make nice labels for legend eg 05-Dec

    colseq = py.colors.sequential.Aggrnyl
    text = df.index.strftime("%b-%y")

    fig = go.Figure()
    colcount = 0
    for col in df.columns:
        color = colseq[colcount] if colcount < len(colseq) else colseq[-1]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[col],
                hoverinfo="y",
                name=str(col),
                line=dict(color=color),
                hovertemplate=cptr.hovertemplate_default,
                text=text,
            )
        )

        colcount = colcount + 1

    fig["data"][0]["line"]["width"] = 2.2  # make latest line thicker
    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        margin=preset_margins,
    )
    return fig


def bar_line_plot(df, linecol="Total", **kwargs):
    """
    Give a dataframe, make a stacked bar chart along with overlaying line chart.
    """
    if linecol not in df:
        df[linecol] = df.sum(1, skipna=False)

    barcols = [x for x in df.columns if linecol not in x]
    barspecs = {"kind": "bar", "barmode": "relative", "title": "d", "columns": barcols}
    linespecs = {"kind": "scatter", "columns": linecol, "color": "black"}

    fig = cf.tools.figures(df, [barspecs, linespecs])  # returns dict
    fig = go.Figure(fig)
    yaxis_title = kwargs.get("yaxis_title", None)
    yaxis_range = kwargs.get("yaxis_range", None)
    title = kwargs.get("title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        margin=preset_margins,
    )
    if yaxis_range is not None:
        fig.update_layout(yaxis=dict(range=yaxis_range))
    return fig


def diff_plot(df, **kwargs):
    """
    Given a dataframe, plot each column as line plot with a subplot below
    showing differences between each column.
    :param df:
    :param kwargs:
    :return:
    """
    # calculate difference between each column
    for comb in itertools.combinations(df.columns, 2):
        df["%s-%s" % (comb[0], comb[1])] = df[comb[0]] - df[comb[1]]

    barcols = [x for x in df.columns if "-" in x]
    linecols = [x for x in df.columns if "-" not in x]

    fig = make_subplots(
        rows=2, cols=1, row_heights=[0.8, 0.2], shared_xaxes=True, vertical_spacing=0.02
    )
    for col in linecols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col))

    for col in barcols:
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col), row=2, col=1)

    title = kwargs.get("title", "")
    fig.update_layout(title_text=title, title_x=0.01, margin=preset_margins)
    return fig


def reindex_year_line_plot(df, **kwargs):
    """
    Given a dataframe of timeseries, reindex years and produce line plot
    :param df:
    :return:
    """
    fig = go.Figure()
    dft = transforms.reindex_year(df)
    colsel = cpu.reindex_year_df_rel_col(dft)

    traces = cptr.reindex_plot_traces(dft, current_select_year=colsel, **kwargs)

    if "shaded_range" in traces and traces["shaded_range"]:
        for trace in traces["shaded_range"]:
            fig.add_trace(trace)

    if "hist" in traces:
        for trace in traces["hist"]:
            fig.add_trace(trace)

    kwargs["title_postfix"] = colsel
    title = cpu.gen_title(df[colsel], title_prefix=colsel, **kwargs)

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        margin=preset_margins,
    )
    # zoom into last 3 years
    fig.update_xaxes(
        type="date",
        range=[
            dft.tail(365 * 3).index[0].strftime("%Y-%m-%d"),
            dft.index[-1].strftime("%Y-%m-%d"),
        ],
    )

    return fig


def candle_chart(df, **kwargs):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )

    title = cpu.gen_title(df["Close"], **kwargs)
    fig.update_layout(title=title)
    return fig


def stacked_area_chart(df, **kwargs):
    fig = go.Figure()
    group = kwargs.get("stackgroup", "stackgroup")

    for col in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, stackgroup=group))

    fig.update_layout(title=kwargs.get("title", ""))
    return fig


def bar_chart(df, **kwargs):
    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col))

    hovermode = kwargs.get("hovermode", "x")
    fig.update_layout(title=kwargs.get("title", ""), hovermode=hovermode)
    barmode = kwargs.get("barmode", None)
    if barmode:
        fig.update_layout(barmode=barmode)

    return fig


def reindex_year_line_subplot(rows, cols, dfs, **kwargs):
    fig = make_subplots(
        cols=cols,
        rows=rows,
        specs=[[{"type": "scatter"} for x in range(0, cols)] for y in range(0, rows)],
        subplot_titles=kwargs.get("subplot_titles", None),
        shared_xaxes=False,
    )

    chartcount = 0
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            # print(row, col)
            if chartcount > len(dfs):
                chartcount += 1
                continue
            showlegend = True if chartcount == 0 else False

            dfx = dfs[chartcount]
            dft = transforms.reindex_year(dfx)
            colsel = cpu.reindex_year_df_rel_col(dft)
            traces = cptr.reindex_plot_traces(
                dft, current_select_year=colsel, showlegend=showlegend, **kwargs
            )
            for trace_set in ["shaded_range", "hist"]:
                if trace_set in traces:
                    for trace in traces[trace_set]:
                        fig.add_trace(trace, row=row, col=col)

            chartcount += 1

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "closest")
    title = kwargs.get("title", "")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        hovermode=hovermode,
        margin=preset_margins,
    )

    fig.update_xaxes(type="date")

    return fig


def line_plot(df, fwd=None, **kwargs):
    fig = go.Figure()
    res = cptr.line_plot_traces(df, fwd, **kwargs)
    for trace in res:
        fig.add_trace(trace)

    title = cpu.gen_title(df, inc_change_sum=False, **kwargs)
    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "closest")
    fig.update_layout(
        title=title,
        title_x=0.01,
        yaxis_title=yaxis_title,
        legend=legend,
        hovermode=hovermode,
    )
    return fig

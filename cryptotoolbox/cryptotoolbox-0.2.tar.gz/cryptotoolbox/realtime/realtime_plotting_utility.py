from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.graph_objects as go

import plotly.express as px
from itertools import cycle
palette = cycle(px.colors.qualitative.Plotly)

import numpy as np
import plotly.express as px

def create_ohlc_figure(data_df, underlying):
    fig = go.Figure(data=go.Ohlc(x=data_df.index,
                                 open=data_df['open'],
                                 high=data_df['high'],
                                 low=data_df['low'],
                                 close=data_df['close']))
    fig.update_layout(height=600, width=1600, title_text=f'Live minute {underlying}')
    return fig




def create_quote_signal_figure(data_df, signals_df, strategy_name):
    fig = make_subplots(rows=2, cols=1, row_heights=[0.9, 0.1])
    fig.add_trace(
        go.Scatter(x=data_df.index, y=data_df['close'], name=f'quotes {strategy_name}'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data_df.index, y=signals_df['value'], name=f'signals {strategy_name}'),
        row=2, col=1
    )
    fig.update_layout(height=600, width=1600, title_text=f'Live strategy {strategy_name}')
    return fig


def plot_multiple_time_series(data_df, error_message='no data available'):
    if data_df is None:
        fig = make_subplots(rows=1, cols=1)
        fig.update_layout(height=600, width=1000, title_text=error_message)
        return fig

    fig = make_subplots(rows=1, cols=1)
    constituents = [col for col in data_df.columns if col not in ['date','Date']]
    for me_constituent in constituents:
        trace_sig = go.Scatter(
            x=data_df.index,
            y=data_df[me_constituent],
            name=me_constituent,
            opacity=0.8)
        fig.append_trace(trace_sig, row=1, col=1)

    fig.update_layout(height=600, width=1600, title_text="Strategy performances",showlegend=True)
    fig.update_layout(height=600, width=1600, showlegend=True, legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def plot_stacked_bar(data_df, title = ''):

    ts_data=[]
    for col in data_df.columns:
        me_x=list(range(len(data_df.index)))
        me_x=data_df.index
        me_y=data_df[col].values
        #print(me_x)
        #print(me_y)
        ts_data.append(go.Bar(name=col, x=me_x, y=me_y))

    fig = go.Figure(data=ts_data)
    fig.update_layout(barmode='stack', title=title)
    return fig



def plot_regime_close(data_df):
    assert 'regime' in data_df.columns
    assert 'close' in data_df.columns


    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=data_df.index, y=data_df['close'], name='close'),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=data_df.index, y=data_df['regime'], name='regime'),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Double Y Axis Example"
    )

    # Set x-axis title
    fig.update_xaxes(rangeslider_visible=True)
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
    return fig


def plot_sig_vs_ret(data_df, return_col = 'close', sig_col = None):
    fig = go.Figure(data=go.Scatter(x=data_df[sig_col], y=data_df[return_col], mode='markers'))
    return fig


def plot_scatter_indicator_vs_ret(data_df, return_col = 'close', sig_col = None, color_red_return = True):
    if color_red_return:
        data_df['color']='red'
        data_df['to_filter'] = data_df[return_col] >= 0.
        data_df['color'][ data_df['to_filter']] = 'green'
        # fig = px.scatter(data_df, x=sig_col, y=return_col,color='color')


        fig = go.Figure(data=go.Scatter(
            x=data_df[sig_col],
            y=data_df[return_col],
            mode='markers',
            marker=dict(color=list(data_df['color']))
        ))

        return fig
    fig = go.Figure(data=go.Scatter(x=data_df[sig_col], y=data_df[return_col], mode='markers'))
    return fig

def plot_box_plot_sig_vs_ret(data_df, return_col = 'close', sig_col = None):
    fig = px.box(data_df, x=sig_col, y=return_col, points="all")
    return fig

def plot_month_hit_ratio(month_dictionary, height=600 , width=1600, put_on_same_scale = True,title = 'Hit ratio',  split = True):
    if split :
        for month_name, data_df in month_dictionary.items():
            fig = px.bar(data_df, x="strategy_underlying", y='value', color="type", barmode='group',
                         title=f'hitration {month_name}')
            fig.update_layout(barmode='group')
            fig.show()
    else:

        dict_length = len(month_dictionary)
        fig = make_subplots(rows=len(month_dictionary), cols=1)
        counter = 0
        for month_name, data_df in month_dictionary.items():
            counter = counter + 1
            print(f'displaying {month_name}')
            data = []
            for me_type in data_df['type'].unique():
                merged_type_df = data_df[data_df['type'] == me_type].copy()
                trace1 = go.Bar(
                    x=merged_type_df['strategy_underlying'],
                    y=merged_type_df['value'],
                    name=me_type
                )
                fig.append_trace(trace1,  counter, 1)

    #            data.append(trace1)

    #        fig.append_trace(data, counter, 1)



        fig.update_layout(barmode='group')
        fig.update_layout(height=height*dict_length, width=width, title_text=title,showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)
        return fig
    #if put_on_same_scale:
    #    fig.update_yaxes(range=[data_df[constituents].min().min(), data_df[constituents].max().max()])

def plot_multiple_time_series_scatter(data_df, split =False, logy = True, title = 'Strategy performances', height=600 ,width=1600, put_on_same_scale = True, drop_na_inf = True):
    palette = cycle(px.colors.qualitative.Bold)
#    palette = cycle(px.colors.qualitative.Vivid)
#    palette = cycle(px.colors.qualitative.Safe)
#    data_df[~data_df.isin([np.nan, np.inf, -np.inf]).any(1)] = 0.
    if drop_na_inf and not data_df.isin([np.nan, np.inf, -np.inf]).astype(int).sum(axis=0).sum(axis=0) == 0:
        data_df.iloc[data_df.isin([np.nan, np.inf, -np.inf]).values] = 0.
    if split:
        fig = make_subplots(rows=1, cols=len(data_df.columns))
        constituents = [col for col in data_df.columns if col not in ['date','Date']]
        counter = 1
        for me_constituent in constituents:
            trace_sig = go.Scatter(
                x=data_df.index,
                y=data_df[me_constituent],
                name=me_constituent,
                opacity=0.8,
                text=me_constituent,
                hoverinfo='text',
                mode='markers',
                marker_color=next(palette)
            )
            fig.append_trace(trace_sig, row=1, col=counter)
            if logy:
                fig.update_yaxes(title_text="y-axis in logarithmic scale", type="log", row=1, col=counter)
            counter = counter+1

        fig.update_layout(height=height, width=width, title_text=title,showlegend=True)
        fig.update_layout(height=height, width=width, showlegend=True, legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        fig.update_xaxes(rangeslider_visible=True)
        if put_on_same_scale:
            fig.update_yaxes(range=[data_df[constituents].min().min(), data_df[constituents].max().max()])


        return fig
    else:
        fig = make_subplots(rows=1, cols=1)
        constituents = [col for col in data_df.columns if col not in ['date','Date']]
        for me_constituent in constituents:
            trace_sig = go.Scatter(
                x=data_df.index,
                y=data_df[me_constituent],
                name=me_constituent,
                opacity=0.8,
                text=me_constituent,
                hoverinfo='text',
                mode='markers',
                marker_color=next(palette)
            )
            fig.append_trace(trace_sig, row=1, col=1)

        if logy:
            fig.update_yaxes(title_text="y-axis in logarithmic scale", type="log", row=1, col=1)
        fig.update_layout(height=height, width=width, title_text=title,showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(height=height, width=width, showlegend=True, legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        if put_on_same_scale:
            fig.update_yaxes(range=[data_df[constituents].min().min(), data_df[constituents].max().max()])

        return fig

def plot_multiple_time_series(data_df, split =False, logy = True, title = 'Strategy performances', height=600 ,width=1600, put_on_same_scale = True, drop_na_inf = True):
    palette = cycle(px.colors.qualitative.Bold)
#    palette = cycle(px.colors.qualitative.Vivid)
#    palette = cycle(px.colors.qualitative.Safe)
#    data_df[~data_df.isin([np.nan, np.inf, -np.inf]).any(1)] = 0.
    if drop_na_inf and not data_df.isin([np.nan, np.inf, -np.inf]).astype(int).sum(axis=0).sum(axis=0) == 0:
        data_df.iloc[data_df.isin([np.nan, np.inf, -np.inf]).values] = 0.
    if split:
        fig = make_subplots(rows=1, cols=len(data_df.columns))
        constituents = [col for col in data_df.columns if col not in ['date','Date']]
        counter = 1
        for me_constituent in constituents:
            trace_sig = go.Scatter(
                x=data_df.index,
                y=data_df[me_constituent],
                name=me_constituent,
                opacity=0.8,
                text=me_constituent,
                hoverinfo='text',
                marker_color=next(palette)
            )
            fig.append_trace(trace_sig, row=1, col=counter)
            if logy:
                fig.update_yaxes(title_text="y-axis in logarithmic scale", type="log", row=1, col=counter)
            counter = counter+1

        fig.update_layout(height=height, width=width, title_text=title,showlegend=True)
        fig.update_layout(height=height, width=width, showlegend=True, legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        fig.update_xaxes(rangeslider_visible=True)
        if put_on_same_scale:
            fig.update_yaxes(range=[data_df[constituents].min().min(), data_df[constituents].max().max()])


        return fig
    else:
        fig = make_subplots(rows=1, cols=1)
        constituents = [col for col in data_df.columns if col not in ['date','Date']]
        for me_constituent in constituents:
            trace_sig = go.Scatter(
                x=data_df.index,
                y=data_df[me_constituent],
                name=me_constituent,
                opacity=0.8,
                text=me_constituent,
                hoverinfo='text',
                marker_color=next(palette)
            )
            fig.append_trace(trace_sig, row=1, col=1)

        if logy:
            fig.update_yaxes(title_text="y-axis in logarithmic scale", type="log", row=1, col=1)
        fig.update_layout(height=height, width=width, title_text=title,showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(height=height, width=width, showlegend=True, legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        if put_on_same_scale:
            fig.update_yaxes(range=[data_df[constituents].min().min(), data_df[constituents].max().max()])

        return fig

def plot_multiple_turnover(data_df, ma = None):
    fig = make_subplots(rows=1, cols=1)
    constituents = [col for col in data_df.columns if col not in ['date','Date']]
    for me_constituent in constituents:
        if ma is not None:
            data_df[me_constituent] = data_df[me_constituent].rolling(ma).mean()

        trace_sig = go.Scatter(
            x=data_df.index,
            y=data_df[me_constituent],
            name=me_constituent,
            opacity=0.8)
        fig.append_trace(trace_sig, row=1, col=1)

    fig.update_layout(height=600, width=1600, title_text="Strategy performances",showlegend=True)
    fig.update_layout(height=600, width=1600, showlegend=True, legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def plot_drawdown(data_df, column_name):
    fig = make_subplots(rows=1, cols=1)
    trace_sig = go.Scatter(
        x=data_df.index,
        y=data_df[column_name],
        name="drawdown",
        opacity=0.8)
    fig.append_trace(trace_sig, row=1, col=1)
    fig.update_layout(height=600, width=1600, title_text="Drawdown chart",showlegend=True)
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def plot_heatmap(data_df,title= 'heatmap'):

    fig = go.Figure(data=go.Heatmap(
        z=data_df.values,
        x=data_df.index,
        y=data_df.columns))
    fig.update_layout(
        title=title)
    return fig


def plot_correlation(data_df):
    static_correlation_df = data_df.corr()

    fig = go.Figure(data=go.Heatmap(
        z=static_correlation_df.values,
        x=static_correlation_df.index,
        y=static_correlation_df.columns,
        colorscale='Viridis'))

    fig.update_layout(
        title='Signal correlation matrix',
        xaxis_nticks=36)
    return fig



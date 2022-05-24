from plotly.subplots import make_subplots

import plotly.graph_objs as go




def generate_simple_timeseries_plot(data = None, title = ''):

    if data is None:
        fig = make_subplots(rows=1, cols=1)
        fig.update_layout(height=600, width=1600, title_text="no data provided")
        return fig
    else:
        fig = make_subplots(rows=1, cols=1)
        for me_constituent in data.columns:
            trace_sig = go.Scatter(
                x=data.index,
                y=data[me_constituent],
                name=me_constituent,
                opacity=0.8)
            fig.append_trace(trace_sig, row=1, col=1)
        fig.update_layout(height=600, width=1600, title_text=title, showlegend=True)
        fig.update_xaxes(rangeslider_visible=True)
    return fig

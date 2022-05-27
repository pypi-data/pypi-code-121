# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class plot():
    def __init__(self, fig_width, fig_height):
        self.fig_width = fig_width
        self.fig_height = fig_height

    def plot_render(self, data, layout, **kwargs):
        kwargs['output_type'] = 'div'
        plot_str = plotly.offline.plot({"data": data, "layout": layout}, **kwargs)
        print(
            '%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (self.fig_height, self.fig_width, plot_str))

    def plot_table(self, df, title_text=''):
        fig = ff.create_table(df)
        fig.layout.title = title_text
        self.plot_render(fig.data, fig.layout)

    def plot_line(self, df, title_text=''):
        data = []
        for name in list(df.columns):
            trace = go.Scatter(
                x=list(df.index),
                y=df[name].values,
                name=name,
                mode="lines+markers")
            data.append(trace)
        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=self.fig_width, height=self.fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            yaxis2={'anchor': 'x', "overlaying": 'y', "side": 'right'},
            template='plotly_white')
        self.plot_render(data, layout)

    def plot_bar(self, df, title_text='', legend_x=0.30):
        data = []
        for name in list(df.columns):
            trace = go.Bar(
                x=list(df.index),
                y=df[name].values,
                name=name)
            data.append(trace)
        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=self.fig_width, height=self.fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white')
        self.plot_render(data, layout)

    def plot_area(self, df, title_text=''):
        data = []
        for name in list(df.columns):
            tmp = go.Scatter(
                x=list(df.index),
                y=df[name].values,
                name=name,
                mode='lines',
                line=dict(width=0.5),
                fill='tonexty',
                stackgroup='one')
            data.append(tmp)
        layout = go.Layout(
            title=title_text,
            autosize=False, width=self.fig_width, height=self.fig_height,
            showlegend=True,
            xaxis=dict(type='category'),
            yaxis=dict(type='linear', range=[1, 100], dtick=20, ticksuffix='%'))
        self.plot_render(data, layout)
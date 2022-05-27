import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


# We can then compare the Sales distribution with media spent distribution to find correlations
# Define an array with all the media spent names
# media_spent = ['g_discovery_cost', 'g_display_cost', 'g_video_cost', 'g_search_brand_cost',
# 'g_search_no_brand_cost', 'b_audience_cost', 'b_search_cost', 'pinterest_cost', 'fb_cost']
def show_target_vs_media_spent_graph(df, name_data_column, name_target_column, medias_spent, title_y2='Medias Spent'):
    subfig = make_subplots(specs=[[{"secondary_y": True}]])

    fig = px.line(df, x=name_data_column, y=name_target_column)

    fig2 = px.line(df, x=name_data_column, y=medias_spent)
    fig2.update_traces(yaxis="y2")

    subfig.add_traces(fig.data + fig2.data)
    subfig.layout.xaxis.title = name_data_column
    subfig.layout.yaxis.title = name_target_column
    subfig.layout.yaxis2.title = title_y2
    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()


# We may want to compare Predicted vs. Actual sales
def show_prediction_vs_actual_graph(df, name_data_column, name_target_column, name_prediction_column):
    fig = px.line(df, x=name_data_column, y=[name_target_column, name_prediction_column])
    fig.show()


# We may want to compare Predicted vs. Actual sales with error
def show_prediction_vs_actual_graph_with_error(df, target_column, prediction_column, name_data_column,
                                               name_target_column, name_model=''):
    y_error = (prediction_column - target_column) / target_column * 100

    title_accuracy_graph = name_model + ' Model: Actual vs Predicted'

    accuracy_chart = go.Figure(
        layout=dict(height=700, width=1000, xaxis_title=name_data_column, yaxis_title=name_target_column,
                    title=title_accuracy_graph, legend_title='Legend'))
    accuracy_chart.add_trace(go.Scatter(name="Actual", x=df[name_data_column], y=target_column))
    accuracy_chart.add_trace(go.Scatter(name="Predicted", x=df[name_data_column], y=prediction_column))
    accuracy_chart.show()

    title_error_graph = name_model + ' Model Error of Actual vs Predicted'

    error_chart = go.Figure(
        layout=dict(xaxis_title=name_data_column, yaxis_title=name_target_column + ' error', title=title_error_graph,
                    legend_title='Legend'))
    error_chart.add_trace(go.Scatter(name="Error", x=df[name_data_column], y=y_error))
    error_chart.show()


def show_metric_trend(metric_array, name_metric=None):
    if name_metric is None:
        name_metric = ['nrmse_test']

    if len(name_metric) == 1:
        df = pd.DataFrame(data=metric_array,
                          columns=name_metric)
        fig = go.Figure(
            layout=dict(xaxis_title='Iterations', yaxis_title=name_metric[0], title=name_metric[0] + ' Trend',
                        legend_title='Legend'))
        fig.add_trace(go.Scatter(y=df[name_metric[0]]))
        fig.show()
    elif len(name_metric) == 2:
        df = pd.DataFrame(data=metric_array,
                          columns=name_metric)
        fig = px.scatter_3d(df, x=df.index, y=name_metric[0], z=name_metric[1], color=df.index)
        fig.show()

from plotly.graph_objects import Figure

from polisher.configs import GREY


def remove_grids(
    figure: Figure,
    keep_y_axis_grid: bool = False,
    keep_x_axis_grid: bool = False
) -> Figure:
    """
    Removes grids from layout. Grids are not necessary most of the time; it
    is good practice to only use them when necessary.
    :param figure: The figure to remove the grids.
    :param keep_y_axis_grid: To keep y axis grid lines or not.
    :param keep_x_axis_grid: To keep x axis grid lines or not.
    """
    return figure.update_layout(
        xaxis_showgrid=keep_x_axis_grid, yaxis_showgrid=keep_y_axis_grid
    )


def remove_background(
    figure: Figure, color: str = 'rgba(0,0,0,0)'
) -> Figure:
    """
    Removes background from layout by setting them to white.
    :param figure: The figure to remove the background.
    :param color: The rgba color
    """
    return figure.update_layout({
        'plot_bgcolor': color
    })


def send_to_background(
    figure: Figure, color: str = GREY, keep_trace_colors: bool = False
) -> Figure:
    """
    De-prioritize graphic importance by neutralizing the color of everything.
    Setting it to grey, will allow us later to only add color to what really
    matters in the plot.

    What will be set to grey? The axis titles, the trace colors, the title, and
    the xaxis and yaxis labels.

    :param figure: The figure to set everything to grey
    :param color: The color to set the everything to.
    :param keep_trace_colors: If true, function will skip setting trace colors.
    """
    figure.update_layout({'title_font_color': color})
    figure.update_xaxes({
        'title_font_color': color,
        'color': color,
    })
    figure.update_yaxes({
        'title_font_color': color,
        'color': color,
    })
    figure.update_annotations({
        'font_color': color,
    })
    # can be multiple colors for the whole series.
    if not keep_trace_colors:
        figure.update_traces({'marker_color': color})
    return figure

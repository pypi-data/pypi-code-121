from typing import Any, Dict, List
import plotly.io as pio
import plotly.graph_objects as go
from . import default
from ._layout import merge_layout


def _set_default_template() -> None:
    """Set the combination of the user-defined theme and layout as the default
    template.
    """
    pio.templates["plotly_light"] = pio.templates.merge_templates(
        pio.templates[default.theme],
        go.layout.Template(layout=default.layout))
    pio.templates.default = default.theme = "plotly_light"


def set_default_theme(theme_name: str,
                      keep_layout: bool = True) -> None:
    """Change plotly's default theme.

    positional_arguments:
      @ theme_name : A plotly theme name. Must be one of:
                      {"plotly_light",   (default)
                       "ggplot2",
                       "seaborn",
                       "simple_white",
                       "plotly",
                       "plotly_white",
                       "plotly_dark",
                       "none"}

    optional arguments:
      @ keep_layout : If True, overwrite the theme's layout with the 
                             default layout set by `set_default_layout()`.
    """
    pio.templates.default = default.theme = theme_name
    if keep_layout and default.layout is not None:
        _set_default_template()


def set_default_layout(layout: go.Layout) -> None:
    """Change the default layout for plots.

    positional arguments:
      @ layout : The layout object.
    """
    default.layout = layout
    _set_default_template()


def update_default_layout(layout: go.Layout) -> None:
    """Update the default layout for plots.

    positional arguments:
      @ layout    : The layout object.
    """
    set_default_layout(merge_layout(default.layout, layout))


def set_default_config(config: Dict[Any, Any]) -> None:
    """Change the default config for `go.Figure.show()`.
    List of the available configs is:
      https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js

    positional_arguments:
      @ config : Config keys and values.
    """
    pio.renderers[pio.renderers.default.split('+')[0]].config = default.config = config


def update_default_config(config: Dict[Any, Any]) -> None:
    """Change the default config for `go.Figure.show()`.
    List of the available configs is:
      https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js

    positional_arguments:
      @ config : Config keys and values.
    """
    pio.renderers[pio.renderers.default.split('+')[0]].config.update(config)
    default.config = pio.renderers[pio.renderers.default.split('+')[0]].config


def set_default_renderer(renderer_name: str) -> None:
    """Change plotly's default renderer.

    positional_arguments:
      @ renderer_name : A plotly theme name like:
                         {"plotly_mimetype",
                          "browser",
                          "notebook[_connected]",
                          "iframe[_connected]"}
    """
    config = pio.renderers[pio.renderers.default.split('+')[0]].config
    pio.renderers.default = default.renderer = renderer_name
    set_default_config(config)
    pio.renderers._activate_pending_renderers()


def set_default_colors(cols: List[str]) -> None:
    default.layout["colorway"] = cols
    _set_default_template()

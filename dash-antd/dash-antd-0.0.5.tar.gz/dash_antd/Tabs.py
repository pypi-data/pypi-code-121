# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tabs(Component):
    """A Tabs component.
Tabs

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- add_icon (string; optional):
    Customize add icon.

- animated (boolean; optional):
    Whether to change tabs with animation. Only works while
    tabPosition=\"top\".

- centered (boolean; optional):
    Centers tabs.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- destroy_inactive_tab_pane (boolean; optional):
    Whether destroy inactive TabPane when tab is changed.

- hide_add (boolean; optional):
    Hide plus icon or not. Only works while type=\"editable-card\".

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- more_icon (string; optional):
    The custom icon of ellipsis.

- size (a value equal to: 'large', 'middle', 'small'; optional):
    Preset tab bar size.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- tab_bar_gutter (number; optional):
    The gap between tabs.

- tab_bar_style (dict; optional):
    Tab bar style object.

- tab_position (a value equal to: 'top', 'right', 'bottom', 'left'; optional):
    Position of tabs.

- type (a value equal to: 'line', 'card', 'editable-card'; optional):
    Basic style of tabs.

- value (string; optional):
    Current TabPane's key."""
    @_explicitize_args
    def __init__(self, children=None, value=Component.UNDEFINED, add_icon=Component.UNDEFINED, animated=Component.UNDEFINED, centered=Component.UNDEFINED, hide_add=Component.UNDEFINED, more_icon=Component.UNDEFINED, size=Component.UNDEFINED, tab_bar_gutter=Component.UNDEFINED, tab_bar_style=Component.UNDEFINED, tab_position=Component.UNDEFINED, destroy_inactive_tab_pane=Component.UNDEFINED, type=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'add_icon', 'animated', 'centered', 'class_name', 'destroy_inactive_tab_pane', 'hide_add', 'key', 'more_icon', 'size', 'style', 'tab_bar_gutter', 'tab_bar_style', 'tab_position', 'type', 'value']
        self._type = 'Tabs'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'add_icon', 'animated', 'centered', 'class_name', 'destroy_inactive_tab_pane', 'hide_add', 'key', 'more_icon', 'size', 'style', 'tab_bar_gutter', 'tab_bar_style', 'tab_position', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Tabs, self).__init__(children=children, **args)

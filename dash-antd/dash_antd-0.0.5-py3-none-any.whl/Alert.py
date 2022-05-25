# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Alert(Component):
    """An Alert component.
Alert component for feedback.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- banner (boolean; optional):
    Whether to show as banner.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- closable (boolean; optional):
    Whether Alert can be closed.

- close_icon (string; optional):
    Custom close icon.

- close_text (string; optional):
    Close text to show.

- description (string; optional):
    Additional content of Alert.

- icon (string; optional):
    Custom icon, effective when showIcon is True.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- message (string; optional):
    Content of Alert.

- show_icon (boolean; optional):
    Whether to show icon.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- type (a value equal to: 'success', 'info', 'warning', 'error'; optional):
    Type of Alert."""
    @_explicitize_args
    def __init__(self, children=None, banner=Component.UNDEFINED, closable=Component.UNDEFINED, close_text=Component.UNDEFINED, close_icon=Component.UNDEFINED, description=Component.UNDEFINED, icon=Component.UNDEFINED, message=Component.UNDEFINED, show_icon=Component.UNDEFINED, type=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'banner', 'class_name', 'closable', 'close_icon', 'close_text', 'description', 'icon', 'key', 'message', 'show_icon', 'style', 'type']
        self._type = 'Alert'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'banner', 'class_name', 'closable', 'close_icon', 'close_text', 'description', 'icon', 'key', 'message', 'show_icon', 'style', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Alert, self).__init__(children=children, **args)

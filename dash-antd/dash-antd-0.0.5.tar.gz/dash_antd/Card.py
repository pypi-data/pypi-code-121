# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Card(Component):
    """A Card component.
Simple rectangular container.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- active_tab_key (string; optional):
    Current TabPane's key.

- body_style (dict; optional):
    Inline style to apply to the card content.

- bordered (boolean; optional):
    Toggles rendering of the border around the card.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- head_style (dict; optional):
    Inline style to apply to the card head.

- hoverable (boolean; optional):
    Lift up when hovering card.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- loading (boolean; optional):
    Shows a loading indicator while the contents of the card are being
    fetched.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; required):
        Holds the name of the component that is loading.

    - is_loading (boolean; required):
        Determines if the component is loading or not.

    - prop_name (string; required):
        Holds which property is loading.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- title (string; optional):
    Card title."""
    @_explicitize_args
    def __init__(self, children=None, active_tab_key=Component.UNDEFINED, body_style=Component.UNDEFINED, bordered=Component.UNDEFINED, head_style=Component.UNDEFINED, hoverable=Component.UNDEFINED, title=Component.UNDEFINED, loading=Component.UNDEFINED, loading_state=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'active_tab_key', 'body_style', 'bordered', 'class_name', 'head_style', 'hoverable', 'key', 'loading', 'loading_state', 'style', 'title']
        self._type = 'Card'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'active_tab_key', 'body_style', 'bordered', 'class_name', 'head_style', 'hoverable', 'key', 'loading', 'loading_state', 'style', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Card, self).__init__(children=children, **args)

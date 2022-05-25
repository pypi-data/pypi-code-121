# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Button(Component):
    """A Button component.
A basic Button component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- danger (boolean; default False):
    Set the danger status of button.

- disabled (boolean; default False):
    Disabled state of button.

- href (string; optional):
    Pass a URL (relative or absolute) to make the menu entry a link.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

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

- n_clicks (number; default 0):
    An integer that represents the number of times that this element
    has been clicked on.

- shape (a value equal to: 'default', 'circle', 'round'; default 'default'):
    The shape of the button.

- size (a value equal to: 'large', 'middle', 'small'; default 'middle'):
    The size of the button.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- target (string; optional):
    Same as target attribute of a, works when href is specified.

- type (a value equal to: 'default', 'primary', 'ghost', 'dashed', 'link', 'text'; default 'default'):
    The type of the button."""
    @_explicitize_args
    def __init__(self, children=None, danger=Component.UNDEFINED, disabled=Component.UNDEFINED, shape=Component.UNDEFINED, size=Component.UNDEFINED, target=Component.UNDEFINED, type=Component.UNDEFINED, n_clicks=Component.UNDEFINED, loading_state=Component.UNDEFINED, href=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'danger', 'disabled', 'href', 'key', 'loading_state', 'n_clicks', 'shape', 'size', 'style', 'target', 'type']
        self._type = 'Button'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'danger', 'disabled', 'href', 'key', 'loading_state', 'n_clicks', 'shape', 'size', 'style', 'target', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Button, self).__init__(children=children, **args)

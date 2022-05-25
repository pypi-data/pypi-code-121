# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Divider(Component):
    """A Divider component.
Divides content with a simple line and optional text included.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- dashed (boolean; optional):
    Whether line is dashed.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- orientation (a value equal to: 'left', 'right', 'center'; optional):
    The position of title inside divider.

- orientation_margin (string | number; optional):
    The margin-left/right between the title and its closest border,
    while the orientation must be left or right.

- plain (boolean; optional):
    Divider text show as plain style.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- type (a value equal to: 'horizontal', 'vertical'; optional):
    The direction type of divider."""
    @_explicitize_args
    def __init__(self, children=None, dashed=Component.UNDEFINED, orientation=Component.UNDEFINED, orientation_margin=Component.UNDEFINED, plain=Component.UNDEFINED, type=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'dashed', 'key', 'orientation', 'orientation_margin', 'plain', 'style', 'type']
        self._type = 'Divider'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'dashed', 'key', 'orientation', 'orientation_margin', 'plain', 'style', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Divider, self).__init__(children=children, **args)

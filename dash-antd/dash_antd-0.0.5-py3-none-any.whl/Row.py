# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Row(Component):
    """A Row component.
Row

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- align (a value equal to: 'top', 'middle', 'bottom'; default 'top'):
    Vertical alignment.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- gutter (number | dict; default 0):
    Spacing between grids, could be a number or a object like { xs: 8,
    sm: 16, md: 24} Or you can use array to make horizontal and
    vertical spacing work at the same time [horizontal, vertical].

- justify (a value equal to: 'start', 'end', 'center', 'space-around', 'space-between', 'space-evenly'; default 'start'):
    Horizontal arrangement.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- wrap (boolean; default True):
    Auto wrap line."""
    @_explicitize_args
    def __init__(self, children=None, align=Component.UNDEFINED, gutter=Component.UNDEFINED, justify=Component.UNDEFINED, wrap=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'align', 'class_name', 'gutter', 'justify', 'key', 'style', 'wrap']
        self._type = 'Row'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'align', 'class_name', 'gutter', 'justify', 'key', 'style', 'wrap']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Row, self).__init__(children=children, **args)

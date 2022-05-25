# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Space(Component):
    """A Space component.
Set components spacing.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- align (a value equal to: 'start', 'end', 'center', 'baseline'; optional):
    Align items.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- direction (a value equal to: 'vertical', 'horizontal'; optional):
    The space direction.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- size (number; optional):
    The space size.

- split (a list of or a singular dash component, string or number; optional):
    Set split.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- wrap (boolean; optional):
    Auto wrap line, when horizontal effective."""
    @_explicitize_args
    def __init__(self, children=None, align=Component.UNDEFINED, direction=Component.UNDEFINED, size=Component.UNDEFINED, split=Component.UNDEFINED, wrap=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'align', 'class_name', 'direction', 'key', 'size', 'split', 'style', 'wrap']
        self._type = 'Space'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'align', 'class_name', 'direction', 'key', 'size', 'split', 'style', 'wrap']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Space, self).__init__(children=children, **args)

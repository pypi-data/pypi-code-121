# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tag(Component):
    """A Tag component.
Tag for categorizing or markup.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- closable (boolean; optional):
    Whether the Tag can be closed.

- close_icon (string; optional):
    Custom close icon.

- color (string; optional):
    Color of the Tag.

- icon (string; optional):
    Set the icon of tag.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- visible (boolean; optional):
    Whether the Tag is closed or not."""
    @_explicitize_args
    def __init__(self, children=None, closable=Component.UNDEFINED, close_icon=Component.UNDEFINED, color=Component.UNDEFINED, icon=Component.UNDEFINED, visible=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'closable', 'close_icon', 'color', 'icon', 'key', 'style', 'visible']
        self._type = 'Tag'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'closable', 'close_icon', 'color', 'icon', 'key', 'style', 'visible']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Tag, self).__init__(children=children, **args)

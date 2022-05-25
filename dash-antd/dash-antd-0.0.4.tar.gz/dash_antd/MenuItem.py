# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MenuItem(Component):
    """A MenuItem component.
MenuItem to be used as child elements to the "Menu" component.
If used, "items" property on menu must be left empty.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- danger (boolean; optional):
    Display the danger style.

- disabled (boolean; optional):
    Whether menu item is disabled.

- icon (a list of or a singular dash component, string or number; optional):
    The icon of the menu item.

- key (string; required):
    Unique ID of the menu item   A unique identifier for the
    component, used to improve performance by React.js while rendering
    components See https://reactjs.org/docs/lists-and-keys.html for
    more info.

- label (a list of or a singular dash component, string or number; required):
    Menu label.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- title (string; optional):
    Set display title for collapsed item."""
    @_explicitize_args
    def __init__(self, children=None, danger=Component.UNDEFINED, disabled=Component.UNDEFINED, icon=Component.UNDEFINED, key=Component.REQUIRED, label=Component.REQUIRED, title=Component.UNDEFINED, id=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'danger', 'disabled', 'icon', 'key', 'label', 'style', 'title']
        self._type = 'MenuItem'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'danger', 'disabled', 'icon', 'key', 'label', 'style', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['key', 'label']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(MenuItem, self).__init__(children=children, **args)

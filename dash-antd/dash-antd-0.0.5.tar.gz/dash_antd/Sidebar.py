# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Sidebar(Component):
    """A Sidebar component.
Handling the overall layout of a page.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- collapsed (boolean; default False):
    Whether the sidebar is collapsed.

- collapsed_width (number; default 80):
    Width of the collapsed sidebar, by setting to 0 a special trigger
    will appear.

- collapsible (boolean; default False):
    Whether the sidebar can be collapsed.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- reverse_arrow (boolean; default False):
    Reverse direction of arrow, for a sidebar that expands from the
    right.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- theme (a value equal to: 'light', 'dark'; optional):
    Color theme of the sidebar.

- width (string | number; default 200):
    Width of the sidebar."""
    @_explicitize_args
    def __init__(self, children=None, collapsed=Component.UNDEFINED, collapsed_width=Component.UNDEFINED, collapsible=Component.UNDEFINED, reverse_arrow=Component.UNDEFINED, theme=Component.UNDEFINED, width=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'collapsed', 'collapsed_width', 'collapsible', 'key', 'reverse_arrow', 'style', 'theme', 'width']
        self._type = 'Sidebar'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'collapsed', 'collapsed_width', 'collapsible', 'key', 'reverse_arrow', 'style', 'theme', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Sidebar, self).__init__(children=children, **args)

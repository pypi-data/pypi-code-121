# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PageHeader(Component):
    """A PageHeader component.
A header with common actions and design elements built in.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- back_icon (a list of or a singular dash component, string or number; optional):
    Custom back icon, if False the back icon will not be displayed.

- breadcrumb_routes (list of dicts; optional):
    Routes for breadcrumbs to be displayed in page header.

    `breadcrumb_routes` is a list of dicts with keys:

    - breadcrumbName (string; required)

    - children (list of dicts; required)

        `children` is a list of dicts with keys:

        - breadcrumbName (string; required)

        - path (string; required)

    - path (string; required)

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- extra (a list of or a singular dash component, string or number; optional):
    Operating area, at the end of the line of the title line.

- footer (a list of or a singular dash component, string or number; optional):
    PageHeader's footer, generally used to render TabBar.

- ghost (boolean; optional):
    PageHeader type, will change background color.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- sub_title (a list of or a singular dash component, string or number; optional):
    Custom subtitle text.

- title (a list of or a singular dash component, string or number; optional):
    Custom title text."""
    @_explicitize_args
    def __init__(self, children=None, back_icon=Component.UNDEFINED, breadcrumb_routes=Component.UNDEFINED, extra=Component.UNDEFINED, footer=Component.UNDEFINED, ghost=Component.UNDEFINED, sub_title=Component.UNDEFINED, title=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'back_icon', 'breadcrumb_routes', 'class_name', 'extra', 'footer', 'ghost', 'key', 'style', 'sub_title', 'title']
        self._type = 'PageHeader'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'back_icon', 'breadcrumb_routes', 'class_name', 'extra', 'footer', 'ghost', 'key', 'style', 'sub_title', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(PageHeader, self).__init__(children=children, **args)

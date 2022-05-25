# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Col(Component):
    """A Col component.
Col

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- flex (string | number; optional):
    Flex layout style.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- lg (number | dict; optional):
    screen ≥ 992px, could be a span value or an object containing
    above props.

- md (number | dict; optional):
    screen ≥ 768px, could be a span value or an object containing
    above props.

- offset (number; optional):
    The number of cells to offset Col from the left.

- order (number; optional):
    Raster order.

- pull (number; optional):
    The number of cells that raster is moved to the left.

- push (number; optional):
    The number of cells that raster is moved to the right.

- sm (number | dict; optional):
    screen ≥ 576px, could be a span value or an object containing
    above props.

- span (number; optional):
    Raster number of cells to occupy, 0 corresponds to display: none.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- xl (number | dict; optional):
    screen ≥ 1200px, could be a span value or an object containing
    above props.

- xs (number | dict; optional):
    screen < 576px and also default setting, could be a span value or
    an object containing above props.

- xxl (number | dict; optional):
    screen ≥ 1600px, could be a span value or an object containing
    above props."""
    @_explicitize_args
    def __init__(self, children=None, flex=Component.UNDEFINED, offset=Component.UNDEFINED, order=Component.UNDEFINED, pull=Component.UNDEFINED, push=Component.UNDEFINED, span=Component.UNDEFINED, xs=Component.UNDEFINED, sm=Component.UNDEFINED, md=Component.UNDEFINED, lg=Component.UNDEFINED, xl=Component.UNDEFINED, xxl=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'flex', 'key', 'lg', 'md', 'offset', 'order', 'pull', 'push', 'sm', 'span', 'style', 'xl', 'xs', 'xxl']
        self._type = 'Col'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'flex', 'key', 'lg', 'md', 'offset', 'order', 'pull', 'push', 'sm', 'span', 'style', 'xl', 'xs', 'xxl']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Col, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Checkbox(Component):
    """A Checkbox component.
Checkbox component.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- checked (boolean; default False):
    Whether the checkbox is selected.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; default False):
    Whether the checkbox is disabled.

- indeterminate (boolean; default False):
    Whether the checkbox is indeterminate.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    @_explicitize_args
    def __init__(self, children=None, checked=Component.UNDEFINED, disabled=Component.UNDEFINED, indeterminate=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'checked', 'class_name', 'disabled', 'indeterminate', 'key', 'style']
        self._type = 'Checkbox'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'checked', 'class_name', 'disabled', 'indeterminate', 'key', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Checkbox, self).__init__(children=children, **args)

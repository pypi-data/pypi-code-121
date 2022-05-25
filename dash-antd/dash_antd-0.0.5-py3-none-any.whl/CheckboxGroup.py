# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CheckboxGroup(Component):
    """A CheckboxGroup component.
A collection of Checkboxes.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Disables all checkboxes within the group.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- options (list of strings | list of numbers; optional):
    All options within the CheckboxGroup.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- value (list of strings; optional):
    Currently selected values."""
    @_explicitize_args
    def __init__(self, value=Component.UNDEFINED, options=Component.UNDEFINED, disabled=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'class_name', 'disabled', 'key', 'options', 'style', 'value']
        self._type = 'CheckboxGroup'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'class_name', 'disabled', 'key', 'options', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(CheckboxGroup, self).__init__(**args)

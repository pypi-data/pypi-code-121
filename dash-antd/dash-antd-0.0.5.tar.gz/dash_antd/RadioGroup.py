# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RadioGroup(Component):
    """A RadioGroup component.
RadioGroup

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- button_style (a value equal to: 'outline', 'solid'; optional):
    The style type of radio button.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Disable all radio buttons.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- option_type (a value equal to: 'default', 'button'; optional):
    Set Radio optionType.

- options (list of strings | list of numbers; optional):
    Set children optional.

- size (a value equal to: 'large', 'middle', 'small'; optional):
    The size of radio button.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    @_explicitize_args
    def __init__(self, children=None, button_style=Component.UNDEFINED, disabled=Component.UNDEFINED, options=Component.UNDEFINED, option_type=Component.UNDEFINED, size=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'button_style', 'class_name', 'disabled', 'key', 'option_type', 'options', 'size', 'style']
        self._type = 'RadioGroup'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'button_style', 'class_name', 'disabled', 'key', 'option_type', 'options', 'size', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(RadioGroup, self).__init__(children=children, **args)

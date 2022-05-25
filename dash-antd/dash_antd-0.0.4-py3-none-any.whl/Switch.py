# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Switch(Component):
    """A Switch component.
Switching Selector.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- checked (boolean; optional):
    Specifies whether the radio is selected.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Disable radio.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; required):
        Holds the name of the component that is loading.

    - is_loading (boolean; required):
        Determines if the component is loading or not.

    - prop_name (string; required):
        Holds which property is loading.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- switch (a value equal to: 'default', 'small'; optional):
    The size of the Switch."""
    @_explicitize_args
    def __init__(self, checked=Component.UNDEFINED, disabled=Component.UNDEFINED, switch=Component.UNDEFINED, loading_state=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'checked', 'class_name', 'disabled', 'key', 'loading_state', 'style', 'switch']
        self._type = 'Switch'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'checked', 'class_name', 'disabled', 'key', 'loading_state', 'style', 'switch']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Switch, self).__init__(**args)

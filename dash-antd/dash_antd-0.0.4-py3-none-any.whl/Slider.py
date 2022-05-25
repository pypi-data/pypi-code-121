# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Slider(Component):
    """A Slider component.
A Slider component for displaying current value and intervals in range.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Disable radio.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- marks (dict; optional):
    Tick mark of Slider, type of key must be number, and must in
    closed interval [min, max], each mark can declare its own style.

    `marks` is a dict with keys:


      Or dict with keys:


- max (number; default 100):
    The maximum value the slider can slide to.

- min (number; default 0):
    The minimum value the slider can slide to.

- range (boolean; optional):
    Dual thumb mode.

- reverse (boolean; optional):
    Reverse the component.

- step (number; optional):
    The granularity the slider can step through values. Must greater
    than 0, and be divided by (max - min). When marks no None, step
    can be None.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- value (number; optional):
    The value of slider. When range is False, use number, otherwise,
    use [number, number].

- vertical (boolean; optional):
    If True, the slider will be vertical."""
    @_explicitize_args
    def __init__(self, disabled=Component.UNDEFINED, marks=Component.UNDEFINED, max=Component.UNDEFINED, min=Component.UNDEFINED, range=Component.UNDEFINED, reverse=Component.UNDEFINED, step=Component.UNDEFINED, value=Component.UNDEFINED, vertical=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'class_name', 'disabled', 'key', 'marks', 'max', 'min', 'range', 'reverse', 'step', 'style', 'value', 'vertical']
        self._type = 'Slider'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'class_name', 'disabled', 'key', 'marks', 'max', 'min', 'range', 'reverse', 'step', 'style', 'value', 'vertical']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Slider, self).__init__(**args)

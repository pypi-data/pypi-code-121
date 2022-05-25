# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DateRangePicker(Component):
    """A DateRangePicker component.
Select Date or DateTime

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allow_clear (boolean; optional):
    If allow to remove input content with clear icon.

- bordered (boolean; optional):
    Whether has border style.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; optional):
    Disables all checkboxes within the group.

- end (string; optional):
    The selected end date / datetime.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- open (boolean; optional):
    The open state of picker.

- placement (a value equal to: 'bottomLeft', 'bottomRight', 'topLeft', 'topRight'; optional):
    The position where the selection box pops up.

- show_now (boolean; optional):
    Whether to show 'Now' button on panel when show_time is set.

- show_time (boolean; optional):
    Whether to provide an additional time selection.

- size (a value equal to: 'large', 'middle', 'small'; optional):
    To determine the size of the input box, the height of large and
    small, are 40px and 24px respectively, while default size is 32px.

- start (string; optional):
    The selected start date / datetime.

- status (a value equal to: 'error', 'warning'; optional):
    Set validation status.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    @_explicitize_args
    def __init__(self, allow_clear=Component.UNDEFINED, bordered=Component.UNDEFINED, disabled=Component.UNDEFINED, open=Component.UNDEFINED, placement=Component.UNDEFINED, show_time=Component.UNDEFINED, show_now=Component.UNDEFINED, size=Component.UNDEFINED, status=Component.UNDEFINED, start=Component.UNDEFINED, end=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allow_clear', 'bordered', 'class_name', 'disabled', 'end', 'key', 'open', 'placement', 'show_now', 'show_time', 'size', 'start', 'status', 'style']
        self._type = 'DateRangePicker'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allow_clear', 'bordered', 'class_name', 'disabled', 'end', 'key', 'open', 'placement', 'show_now', 'show_time', 'size', 'start', 'status', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DateRangePicker, self).__init__(**args)

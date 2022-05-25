# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Input(Component):
    """An Input component.
A basic widget for getting the user input is a text field.
Keyboard and mouse can be used for providing or changing data.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- addon_after (a list of or a singular dash component, string or number; optional):
    The label text displayed after (on the right side of) the input
    field.

- addon_before (a list of or a singular dash component, string or number; optional):
    The label text displayed before (on the left side of) the input
    field.

- allow_clear (boolean; optional):
    If allow to remove input content with clear icon.

- autocomplete (a value equal to: 'on', 'off'; optional):
    This attribute indicates whether the value of the control can be
    automatically completed by the browser.

- bordered (boolean; optional):
    Whether has border style.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- debounce (boolean; default False):
    If True, changes to input will be sent back to the Dash server
    only when the enter key is pressed or when the component loses
    focus.  If it's False, it will sent the value back on every
    change.

- disabled (boolean; optional):
    Whether the input is disabled.

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

- max (string | number; optional):
    The maximum (numeric or date-time) value for this item, which must
    not be less than its minimum (min attribute) value.

- max_length (number; optional):
    The max length.

- min (string | number; optional):
    The minimum (numeric or date-time) value for this item, which must
    not be greater than its maximum (max attribute) value.

- n_blur (number; default 0):
    Number of times the input lost focus.

- n_blur_timestamp (number; default -1):
    Last time the input lost focus.

- n_submit (number; default 0):
    Number of times the `Enter` key was pressed while the input had
    focus.

- n_submit_timestamp (number; default -1):
    Last time that `Enter` was pressed.

- placeholder (string; optional):
    A hint to the user of what can be entered in the control.

- readonly (boolean; optional):
    Indicates whether the element can be edited.

- show_count (boolean; optional):
    Whether show character count.

- size (a value equal to: 'large', 'middle', 'small'; optional):
    The size of the input box.

- status (a value equal to: 'error', 'warning'; optional):
    Set validation status.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- type (a value equal to: 'number', 'text', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'; optional):
    The type of control to render.

- value (string | number; optional):
    The input content value."""
    @_explicitize_args
    def __init__(self, value=Component.UNDEFINED, addon_after=Component.UNDEFINED, addon_before=Component.UNDEFINED, allow_clear=Component.UNDEFINED, autocomplete=Component.UNDEFINED, bordered=Component.UNDEFINED, disabled=Component.UNDEFINED, max=Component.UNDEFINED, min=Component.UNDEFINED, max_length=Component.UNDEFINED, readonly=Component.UNDEFINED, show_count=Component.UNDEFINED, size=Component.UNDEFINED, n_blur=Component.UNDEFINED, n_blur_timestamp=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, debounce=Component.UNDEFINED, type=Component.UNDEFINED, status=Component.UNDEFINED, placeholder=Component.UNDEFINED, loading_state=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'addon_after', 'addon_before', 'allow_clear', 'autocomplete', 'bordered', 'class_name', 'debounce', 'disabled', 'key', 'loading_state', 'max', 'max_length', 'min', 'n_blur', 'n_blur_timestamp', 'n_submit', 'n_submit_timestamp', 'placeholder', 'readonly', 'show_count', 'size', 'status', 'style', 'type', 'value']
        self._type = 'Input'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'addon_after', 'addon_before', 'allow_clear', 'autocomplete', 'bordered', 'class_name', 'debounce', 'disabled', 'key', 'loading_state', 'max', 'max_length', 'min', 'n_blur', 'n_blur_timestamp', 'n_submit', 'n_submit_timestamp', 'placeholder', 'readonly', 'show_count', 'size', 'status', 'style', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Input, self).__init__(**args)

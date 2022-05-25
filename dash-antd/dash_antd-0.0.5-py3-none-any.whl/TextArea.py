# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class TextArea(Component):
    """A TextArea component.
TextArea component.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allow_clear (boolean; optional):
    If allow to remove input content with clear icon.

- bordered (boolean; optional):
    Whether has border style.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- cols (number; optional):
    Defines the number of columns in a textarea.

- debounce (boolean; default False):
    If True, changes to input will be sent back to the Dash server
    only on enter or when losing focus. If it's False, it will sent
    the value back on every change.

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

- max_length (number; optional):
    The max length.

- n_blur (number; default 0):
    Number of times the input lost focus.

- n_blur_timestamp (number; default -1):
    Last time the input lost focus.

- n_clicks (number; default 0):
    An integer that represents the number of times that this element
    has been clicked on.

- n_submit (number; default 0):
    Number of times the `Enter` key was pressed while the textarea had
    focus.

- n_submit_timestamp (number; default -1):
    Last time that `Enter` was pressed.

- placeholder (string; optional):
    A hint to the user of what can be entered in the control.

- readonly (boolean; optional):
    Indicates whether the element can be edited.

- rows (number; optional):
    Defines the number of rows in a text area.

- show_count (boolean; optional):
    Whether show text count.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- value (string; default ''):
    The input content value."""
    @_explicitize_args
    def __init__(self, value=Component.UNDEFINED, allow_clear=Component.UNDEFINED, bordered=Component.UNDEFINED, cols=Component.UNDEFINED, max_length=Component.UNDEFINED, show_count=Component.UNDEFINED, readonly=Component.UNDEFINED, rows=Component.UNDEFINED, placeholder=Component.UNDEFINED, loading_state=Component.UNDEFINED, n_blur=Component.UNDEFINED, n_blur_timestamp=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, n_clicks=Component.UNDEFINED, debounce=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allow_clear', 'bordered', 'class_name', 'cols', 'debounce', 'key', 'loading_state', 'max_length', 'n_blur', 'n_blur_timestamp', 'n_clicks', 'n_submit', 'n_submit_timestamp', 'placeholder', 'readonly', 'rows', 'show_count', 'style', 'value']
        self._type = 'TextArea'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allow_clear', 'bordered', 'class_name', 'cols', 'debounce', 'key', 'loading_state', 'max_length', 'n_blur', 'n_blur_timestamp', 'n_clicks', 'n_submit', 'n_submit_timestamp', 'placeholder', 'readonly', 'rows', 'show_count', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(TextArea, self).__init__(**args)

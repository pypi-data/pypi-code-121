# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Select(Component):
    """A Select component.
A dropdown component

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allow_clear (boolean; optional):
    Show clear button.

- auto_clear_search_value (boolean; optional):
    Whether the current search will be cleared on selecting an item.
    Only applies when mode is set to multiple or tags.

- bordered (boolean; optional):
    Whether has border style.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- clear_icon (string; optional):
    The custom clear icon.

- default_active_first_option (boolean; optional):
    Whether to activate first option by default.

- disabled (boolean; optional):
    Whether disabled select.

- dropdown_class_name (string; optional):
    The className of dropdown menu.

- dropdown_match_select_width (number; optional):
    Determine whether the dropdown menu and the select input are the
    same width. Default set min-width same as input. Will ignore when
    value less than select width False will disable virtual scroll.

- dropdown_style (dict; optional):
    The style of dropdown menu.

- fieldNames (dict; optional):
    Customize node label, value, options field name.

- filter_option (boolean; optional):
    If True, filter options by input.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- label_in_value (boolean; optional):
    Whether to embed label in value, turn the format of value from
    string to { value: string, label: ReactNode }.

- list_height (number; optional):
    Config popup height.

- loading (boolean; optional):
    Indicate loading state.

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

- max_tag_count (number; optional):
    Max tag count to show. responsive will cost render performance.

- max_tag_text_length (number; optional):
    Max tag text length to show.

- menu_item_selected_icon (string; optional):
    The custom menuItemSelected icon with multiple options.

- mode (a value equal to: 'multiple', 'tags'; optional):
    Set mode of Select.

- n_blur (number; default 0):
    Number of times the input lost focus.

- n_blur_timestamp (number; default -1):
    Last time the input lost focus.

- n_submit (number; default 0):
    Number of times the `Enter` key was pressed while the input had
    focus.

- n_submit_timestamp (number; default -1):
    Last time that `Enter` was pressed.

- open (boolean; optional):
    Controlled open state of dropdown.

- option_filter_prop (string; optional):
    Which prop value of option will be used for filter if filterOption
    is True. If options is set, it should be set to 'label'.

- option_label_prop (string; optional):
    Which prop value of option will render as content of select.

- options (list of dicts; optional):
    Select options. Will get better perf than jsx definition        {
    label, value }[].

- placeholder (string; optional):
    Placeholder of select.

- placement (a value equal to: 'bottomLeft', 'bottomRight', 'topLeft', 'topRight'; optional):
    The position where the selection box pops up.

- remove_icon (string; optional):
    The custom remove icon.

- show_arrow (boolean; optional):
    Whether to show the drop-down arrow.

- show_search (boolean; optional):
    Whether show search input in single mode.

- size (a value equal to: 'large', 'middle', 'small'; optional):
    Size of Select input.

- status (a value equal to: 'error', 'warning'; optional):
    Set validation status.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- suffix_icon (string; optional):
    The custom suffix icon.

- token_separators (list of strings; optional):
    Separator used to tokenize, only applies when mode=\"tags\".

- value (string | number | list of strings | list of numbers; optional):
    Current selected option (considered as a immutable array).

- virtual (boolean; optional):
    Disable virtual scroll when set to False."""
    @_explicitize_args
    def __init__(self, allow_clear=Component.UNDEFINED, auto_clear_search_value=Component.UNDEFINED, bordered=Component.UNDEFINED, clear_icon=Component.UNDEFINED, default_active_first_option=Component.UNDEFINED, disabled=Component.UNDEFINED, dropdown_class_name=Component.UNDEFINED, dropdown_match_select_width=Component.UNDEFINED, dropdown_style=Component.UNDEFINED, fieldNames=Component.UNDEFINED, filter_option=Component.UNDEFINED, label_in_value=Component.UNDEFINED, list_height=Component.UNDEFINED, loading=Component.UNDEFINED, max_tag_count=Component.UNDEFINED, max_tag_text_length=Component.UNDEFINED, menu_item_selected_icon=Component.UNDEFINED, mode=Component.UNDEFINED, open=Component.UNDEFINED, option_filter_prop=Component.UNDEFINED, option_label_prop=Component.UNDEFINED, options=Component.UNDEFINED, placeholder=Component.UNDEFINED, placement=Component.UNDEFINED, remove_icon=Component.UNDEFINED, show_arrow=Component.UNDEFINED, show_search=Component.UNDEFINED, size=Component.UNDEFINED, status=Component.UNDEFINED, suffix_icon=Component.UNDEFINED, token_separators=Component.UNDEFINED, value=Component.UNDEFINED, virtual=Component.UNDEFINED, loading_state=Component.UNDEFINED, n_blur=Component.UNDEFINED, n_blur_timestamp=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allow_clear', 'auto_clear_search_value', 'bordered', 'class_name', 'clear_icon', 'default_active_first_option', 'disabled', 'dropdown_class_name', 'dropdown_match_select_width', 'dropdown_style', 'fieldNames', 'filter_option', 'key', 'label_in_value', 'list_height', 'loading', 'loading_state', 'max_tag_count', 'max_tag_text_length', 'menu_item_selected_icon', 'mode', 'n_blur', 'n_blur_timestamp', 'n_submit', 'n_submit_timestamp', 'open', 'option_filter_prop', 'option_label_prop', 'options', 'placeholder', 'placement', 'remove_icon', 'show_arrow', 'show_search', 'size', 'status', 'style', 'suffix_icon', 'token_separators', 'value', 'virtual']
        self._type = 'Select'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allow_clear', 'auto_clear_search_value', 'bordered', 'class_name', 'clear_icon', 'default_active_first_option', 'disabled', 'dropdown_class_name', 'dropdown_match_select_width', 'dropdown_style', 'fieldNames', 'filter_option', 'key', 'label_in_value', 'list_height', 'loading', 'loading_state', 'max_tag_count', 'max_tag_text_length', 'menu_item_selected_icon', 'mode', 'n_blur', 'n_blur_timestamp', 'n_submit', 'n_submit_timestamp', 'open', 'option_filter_prop', 'option_label_prop', 'options', 'placeholder', 'placement', 'remove_icon', 'show_arrow', 'show_search', 'size', 'status', 'style', 'suffix_icon', 'token_separators', 'value', 'virtual']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Select, self).__init__(**args)

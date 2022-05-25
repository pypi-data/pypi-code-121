# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Menu(Component):
    """A Menu component.
A versatile menu for navigation.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- expand_icon (a list of or a singular dash component, string or number; optional):
    custom expand icon of submenu.

- force_sub_menu_render (boolean; optional):
    Render submenu into DOM before it becomes visible.

- inline_collapsed (boolean; optional):
    Specifies the collapsed status when menu is inline mode.

- inline_indent (number; optional):
    Indent (in pixels) of inline menu items on each level.

- items (list of boolean | number | string | dict | lists; optional):
    Menu item content.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- mode (a value equal to: 'vertical', 'horizontal', 'inline'; optional):
    Type of menu.

- multiple (boolean; optional):
    Allows selection of multiple items.

- open_keys (list of strings; optional):
    Array with the keys of currently opened sub-menus.

- overflowed_indicator (a list of or a singular dash component, string or number; optional):
    Customized the ellipsis icon when menu is collapsed horizontally.

- selectable (boolean; default True):
    Allows selecting menu items.

- selected_keys (list of strings; optional):
    Array with the keys of currently selected menu items.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- sub_menu_close_delay (number; optional):
    Delay time to hide submenu when mouse leaves (in seconds).

- sub_menu_open_delay (number; optional):
    Delay time to show submenu when mouse enters, (in seconds).

- theme (a value equal to: 'light', 'dark'; optional):
    Color theme of the menu."""
    @_explicitize_args
    def __init__(self, children=None, expand_icon=Component.UNDEFINED, force_sub_menu_render=Component.UNDEFINED, inline_collapsed=Component.UNDEFINED, inline_indent=Component.UNDEFINED, items=Component.UNDEFINED, mode=Component.UNDEFINED, multiple=Component.UNDEFINED, open_keys=Component.UNDEFINED, overflowed_indicator=Component.UNDEFINED, selectable=Component.UNDEFINED, selected_keys=Component.UNDEFINED, sub_menu_close_delay=Component.UNDEFINED, sub_menu_open_delay=Component.UNDEFINED, theme=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'expand_icon', 'force_sub_menu_render', 'inline_collapsed', 'inline_indent', 'items', 'key', 'mode', 'multiple', 'open_keys', 'overflowed_indicator', 'selectable', 'selected_keys', 'style', 'sub_menu_close_delay', 'sub_menu_open_delay', 'theme']
        self._type = 'Menu'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'expand_icon', 'force_sub_menu_render', 'inline_collapsed', 'inline_indent', 'items', 'key', 'mode', 'multiple', 'open_keys', 'overflowed_indicator', 'selectable', 'selected_keys', 'style', 'sub_menu_close_delay', 'sub_menu_open_delay', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Menu, self).__init__(children=children, **args)

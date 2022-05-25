# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DropdownMenu(Component):
    """A DropdownMenu component.
A Dropdown component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- arrow (boolean; optional):
    Whether the dropdown arrow should be visible.

- disabled (boolean; optional):
    Whether the dropdown menu is disabled.

- items (list of boolean | number | string | dict | lists; required):
    Items displayed in the dropdown menu.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- placement (a value equal to: 'bottom', 'bottomLeft', 'bottomRight', 'top', 'topLeft', 'topRight'; optional):
    Placement of popup menu.

- trigger (list of a value equal to: 'click', 'hover', 'contextMenu's; optional):
    The trigger mode which executes the dropdown action. Note that
    hover can't be used on touchscreens.

- visible (boolean; optional):
    Whether the dropdown menu is currently visible."""
    @_explicitize_args
    def __init__(self, children=None, items=Component.REQUIRED, arrow=Component.UNDEFINED, disabled=Component.UNDEFINED, placement=Component.UNDEFINED, trigger=Component.UNDEFINED, visible=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'arrow', 'disabled', 'items', 'key', 'placement', 'trigger', 'visible']
        self._type = 'DropdownMenu'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'arrow', 'disabled', 'items', 'key', 'placement', 'trigger', 'visible']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['items']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DropdownMenu, self).__init__(children=children, **args)

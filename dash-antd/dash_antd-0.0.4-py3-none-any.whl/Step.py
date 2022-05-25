# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Step(Component):
    """A Step component.
Step

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- description (string; optional):
    Description of the step.

- disabled (boolean; optional):
    Disable click.

- icon (string; optional):
    Icon of the step.

- key (string; optional):
    A unique identifier for the component, used to improve performance
    by React.js while rendering components See
    https://reactjs.org/docs/lists-and-keys.html for more info.

- status (a value equal to: 'wait', 'process', 'finish', 'error'; optional):
    To specify the status. It will be automatically set by current of
    Steps if not configured.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- sub_title (string; optional):
    Subtitle of the step.

- title (string; optional):
    Title of the step."""
    @_explicitize_args
    def __init__(self, children=None, description=Component.UNDEFINED, disabled=Component.UNDEFINED, icon=Component.UNDEFINED, status=Component.UNDEFINED, sub_title=Component.UNDEFINED, title=Component.UNDEFINED, id=Component.UNDEFINED, key=Component.UNDEFINED, style=Component.UNDEFINED, class_name=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'description', 'disabled', 'icon', 'key', 'status', 'style', 'sub_title', 'title']
        self._type = 'Step'
        self._namespace = 'dash_antd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'description', 'disabled', 'icon', 'key', 'status', 'style', 'sub_title', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Step, self).__init__(children=children, **args)

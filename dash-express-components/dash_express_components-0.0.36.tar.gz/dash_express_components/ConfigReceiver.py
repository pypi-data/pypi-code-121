# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ConfigReceiver(Component):
    """A ConfigReceiver component.
A config receiver listening for `window.postMessage()`

@hideconstructor

@example
 rec = dxc.ConfigReceiver(
          id="plotConfig",
          token="test"
 )

 window.postMessage({config: "Test", token:"test" })
@public

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks. @type
    {string}.

- config (boolean | number | string | dict | list; optional):
    Prop The resulting configuration of the plot. @type {Object}.

- token (string; required):
    A token used to define the configuration across frames. @type
    {string}."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, token=Component.REQUIRED, config=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'config', 'token']
        self._type = 'ConfigReceiver'
        self._namespace = 'dash_express_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'config', 'token']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'token']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ConfigReceiver, self).__init__(**args)

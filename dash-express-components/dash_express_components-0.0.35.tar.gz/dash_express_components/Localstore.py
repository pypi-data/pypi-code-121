# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Localstore(Component):
    """A Localstore component.


Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- config (boolean | number | string | dict | list; optional):
    The config the user sets in this component.

- meta (boolean | number | string | dict | list; required):
    The metadata this section is based on.

- meta_out (boolean | number | string | dict | list; optional):
    The metadata section will create as output."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, config=Component.UNDEFINED, meta=Component.REQUIRED, meta_out=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'config', 'meta', 'meta_out']
        self._type = 'Localstore'
        self._namespace = 'dash_express_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'config', 'meta', 'meta_out']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'meta']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Localstore, self).__init__(**args)

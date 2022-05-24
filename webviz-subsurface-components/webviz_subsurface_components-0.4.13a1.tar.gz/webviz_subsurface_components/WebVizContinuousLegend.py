# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class WebVizContinuousLegend(Component):
    """A WebVizContinuousLegend component.


Keyword arguments:

- colorName (string; required)

- colorTables (string | list; optional)

- horizontal (boolean; optional)

- max (number; required)

- min (number; required)

- position (list of numbers; optional)

- title (string; required)"""
    @_explicitize_args
    def __init__(self, title=Component.REQUIRED, min=Component.REQUIRED, max=Component.REQUIRED, position=Component.UNDEFINED, colorName=Component.REQUIRED, horizontal=Component.UNDEFINED, colorTables=Component.UNDEFINED, **kwargs):
        self._prop_names = ['colorName', 'colorTables', 'horizontal', 'max', 'min', 'position', 'title']
        self._type = 'WebVizContinuousLegend'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['colorName', 'colorTables', 'horizontal', 'max', 'min', 'position', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['colorName', 'max', 'min', 'title']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(WebVizContinuousLegend, self).__init__(**args)

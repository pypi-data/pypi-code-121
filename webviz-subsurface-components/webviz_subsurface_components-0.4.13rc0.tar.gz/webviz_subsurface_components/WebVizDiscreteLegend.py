# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class WebVizDiscreteLegend(Component):
    """A WebVizDiscreteLegend component.


Keyword arguments:

- colorName (string; required)

- colorTables (string | list; optional)

- discreteData (boolean | number | string | dict | list; required)

- horizontal (boolean; optional)

- position (list of numbers; optional)

- title (string; required)"""
    @_explicitize_args
    def __init__(self, discreteData=Component.REQUIRED, title=Component.REQUIRED, position=Component.UNDEFINED, colorName=Component.REQUIRED, colorTables=Component.UNDEFINED, horizontal=Component.UNDEFINED, **kwargs):
        self._prop_names = ['colorName', 'colorTables', 'discreteData', 'horizontal', 'position', 'title']
        self._type = 'WebVizDiscreteLegend'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['colorName', 'colorTables', 'discreteData', 'horizontal', 'position', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['colorName', 'discreteData', 'title']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(WebVizDiscreteLegend, self).__init__(**args)

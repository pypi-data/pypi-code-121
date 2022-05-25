# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Configurator(Component):
    """A Configurator component.
<div style="width:450px; margin-left: 20px; float: right;  margin-top: -150px;">
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/configurator.png"/>
</div>


The configurator component helps to define plot definitions based on the
metadata of a dataframe.
Different configuration parts like `Filter`, `Transform` or `Plotter`
are combined in a single accordion component.

The metadata is used to compute the available parameters after data 
transformations and newly available colums are adjusted automatically.

@hideconstructor

@example
import dash_express_components as dxc
import plotly.express as px

meta = dxc.get_meta(px.data.gapminder())

 dxc.Configurator(
          id="plotConfig",
          meta=meta,
 )
@public

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks. @type
    {string}.

- config (boolean | number | string | dict | list; optional):
    Prop The resulting configuration of the plot. @type {Object}.

- meta (boolean | number | string | dict | list; required):
    The metadata the plotter selection is based on. @type {Object}.

- showFilter (boolean; default True):
    Prop to define the visibility of the Filter panel @type {boolean}.

- showMetadata (boolean; default False):
    Prop to define the visibility of the Metadata panel @type
    {boolean}.

- showParameterization (boolean; default False):
    Prop to define the visibility of the Parameterization panel @type
    {boolean}.

- showPlotter (boolean; default True):
    Prop to define the visibility of the Plot panel @type {boolean}.

- showStore (boolean; default False):
    Prop to define the visibility of the Store panel @type {boolean}.

- showTransform (boolean; default True):
    Prop to define the visibility of the Transform panel @type
    {boolean}.

- showUpdate (boolean; default True):
    Prop to define the visibility of the update plot button @type
    {boolean}."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, meta=Component.REQUIRED, config=Component.UNDEFINED, showFilter=Component.UNDEFINED, showTransform=Component.UNDEFINED, showPlotter=Component.UNDEFINED, showMetadata=Component.UNDEFINED, showParameterization=Component.UNDEFINED, showStore=Component.UNDEFINED, showUpdate=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'config', 'meta', 'showFilter', 'showMetadata', 'showParameterization', 'showPlotter', 'showStore', 'showTransform', 'showUpdate']
        self._type = 'Configurator'
        self._namespace = 'dash_express_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'config', 'meta', 'showFilter', 'showMetadata', 'showParameterization', 'showPlotter', 'showStore', 'showTransform', 'showUpdate']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'meta']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Configurator, self).__init__(**args)

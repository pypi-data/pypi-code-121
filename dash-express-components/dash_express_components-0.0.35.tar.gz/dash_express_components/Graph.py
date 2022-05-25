# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Graph(Component):
    """A Graph component.
<div style="width:450px; margin-left: 20px; float: right;  margin-top: -150px;">
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/graph.png"/>
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/graph-table.png"/>
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/graph-modal.png"/>
</div>


The `Graph` component is a combination of the original dash `Graph` and the dash `data_table`.

It can not only be used to render a plotly.js-powered data visualization,
but also shows a searchable table, if only data is submitted.

In addition, there is the possibility to add plot parameters as `defParams` and 
the dataframe `meta` data.  
This automatically adds a configurator modal, which can be opened via a button
at the bottom right.


@hideconstructor

@example
import dash_express_components as dxc
import plotly.express as px

meta = dxc.get_meta(px.data.gapminder())

dxc.Graph(
    id="fig",
    meta=meta,
    defParams={}
)
@public

Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app. @type {string}.

- className (string; optional):
    className of the parent div.

- defParams (dict; optional):
    Configuration to describe the plot features.

- figure (boolean | number | string | dict | list; default {    data: [],    layout: {},    frames: [],}):
    Plotly `figure` object. See schema:
    https://plotly.com/javascript/reference  `config` is set
    separately by the `config` property.

- meta (boolean | number | string | dict | list; optional):
    The metadata the plotter selection is based on.

- selectedData (boolean | number | string | dict | list; optional):
    The data selected in the plot or in the table.

- style (dict; optional):
    Generic style overrides on the plot div."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, defParams=Component.UNDEFINED, meta=Component.UNDEFINED, figure=Component.UNDEFINED, style=Component.UNDEFINED, selectedData=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'defParams', 'figure', 'meta', 'selectedData', 'style']
        self._type = 'Graph'
        self._namespace = 'dash_express_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'defParams', 'figure', 'meta', 'selectedData', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Graph, self).__init__(**args)

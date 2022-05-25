# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Transform(Component):
    """A Transform component.
<div style="width:450px; margin-left: 20px; float: right;  margin-top: -150px;">
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/transform.png"/>
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/transform-modal.png"/>
<img src="https://raw.githubusercontent.com/VK/dash-express-components/main/.media/transform-types.png"/>
</div>

The `Transform` component helps to create user defined data transformations.
Currently basic transformations are available, like:

<ul style="margin-left: 20px;">
   <li><b>eval</b></li>
   <li><b>groupby([...]).aggr([...])</b></li>
   <li><b>melt</b></li>
   <li><b>wide_to_long</b></li>
   <li><b>replace</b></li>
   <li><b>rename</b></li>
</ul>
@hideconstructor

@example
import dash_express_components as dxc
import plotly.express as px

meta = dxc.get_meta(px.data.gapminder())

dxc.Transform(
   id="transform",
   meta=meta
)
@public

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
        self._type = 'Transform'
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
        super(Transform, self).__init__(**args)

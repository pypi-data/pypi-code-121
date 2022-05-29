# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DeckGLMap(Component):
    """A DeckGLMap component.


Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- bounds (optional):
    Coordinate boundary for the view defined as [left, bottom, right,
    top].

- checkDatafileSchema (boolean; default False):
    Validate JSON datafile against schems.

- colorTables (list; optional):
    Prop containing color table data.

- coordinateUnit (string; optional):
    Parameters for the Distance Scale component Unit for the scale
    ruler.

- coords (dict; optional):
    Parameters for the InfoCard component.

    `coords` is a dict with keys:

    - multiPicking (boolean; optional):
        Enable or disable multi picking. Might have a performance
        penalty. See
        https://deck.gl/docs/api-reference/core/deck#pickmultipleobjects.

    - pickDepth (number; optional):
        Number of objects to pick. The more objects picked, the more
        picking operations will be done. See
        https://deck.gl/docs/api-reference/core/deck#pickmultipleobjects.

    - visible (boolean; optional):
        Toggle component visibility.

- editedData (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Prop containing edited data from layers.

- layers (list of dicts with strings as keys and values of type boolean | number | string | dict | list; optional)

- legend (dict; optional):
    Parameters for the legend.

    `legend` is a dict with keys:

    - cssStyle (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
        Legend css style can be used for positioning.

    - horizontal (boolean; optional):
        Orientation of color legend.

    - visible (boolean; optional):
        Toggle component visibility.

- resources (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Resource dictionary made available in the DeckGL specification as
    an enum. The values can be accessed like this:
    `\"@@#resources.resourceId\"`, where `resourceId` is the key in
    the `resources` dict. For more information, see the DeckGL
    documentation on enums in the json spec:
    https://deck.gl/docs/api-reference/json/conversion-reference#enumerations-and-using-the--prefix.

- scale (dict; optional):
    Parameters for the Distance Scale component.

    `scale` is a dict with keys:

    - cssStyle (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
        Scale bar css style can be used for positioning.

    - incrementValue (number; optional):
        Increment value for the scale.

    - visible (boolean; optional):
        Toggle component visibility.

    - widthPerUnit (number; optional):
        Scale bar width in pixels per unit value.

- toolbar (dict; optional):
    Parameters to control toolbar.

    `toolbar` is a dict with keys:

    - visible (boolean; optional):
        Toggle toolbar visibility.

- views (boolean | number | string | dict | list; default {    layout: [1, 1],    showLabel: False,    viewports: [{ id: "main-view", show3D: False, layerIds: [] }],}):
    Views configuration for map. If not specified, all the layers will
    be displayed in a single 2D viewport. Example:      views = {
    \"layout\": [1, 1],          \"showLabel\": False,
    \"viewports\": [              {                  \"id\":
    \"view_1\",                  \"name\"?: \"View 1\"
    \"show3D\"?: False,                  \"layerIds\": [\"layer-ids\"]
    }          ]      }.

- zoom (number; optional):
    Zoom level for the view."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, resources=Component.UNDEFINED, layers=Component.UNDEFINED, bounds=Component.UNDEFINED, zoom=Component.UNDEFINED, views=Component.UNDEFINED, coords=Component.UNDEFINED, scale=Component.UNDEFINED, coordinateUnit=Component.UNDEFINED, toolbar=Component.UNDEFINED, legend=Component.UNDEFINED, colorTables=Component.UNDEFINED, editedData=Component.UNDEFINED, checkDatafileSchema=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'bounds', 'checkDatafileSchema', 'colorTables', 'coordinateUnit', 'coords', 'editedData', 'layers', 'legend', 'resources', 'scale', 'toolbar', 'views', 'zoom']
        self._type = 'DeckGLMap'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'bounds', 'checkDatafileSchema', 'colorTables', 'coordinateUnit', 'coords', 'editedData', 'layers', 'legend', 'resources', 'scale', 'toolbar', 'views', 'zoom']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DeckGLMap, self).__init__(**args)

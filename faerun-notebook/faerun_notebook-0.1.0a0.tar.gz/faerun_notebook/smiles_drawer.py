import ipywidgets as widgets
from traitlets import Unicode, Any, Int, Dict, Bool

# See js/lib/smiles_drawer.js for the frontend counterpart to this file.


@widgets.register
class SmilesDrawer(widgets.DOMWidget):
    """An faerun.js widget."""

    # Name of the widget view class in front-end
    _view_name = Unicode("SmilesDrawerView").tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode("SmilesDrawerModel").tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode("faerun-notebook").tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode("faerun-notebook").tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode("^0.1.0").tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode("^0.1.0").tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    value = Any("").tag(sync=True)
    theme = Unicode("light").tag(sync=True)
    options = Dict({}).tag(sync=True)
    output = Unicode("svg").tag(sync=True)
    border = Bool(True).tag(sync=True)
    background = Unicode("#ffffff").tag(sync=True)

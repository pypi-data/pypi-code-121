import types
import ovito.nonpublic
from . import DislocationVis

# Inject enum types.
DislocationVis.Shading = types.SimpleNamespace()
DislocationVis.Shading.Normal = ovito.nonpublic.ArrowShadingMode.Normal
DislocationVis.Shading.Flat = ovito.nonpublic.ArrowShadingMode.Flat
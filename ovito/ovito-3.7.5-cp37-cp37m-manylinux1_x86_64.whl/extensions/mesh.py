# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.stdobj

# Load the C extension module.
import ovito.plugins.MeshPython

# Register import formats.
ovito.io.import_file._formatTable["stl"] = ovito.nonpublic.STLImporter
ovito.io.import_file._formatTable["obj"] = ovito.nonpublic.WavefrontOBJImporter
ovito.io.import_file._formatTable["vtk/legacy/mesh"] = ovito.nonpublic.VTKFileImporter
ovito.io.import_file._formatTable["vtk/pvd"] = ovito.nonpublic.ParaViewPVDImporter
ovito.io.import_file._formatTable["vtk/vtm"] = ovito.nonpublic.ParaViewVTMImporter
ovito.io.import_file._formatTable["vtk/vtp/mesh"] = ovito.nonpublic.ParaViewVTPMeshImporter

# Register export formats.
ovito.io.export_file._formatTable["vtk/trimesh"] = ovito.nonpublic.VTKTriangleMeshExporter

# Publish classes.
ovito.vis.__all__ += ['SurfaceMeshVis']
ovito.data.__all__ += ['SurfaceMesh']

from ovito.data import DataCollection, SurfaceMesh
from ovito.data.data_objects_dict import DataObjectsDict

# Implementation of the DataCollection.surfaces attribute.
def _DataCollection_surfaces(self):
    """
    Returns a dictionary view providing key-based access to all :py:class:`SurfaceMesh` objects in 
    this data collection. Each :py:class:`SurfaceMesh` has a unique :py:attr:`~ovito.data.DataObject.identifier` key, 
    which can be used to look it up in the dictionary. 
    See the documentation of the modifier producing the surface mesh to find out what the right key is, or use

    .. literalinclude:: ../example_snippets/data_collection_surfaces.py
        :lines: 9-9

    to see which identifier keys exist. Then retrieve the desired :py:class:`SurfaceMesh` object from the collection using its identifier 
    key, e.g.

    .. literalinclude:: ../example_snippets/data_collection_surfaces.py
        :lines: 14-15
    """
    return DataObjectsDict(self, SurfaceMesh)
DataCollection.surfaces = property(_DataCollection_surfaces)

# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.stdobj
import ovito.extensions.stdmod
import ovito.extensions.mesh

# Load the C extension module.
import ovito.plugins.GridPython

# Publish classes.
ovito.vis.__all__ += ['VoxelGridVis']
ovito.modifiers.__all__ += ['CreateIsosurfaceModifier']
ovito.data.__all__ += ['VoxelGrid']

# Register import formats.
ovito.io.import_file._formatTable["vtk/vti/grid"] = ovito.nonpublic.ParaViewVTIGridImporter
ovito.io.import_file._formatTable["vtk/vts/grid"] = ovito.nonpublic.ParaViewVTSGridImporter

# Register export formats.
ovito.io.export_file._formatTable["vtk/grid"] = ovito.nonpublic.VTKVoxelGridExporter

# Load dependencies
from ovito.data import DataCollection, VoxelGrid
from ovito.data.data_objects_dict import DataObjectsDict

# Implementation of the DataCollection.grids attribute.
def _DataCollection_grids(self):
    """
    Returns a dictionary view providing key-based access to all :py:class:`VoxelGrids <VoxelGrid>` in 
    this data collection. Each :py:class:`VoxelGrid` has a unique :py:attr:`~ovito.data.DataObject.identifier` key, 
    which allows you to look it up in this dictionary. To find out which voxel grids exist in the data collection and what 
    their identifiers are, use

    .. literalinclude:: ../example_snippets/data_collection_grids.py
        :lines: 7-7

    Then retrieve the desired :py:class:`VoxelGrid` from the collection using its identifier key, e.g.

    .. literalinclude:: ../example_snippets/data_collection_grids.py
        :lines: 12-13
    """
    return DataObjectsDict(self, VoxelGrid)
DataCollection.grids = property(_DataCollection_grids)
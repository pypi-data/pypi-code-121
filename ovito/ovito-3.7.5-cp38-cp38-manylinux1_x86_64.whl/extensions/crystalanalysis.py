# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.particles
import ovito.extensions.mesh

# Load the C extension module.
import ovito.plugins.CrystalAnalysisPython

# Load class add-ons.
import ovito.modifiers.grain_segmentation_modifier
import ovito.modifiers.elastic_strain_modifier
import ovito.vis.dislocation_vis

# Publish classes.
ovito.vis.__all__ += ['DislocationVis']
ovito.modifiers.__all__ += ['DislocationAnalysisModifier', 'ElasticStrainModifier', 'GrainSegmentationModifier']
ovito.data.__all__ += ['DislocationNetwork', 'DislocationSegment']

# Register import formats.
ovito.io.import_file._formatTable["ca"] = ovito.nonpublic.CAImporter
ovito.io.import_file._formatTable["paradis"] = ovito.nonpublic.ParaDiSImporter

# Register export formats.
ovito.io.export_file._formatTable["ca"] = ovito.nonpublic.CAExporter
ovito.io.export_file._formatTable["vtk/disloc"] = ovito.nonpublic.VTKDislocationsExporter

from ovito.data import DataCollection, DislocationNetwork

# Implementation of the DataCollection.dislocations attribute.
def _DataCollection_dislocations(self):
    """
    Returns the :py:class:`DislocationNetwork` data object; or ``None`` if there 
    is no object of this type in the collection. Typically, the :py:class:`DislocationNetwork` is created by a :ref:`pipeline <modifiers_overview>`
    containing the :py:class:`~ovito.modifiers.DislocationAnalysisModifier`.
    """
    return self._find_object_type(DislocationNetwork)
DataCollection.dislocations = property(_DataCollection_dislocations)

# Returns a mutable version of the DislocationNetwork object.
DataCollection.dislocations_ = property(lambda self: self.make_mutable(self.dislocations))

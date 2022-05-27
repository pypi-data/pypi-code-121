# Load dependencies.
import ovito.extensions.pyscript

# Load the C extension module.
import ovito.plugins.StdObjPython

# Load class add-ons.
import ovito.data.data_table
import ovito.data.property_class
import ovito.data.property_container
import ovito.data.simulation_cell

# Publish classes.
ovito.data.__all__ += ['SimulationCell', 'Property', 'PropertyContainer', 'DataTable', 'ElementType']
ovito.vis.__all__ += ['SimulationCellVis']

# Register export formats.
ovito.io.export_file._formatTable["txt/table"] = ovito.nonpublic.DataTableExporter
# For backward compatibility with older development versions of OVITO:
ovito.io.export_file._formatTable["txt/series"] = ovito.nonpublic.DataTableExporter

from ovito.data import DataCollection, DataTable, SimulationCell
from ovito.data.data_objects_dict import DataObjectsDict

# Implementation of the DataCollection.tables attribute.
def _DataCollection_tables(self):
    """
    A dictionary view of all :py:class:`DataTable` objects in
    this data collection. Each :py:class:`DataTable` has a unique :py:attr:`~ovito.data.DataObject.identifier` key, 
    which can be used to look it up in this dictionary. You can use

    .. literalinclude:: ../example_snippets/data_collection_tables.py
        :lines: 9-9

    to find out which table identifiers exist in the dictionary. Modifiers that generate a data table typically 
    assign a predefined identifier, which can be found in their documentation.
    Use the key string to retrieve the desired :py:class:`DataTable` from the dictionary, e.g.

    .. literalinclude:: ../example_snippets/data_collection_tables.py
        :lines: 14-15

    """
    return DataObjectsDict(self, DataTable)
DataCollection.tables = property(_DataCollection_tables)

# Implementation of the DataCollection.cell attribute.
def _DataCollection_cell(self):
    """ 
    Returns the :py:class:`SimulationCell` data object describing the cell vectors and periodic boundary
    condition flags. It may be ``None``. 

    .. important::

        The :py:class:`SimulationCell` data object returned by this attribute may be marked as read-only, 
        which means your attempts to modify the cell object will raise a Python error.
        This is typically the case if the data collection was produced by a pipeline and its objects are owned by the system.
        
    If you intend to modify the :py:class:`SimulationCell` data object within this data collection, use the :py:attr:`!cell_` 
    attribute instead to explicitly request a mutable version of the cell object. See topic :ref:`underscore_notation` for more information.
    Use :py:attr:`!cell` for read access and :py:attr:`!cell_` for write access, e.g. ::

        print(data.cell.volume)
        data.cell_.pbc = (True,True,False)

    To create a :py:class:`SimulationCell` in a data collection that might not have a simulation cell yet, use the 
    :py:meth:`create_cell` method or simply assign a new instance of the :py:class:`SimulationCell` class to the :py:attr:`!cell` attribute.
    """
    return self._find_object_type(SimulationCell)
# Implement the assignment of a SimulationCell object to the DataCollection.cell field.
def _DataCollection_set_cell(self, obj):
    assert(obj is None or isinstance(obj, SimulationCell)) # Must assign a SimulationCell data object to this field.
    # Check if there already is an existing SimulationCell object in the DataCollection. 
    # If yes, first remove it from the collection before adding the new one. 
    existing = self._find_object_type(SimulationCell)
    if existing is not obj:
        if not existing is None: self.objects.remove(existing)
        if not obj is None: self.objects.append(obj)
DataCollection.cell = property(_DataCollection_cell, _DataCollection_set_cell)

# Implementation of the DataCollection.cell_ attribute.
DataCollection.cell_ = property(lambda self: self.make_mutable(self.cell), _DataCollection_set_cell)

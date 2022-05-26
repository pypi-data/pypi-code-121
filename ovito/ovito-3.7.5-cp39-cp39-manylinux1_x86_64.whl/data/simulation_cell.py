from __future__ import annotations
import numpy
from . import SimulationCell, DataCollection
from .ovito_ndarray_adapter import add_ndarray_interface

# Give the SimulationCell class a Numpy-like interface.
add_ndarray_interface(SimulationCell)

# Implementation of the SimulationCell.pbc property.
def _get_SimulationCell_pbc(self):
    """ A tuple of three Boolean flags specifying whether periodic boundary conditions are enabled along the 
        cell's three spatial directions. 

        :Default: ``(False, False, False)``
    """
    return (self.pbc_x, self.pbc_y, self.pbc_z)

def _set_SimulationCell_pbc(self, flags):
    assert(len(flags) == 3) # Expected an array with three Boolean flags.
    self.pbc_x = flags[0]
    self.pbc_y = flags[1]
    self.pbc_z = flags[2]

SimulationCell.pbc = property(_get_SimulationCell_pbc, _set_SimulationCell_pbc)

# Implementation of the SimulationCell.delta_vector() method.
def _SimulationCell_delta_vector(self, ra, rb, return_pbcvec=False):
    """
    Computes the vector connecting two points :math:`r_a` and :math:`r_b` in a periodic simulation cell by applying the minimum image convention.

    The method starts by computing the 3d vector :math:`{\Delta} = r_b - r_a` for two points :math:`r_a` and :math:`r_b`, which may be located in different images
    of the periodic simulation cell. The `minimum image convention <https://en.wikipedia.org/wiki/Periodic_boundary_conditions>`_
    is then applied to obtain the new vector :math:`{\Delta'} = r_b' - r_a`, where the original point :math:`r_b` has been replaced by the periodic image
    :math:`r_b'` that is closest to :math:`r_a`, making the vector :math:`{\Delta'}` as short as possible (in reduced coordinate space).
    :math:`r_b'` is obtained by translating :math:`r_b` an integer number of times along each of the three cell directions:
    :math:`r_b' = r_b - H*n`, with :math:`H` being the 3x3 cell matrix and :math:`n` being a vector of three integers that are chosen by the
    method such that :math:`r_b'` is as close to :math:`r_a` as possible.

    Note that the periodic image convention is applied only along those cell directions for which
    periodic boundary conditions are enabled (see :py:attr:`pbc` property). For other directions
    no shifting is performed, i.e., the corresponding components of :math:`n = (n_x,n_y,n_z)` will always be zero.

    The method is able to compute the results for either an individual pair of input points or for two *arrays* of input points. In the latter case,
    i.e. if the input parameters *ra* and *rb* are both 2-D arrays of shape *Nx3*, the method returns a 2-D array containing
    *N* output vectors. This allows applying the minimum image convention to a large number of point pairs in one function call.

    The option *return_pbcvec* lets the method return the vector :math:`n` introduced above as an additional output.
    The components of this vector specify the number of times the image point :math:`r_b'` needs to be shifted along each of the three cell directions
    in order to bring it onto the original input point :math:`r_b`. In other words, it specifies the number of times the
    computed vector :math:`{\Delta} = r_b - r_a` crosses a periodic boundary of the cell (either in positive or negative direction).
    For example, the PBC shift vector :math:`n = (1,0,-2)` would indicate that, in order to get from input point :math:`r_a` to input point :math:`r_b`, one has to cross the
    cell boundaries once in the positive x-direction and twice in the negative z-direction. If *return_pbcvec* is True,
    the method returns the tuple (:math:`{\Delta'}`, :math:`n`); otherwise it returns just :math:`{\Delta'}`.
    Note that the vector :math:`n` computed by this method can be used, for instance, to correctly initialize the :py:attr:`Bonds.pbc_vectors <ovito.data.Bonds.pbc_vectors>`
    property for newly created bonds that cross a periodic cell boundary.

    :param ra: The Cartesian xyz coordinates of the first input point(s). Either a 1-D array of length 3 or a 2-D array of shape (*N*,3).
    :param rb: The Cartesian xyz coordinates of the second input point(s). Must have the same shape as *ra*.
    :param bool return_pbcvec: If True, also returns the vector :math:`n`, which specifies how often the vector :math:`(r_b' - r_a)` crosses the periodic cell boundaries.
    :returns: The vector :math:`{\Delta'}` and, optionally, the vector :math:`n`.

    Note that there exists also a convenience method :py:meth:`Particles.delta_vector() <ovito.data.Particles.delta_vector>`,
    which should be used in situations where :math:`r_a` and :math:`r_b` are the coordinates of two particles in the simulation cell.
    """
    return self._delta_vector(rb - ra, return_pbcvec)
SimulationCell.delta_vector = _SimulationCell_delta_vector

# Implementation of the DataCollection.create_cell() method.
def _DataCollection_create_cell(self, matrix, pbc = (True, True, True), vis_params = None):
    """
    This convenience method conditionally creates a new :py:class:`~ovito.data.SimulationCell` object and stores it in this data collection. 
    If a simulation cell already existed in the collection (:py:attr:`.cell` is not ``None``), then that cell object is
    replaced with a :ref:`modifiable copy <data_ownership>` if necessary and the matrix and PBC flags are set to the given values. 
    The attached :py:class:`~ovito.vis.SimulationCellVis` element is maintained in this case. 
    
    :param matrix: A 3x4 array to initialize the cell matrix with. It specifies the three cell vectors and the origin.
    :param pbc: A tuple of three Booleans specifying the cell's :py:attr:`~SimulationCell.pbc` flags.
    :param Mapping[str, Any] vis_params: Optional dictionary to initialize attributes of the attached :py:class:`~ovito.vis.SimulationCellVis` element (only used if the cell object is newly created by the method).
    :rtype: ovito.data.SimulationCell
    
    The logic of this method is roughly equivalent to the following code::
    
        def create_cell(data: DataCollection, matrix, pbc, vis_params=None) -> SimulationCell:
            if data.cell is None:
                data.cell = SimulationCell(pbc=pbc)
                data.cell[...] = matrix
                data.cell.vis.line_width = <...> # Some value that scales with the cell's size
                if vis_params:
                    for name, value in vis_params.items(): setattr(data.cell.vis, name, value)
            else:
                data.cell_[...] = matrix
                data.cell_.pbc = pbc
            return data.cell_
    """
    return SimulationCell._create(self, matrix, pbc, vis_params)
DataCollection.create_cell = _DataCollection_create_cell

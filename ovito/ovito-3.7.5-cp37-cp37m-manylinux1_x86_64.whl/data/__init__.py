"""
This Python module defines various data object types, which are produced and processed within OVITO's data pipeline system.
It also provides the :py:class:`DataCollection` class as a container for such data objects as well as several utility classes for
computing neighbor lists and iterating over the bonds of connected to a particle.

**Data containers:**

  * :py:class:`DataObject` (base of all data object types in OVITO)
  * :py:class:`DataCollection` (a general container for data objects representing an entire dataset)
  * :py:class:`PropertyContainer` (manages a set of uniform :py:class:`Property` arrays)
  * :py:class:`Particles` (a specialized :py:class:`PropertyContainer` for particles)
  * :py:class:`Bonds` (a specialized :py:class:`PropertyContainer` for bonds)
  * :py:class:`VoxelGrid` (a specialized :py:class:`PropertyContainer` for 2d and 3d volumetric grids)
  * :py:class:`DataTable` (a specialized :py:class:`PropertyContainer` for tabulated data)
  * :py:class:`TrajectoryLines` (a set of particle trajectory lines)

**Data objects:**

  * :py:class:`Property` (holds per-data-element property values)
  * :py:class:`SimulationCell` (simulation box geometry and boundary conditions)
  * :py:class:`SurfaceMesh` (polyhedral mesh representing the boundaries of spatial regions)
  * :py:class:`TriangleMesh` (general mesh structure made of vertices and triangular faces)
  * :py:class:`DislocationNetwork` (set of discrete dislocation lines with Burgers vector information)

**Auxiliary data objects:**

  * :py:class:`ElementType` (base class for element type definitions)
  * :py:class:`ParticleType` (describes a single particle or atom type)
  * :py:class:`BondType` (describes a single bond type)
  * :py:class:`DislocationSegment` (a dislocation line in a :py:class:`DislocationNetwork`)

**Utility classes:**

  * :py:class:`CutoffNeighborFinder` (finds neighboring particles within a cutoff distance)
  * :py:class:`NearestNeighborFinder` (finds *N* nearest neighbor particles)
  * :py:class:`BondsEnumerator` (lets you efficiently iterate over the bonds connected to a particle)

"""

__all__ = ['DataCollection', 'DataObject', 'TriangleMesh']

from typing import Generator
import ovito.nonpublic
from . import SimulationCell, DataCollection

class CutoffNeighborFinder(ovito.nonpublic.CutoffNeighborFinder):
    """ 
    A utility class that computes particle neighbor lists.
    
    This class lets you iterate over all neighbors of a particle that are located within a specified spherical cutoff.
    You can use it to build neighbors lists or perform computations that require neighbor vector information.
    
    The constructor takes a positive cutoff radius and a :py:class:`DataCollection <ovito.data.DataCollection>` 
    providing the input particles and the :py:class:`~ovito.data.SimulationCell` (needed for periodic systems).
    
    Once the :py:class:`!CutoffNeighborFinder` has been constructed, you can call its :py:meth:`.find` method to 
    iterate over the neighbors of a particle, for example:
    
    .. literalinclude:: ../example_snippets/cutoff_neighbor_finder.py
    
    Note: In case you rather want to determine the *N* nearest neighbors of a particle,
    use the :py:class:`NearestNeighborFinder` class instead.
    """
        
    def __init__(self, cutoff: float, data_collection: DataCollection) -> None:
        """ This is the constructor. """
        super(self.__class__, self).__init__()
        if data_collection.particles is None or data_collection.particles.positions is None:
            raise KeyError("DataCollection does not contain any particles.")
        pos_property = data_collection.particles.positions
        self.particle_count = len(pos_property)
        if not self.prepare(cutoff, pos_property, data_collection.cell):
            raise RuntimeError("Operation has been canceled by the user.")
        
    def find(self, index: int):
        """ 
        Returns an iterator over all neighbors of the given particle.
         
        :param int index: The zero-based index of the central particle whose neighbors should be enumerated.
        :returns: A Python iterator that visits all neighbors of the central particle within the cutoff distance. 
                  For each neighbor the iterator returns an object with the following property fields:
                  
                      * **index**: The zero-based global index of the current neighbor particle.
                      * **distance**: The distance of the current neighbor from the central particle.
                      * **distance_squared**: The squared neighbor distance.
                      * **delta**: The three-dimensional vector connecting the central particle with the current neighbor (taking into account periodicity).
                      * **pbc_shift**: The periodic shift vector, which specifies how often each periodic boundary of the simulation cell is crossed when going from the central particle to the current neighbor.
        
        The `index` value returned by the iterator can be used to look up properties of the neighbor particle as demonstrated in the example above.
        
        Note that all periodic images of particles within the cutoff radius are visited. Thus, the same particle index may appear multiple times in the neighbor
        list of the central particle. In fact, the central particle may be among its own neighbors in a small periodic simulation cell.
        However, the computed vector (``delta``) and PBC shift (``pbc_shift``) will be unique for each visited image of the neighbor particle.
        """
        if index < 0 or index >= self.particle_count:
            raise IndexError("Particle index is out of range.")
        # Construct the C++ neighbor query. 
        query = ovito.nonpublic.CutoffNeighborFinder.Query(self, int(index))
        # Iterate over neighbors.
        while not query.at_end:
            yield query
            query.next()

    def find_at(self, coords):
        """ 
        Returns an iterator over all particles located within the spherical range of the given center position. In contrast to :py:meth:`find` this method can search for neighbors around arbitrary 
        spatial locations, which don't have to coincide with any physical particle position.
         
        :param coords: A (x,y,z) coordinate triplet specifying the center location around which to search for particles.
        :returns: A Python iterator enumerating all particles within the cutoff distance. 
                  For each neighbor the iterator returns an object with the following properties:
                  
                      * **index**: The zero-based global index of the current neighbor particle.
                      * **distance**: The distance of the current particle from the center position.
                      * **distance_squared**: The squared distance.
                      * **delta**: The three-dimensional vector from the center to the current neighbor (taking into account periodicity).
                      * **pbc_shift**: The periodic shift vector, which specifies how often each periodic boundary of the simulation cell is crossed when going from the center point to the current neighbor.
        
        The index value returned by the iterator can be used to look up properties of the neighbor particle as demonstrated in the example above.
        
        Note that all periodic images of particles within the cutoff radius are visited. Thus, the same particle index may appear multiple times in the neighbor list. 
        However, the computed vector (``delta``) and image offset (``pbc_shift``) will be unique for each visited image of a neighbor particle.
        """
        # Construct the C++ neighbor query. 
        query = ovito.nonpublic.CutoffNeighborFinder.Query(self, coords)
        # Iterate over neighbors.
        while not query.at_end:
            yield query
            query.next()            

    # Inherit method neighbor_distances() from C++ base class.
    neighbor_distances = ovito.nonpublic.CutoffNeighborFinder.neighbor_distances

    # Inherit method neighbor_vectors() from C++ base class.
    neighbor_vectors = ovito.nonpublic.CutoffNeighborFinder.neighbor_vectors

ovito.data.CutoffNeighborFinder = CutoffNeighborFinder
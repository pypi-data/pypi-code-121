import ovito.nonpublic

class NearestNeighborFinder(ovito.nonpublic.NearestNeighborFinder):
    """
    A utility class that finds the *N* nearest neighbors of a particle. 

    .. seealso::
    
      To find all neighbors within a spherical cutoff region around another particle, 
      use :py:class:`CutoffNeighborFinder` instead.

    The constructor takes the requested number of nearest neighbors, *N*, and a :py:class:`DataCollection <ovito.data.DataCollection>`
    containing the input particles and the optional simulation cell.
    *N* must be a positive integer not greater than 64, which is the built-in maximum of neighbors supported by this class.

    .. note::

      Keep in mind that, if the system contains only *N* particles or less, and if the simulation does not use periodic boundary conditions, then the 
      neighbor finder will return less than the requested number of nearest neighbors.

    Once the :py:class:`!NearestNeighborFinder` has been initialized, you can call its :py:meth:`.find` method to
    iterate over the sorted list of nearest neighbors of a given central particle:

    .. literalinclude:: ../example_snippets/nearest_neighbor_finder.py
       :lines: 11-21

    In addition, the class provides the :py:meth:`find_at` method, which determines the *N* nearest particles around some
    arbitrary spatial location:

    .. literalinclude:: ../example_snippets/nearest_neighbor_finder.py
       :lines: 26-29

    """

    def __init__(self, N, data_collection):
        """ Initializes the neighbor finder facility. """
        super(self.__class__, self).__init__(N)
        if N<=0 or N>64:
            raise ValueError("The requested number of nearest neighbors is out of range. N must be a positive integer not greater than 64.")
        if data_collection.particles is None or data_collection.particles.positions is None:
            raise KeyError("DataCollection does not contain any particles.")
        pos_property = data_collection.particles.positions
        self.particle_count = data_collection.particles.count
        self.prepare(pos_property, data_collection.cell)

    def find(self, index):
        """
        Returns an iterator that visits the *N* nearest neighbors of the given particle in order of ascending distance.

        :param int index: The zero-based index of the central particle whose neighbors should be determined.
        :returns: A Python iterator that visits the *N* nearest neighbors of the central particle in order of ascending distance.
                  For each neighbor being visited, the iterator returns an object having the following attributes:

                      * **index**: The global index of the current neighbor particle.
                      * **distance**: The distance of the current neighbor from the central particle.
                      * **distance_squared**: The squared neighbor distance.
                      * **delta**: The three-dimensional vector connecting the central particle with the current neighbor (correctly taking into account periodic boundary conditions).

        The index can be used to look up properties of the neighbor particle as demonstrated in the first example code above.

        Note that several periodic images of the same particle may be visited if the periodic simulation cell is sufficiently small.
        Then the same particle index will appear more than once in the neighbor list. In fact, the central particle may be among its own neighbors in a sufficiently small periodic simulation cell.
        However, the computed neighbor vector (`delta`) will be unique for each image of a neighboring particle.

        The number of neighbors actually visited may be smaller than the requested number, *N*, if the
        system contains too few particles and is non-periodic.

        Note that the :py:meth:`!find()` method will not find other particles located exactly at the same spatial position as the central particle for technical reasons.
        To find such particles too, which are positioned exactly on top of each other, use :py:meth:`.find_at` instead.
        """
        if index < 0 or index >= self.particle_count:
            raise IndexError("Particle index is out of range.")
        # Construct the C++ neighbor query.
        query = ovito.nonpublic.NearestNeighborFinder.Query(self)
        query.findNeighbors(int(index))
        # Iterate over neighbors.
        for i in range(query.count):
            yield query[i]

    def find_at(self, coords):
        """
        Returns an iterator that visits the *N* nearest particles around a spatial point given by *coords* in order of ascending distance.
        Unlike the :py:meth:`find` method, which queries the nearest neighbors of a physical particle, :py:meth:`!find_at` allows
        searching for nearby particles at arbitrary locations in space.

        :param coords: A coordinate triplet (x,y,z) specifying the spatial location where the *N* nearest particles should be queried.
        :returns: A Python iterator that visits the *N* nearest neighbors in order of ascending distance.
                  For each visited particle the iterator returns an object with the following attributes:

                      * **index**: The index of the current particle (starting at 0).
                      * **distance**: The distance of the current neighbor from the query location.
                      * **distance_squared**: The squared distance to the query location.
                      * **delta**: The three-dimensional vector from the query point to the current particle (correctly taking into account periodic boundary conditions).

        If there is a particle located exactly at the query location *coords*, it will be among the returned neighbors.
        This is in contrast to the :py:meth:`find` function, which skips the central particle itself.

        The number of neighbors actually visited may be smaller than the requested number, *N*, if the
        system contains too few particles and is non-periodic.
        """
        # Construct the C++ neighbor query.
        query = ovito.nonpublic.NearestNeighborFinder.Query(self)
        query.findNeighborsAtLocation(coords, True)
        # Iterate over neighbors.
        for i in range(query.count):
            yield query[i]

    def find_all(self, indices = None):
        """
        Finds the *N* nearest neighbors of each particle in the system or of the subset of particles specified by *indices*. 
        This is the batch-processing version of :py:meth:`find`, allowing you to efficiently compute the neighbor lists and neighbor vectors of several 
        particles at once, without explicit for-loop and by making use of all parallel processor cores. 

        The method returns two NumPy arrays:

        ``neigh_idx`` : NumPy array of shape (*M*, *N*) storing the indices of neighbor particles, 
        with *M* equal to *len(indices)* or, if *indices* is *None*, the total number of particles in the system. 
        *N* refers to the number of nearest neighbors requested in the :py:class:`NearestNeighborFinder` constructor. 
        The computed indices in this array can be used to look up properties of neighbor particles in the global :py:class:`Particles` object.

        ``neigh_vec`` : NumPy array of shape (*M*, *N*, 3) storing the xyz components of the three-dimensional neighbor vectors ("delta"), 
        which connect the *M* central particles with their *N* respective nearest neighbors. 

        :param indices: List of zero-based particle indices for which the neighbor lists should be computed. 
                        If left unspecified, neighbor lists will be computed for every particle in the system.
        :returns: ``(neigh_idx, neigh_vec)``

        .. tip::

           To compute all pair-wise distances in one go, i.e. the 2-norms of the neighbor vectors, you can do::

              distances = numpy.linalg.norm(neigh_vec, axis=2)   # Yields (M,N) array of neighbor distances

        """
        return super().find_all(indices)

ovito.data.NearestNeighborFinder = NearestNeighborFinder
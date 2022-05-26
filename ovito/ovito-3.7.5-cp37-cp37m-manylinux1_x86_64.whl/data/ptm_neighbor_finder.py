import ovito.nonpublic
from ovito.data import DataCollection

class PTMNeighborFinder(ovito.nonpublic.PTMNeighborFinder):

    def __init__(self, data_collection: DataCollection) -> None:
        """ Initializes the neighbor finder facility. """
        super(self.__class__, self).__init__(False)

        if data_collection.particles is None or data_collection.particles.positions is None:
            raise ValueError("DataCollection does not contain any particles.")
        
        if not 'Structure Type' in data_collection.particles or not 'Orientation' in data_collection.particles or not 'Correspondences' in data_collection.particles:
            raise RuntimeError("PTM results not found in DataCollection. "
                "Please add a PolyhedralTemplateMatchingModifier to the upstream pipeline and let it compute the local lattice orientations. "
                "PTMNeighborFinder requires the particle properties 'Structure Type', 'Orientation', and 'Correspondences' as input.")
        
        # Store the number of input particles, because we'll need it in the find() method.
        self.particle_count = data_collection.particles.count

        # Initialize the PTMNeighborFinder data structures, including those of the internal NearestNeighborFinder.
        self.prepare(
            data_collection.particles['Position'], 
            data_collection.particles['Structure Type'], 
            data_collection.particles['Orientation'], 
            data_collection.particles['Correspondences'], 
            data_collection.cell)

    def find(self, index: int):
        """
        Returns an iterator that visits the nearest neighbors of the given particle in a prescribed order.

        :param int index: The zero-based index of the central particle whose neighbors should be enumerated.
        :returns: A Python iterator that visits the immediate neighbors of the central particle in order.
                  For each visited neighbor the iterator returns an object having the following attributes:

                      * **index**: The index of the current neighbor particle in the global particles list.
                      * **distance**: The distance of the current neighbor from the central particle.
                      * **distance_squared**: The squared neighbor distance.
                      * **delta**: The three-dimensional vector connecting the central particle with the current neighbor (correctly taking into account periodic boundary conditions).
                      * **idealvec**: The ideal lattice vector corresponding to the current neighbor, expressed in the coordinate frame of the PTM template structure. 

        """
        if index < 0 or index >= self.particle_count:
            raise IndexError("Particle index is out of range.")
        # Construct the C++ query object.
        query = ovito.nonpublic.PTMNeighborFinder.Query(self)
        query.find_neighbors(int(index), None)
        # Iterate over neighbors.
        for i in range(query.count):
            yield query[i]

ovito.data.PTMNeighborFinder = PTMNeighborFinder
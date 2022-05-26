from copy import deepcopy

import numpy as np

from nbodysim import nmath as nm
from nbodysim.exceptions import *

class NBody:
    """
    Class used to simulate the n-body problem.
    """
    def __init__(self, init_positions, init_velocities, masses, collision_tolerance = 10e-4, escape_tolerance = -1):
        """
        :param init_positions: Python list or numpy array of position vectors for the bodies
        :param init_velocities: Python list or numpy array of velocity vectors for the bodies
        :param masses: Python list or numpy array of the mass of each body
        :param collision_tolerance: maximum distance between 2 bodies allowed before ending simulation
               If None, collisions are not considered.
        :param escape_tolerance: maximum distance away from the centre of mass (COM) allowed before ending simulation
                                 If None, escape_tolerance is automatically calculated
                                 If -1, escape_tolerance is not considered
        """

        # number of bodies in simulation
        self.n = len(init_positions)

        # ensures that input is correctly formatted (in terms of shape & data type)
        self.check_update_input(init_positions, init_velocities, masses)

        self.G = 1#6.67408e-11
        self.collision_tolerance = collision_tolerance

        if escape_tolerance is None:
            # escape tolerance set as 10 times the maximum distance of any body from the COM
            self.escape_tolerance = np.max(nm.ten_norm(self.positions, sqrt = True, axis = 1)) * 10 # can be altered
        else:
            self.escape_tolerance = escape_tolerance

        # total mass of simulation
        self.total_mass = np.sum(self.masses)

        # keep masses as stacked array aswell (convenient for calculations)
        self.stacked_masses = np.vstack(self.masses)

        # calculate COM and linear momentum of initial system
        self.com = self.get_com()
        self.linear_momentum = self.get_lmomentum()
        self.total_linear_momentum = np.sum(self.linear_momentum, axis=0)

        # change to COM coordinates (COM becomes the origin, COM moves at constant velocity)
        self.positions = self.positions - self.com
        self.velocities = self.velocities - (self.total_linear_momentum)/self.total_mass

        # compute a tensor (nxnx3) with entry (i,j) corresponding to the distance vector between the ith and jth body
        self.distances = np.zeros(shape = (self.n, self.n, 3))
        self.get_body_distances()

        # recalculate properties of the system based on COM coordinates
        # linear momentum, total linear momentum, angular momentum, total angular momentum,
        # kinetic energy, gravitational potential energy (GPE) and total energy
        self.linear_momentum = self.get_lmomentum()
        self.total_linear_momentum = np.sum(self.linear_momentum, axis=0)
        self.angular_momentum = self.get_amomentum()
        self.total_angular_momentum = np.sum(self.angular_momentum, axis = 0)
        self.kinetic_energy = 0
        self.gpe = 0
        self.energy = self.get_energy()

        # save the initial energy and momentum values (test for conservation)
        self.first_energy = self.energy
        self.first_angular_momentum = self.total_angular_momentum
        self.first_linear_momentum = self.total_linear_momentum

    def check_update_input(self, init_positions, init_velocities, masses):
        """
        Checks that class initialisation has been done with correct parameters
        Ensures that positions, velocities and masses all have the same number of elements
        Ensure that positions and velocities are matrices of shape (n x 3)
        Lastly, ensures that position, velocity and mass tensors are numpy arrays
        """

        # check: same number of bodies as elements in the position, velocity and mass tensors
        assert (self.n == len(init_velocities) and self.n == len(masses)), \
            f"{self.n} positions given; {len(init_velocities)} velocities given; \
                        {len(masses)} masses given. These 3 quantities must be the same."

        # check: vectors are in R^3
        assert (len(init_positions[0]) == 3 and len(init_velocities[0]) == 3)

        # if parameters are Python lists, change to numpy arrays
        # then, set positions, velocities and masses for the simulation

        if (not isinstance(init_positions, np.ndarray)):
            self.positions = np.array(init_positions)
        else:
            self.positions = init_positions

        if (not isinstance(init_velocities, np.ndarray)):
            self.velocities = np.array(init_velocities)
        else:
            self.velocities = init_velocities

        if (not isinstance(masses, np.ndarray)):
            self.masses = np.array(masses)
        else:
            self.masses = masses

    def get_body_distances(self, positions = None):
        """
        Computes the direction vector from all bodies in an n-body system,
        storing them in a tensor of dimensions (n x n x 3),
        where entry (i,j) contains the direction vector from body i to body j.
        :param positions: the positions of a system of bodies. If None, uses the positions within the simulation.
        :return: if positions is not None, a tensor with the distance vectors between the positions
        """

        if positions is None:
            # itereate over the upper triangular section of the tensor
            for i in range(self.n):
                for j in range(i):
                    # compute distance vector using simulation positions
                    distance_vec = self.positions[j] - self.positions[i]

                    if self.collision_tolerance is not None:
                        # check: no body violates the collision_tolerance distance
                        check_exception(nm.ten_norm(distance_vec, axis = 0, sqrt = True) >= self.collision_tolerance,
                                        BodyCollisionException,
                                        f"A collision occurred. Distance between bodies was {nm.ten_norm(distance_vec, axis=0, sqrt=True)}, but the collision distance is {self.collision_tolerance}.")

                    self.distances[i,j] = distance_vec

                    # direction vector (i,j) is the negative of direction vector (j,i)
                    self.distances[j,i] = -distance_vec
        else:
            # compute the number of bodies & create a corresponding tesnor to store the distance vectors
            n = len(positions)
            distances = np.zeros(shape = (n, n, 3))

            # itereate over the upper triangular section of the tensor
            for i in range(n):
                for j in range(i):
                    # compute distance vector using positions given as arguments
                    distance_vec = positions[j] - positions[i]

                    if self.collision_tolerance is not None:
                        # check: no body violates the collision_tolerance distance
                        if self.collision_tolerance is not None:
                            # check: no body violates the collision_tolerance distance
                            check_exception(nm.ten_norm(distance_vec, axis=0, sqrt=True) >= self.collision_tolerance,
                                            BodyCollisionException,
                                            f"A collision occurred. Distance between bodies was {nm.ten_norm(distance_vec, axis=0, sqrt=True)}, but the collision distance is {self.collision_tolerance}.")

                    distances[i, j] = distance_vec

                    # direction vector (i,j) is the negative of direction vector (j,i)
                    distances[j, i] = -distance_vec

            return distances

    def get_com(self):
        """
        Calculates the COM of the system
        :return: a position vector in 3D for the COM of the system
        """

        com = np.sum(self.stacked_masses * self.positions, axis = 0)/self.total_mass

        return com

    def get_lmomentum(self):
        """
        Calculates the linear momentum (product of mass and velocity) of each body in the system
        :return: an (n x 3) matrix, with the linear momentum of body i at entry i
        """

        lmomentum = self.stacked_masses * self.velocities

        return lmomentum

    def get_amomentum(self):
        """
        Calculates the angular momentum (cross product of position and linear momentum) of each element of the system
        :return: an (n x 3) matrix, with the angular momentum of body i at entry i
        """

        amomentum = nm.mat_cross(self.positions, self.linear_momentum)

        return amomentum

    def get_energy(self):
        """
        Calculates the total energy of the system
        :return: the total energy of the system, given as the sum of kinetic and GPE
        """

        # calculate the total kinetic energy of the system
        kinetic_energy = np.sum(nm.ten_norm(self.linear_momentum, axis = 1, sqrt = False) / (2 * self.masses))
        self.kinetic_energy = kinetic_energy

        # calculate the total GPE of the system
        gpe = 0

        for i in range(self.n):
            for j in range(i):
                gpe += (self.masses[i]*self.masses[j]) / nm.ten_norm(self.distances[i, j], axis = 0)

        gpe *= (-self.G)
        self.gpe = gpe

        return kinetic_energy + gpe

    def get_acceleration(self, positions = None):
        """
        Calculates the acceleration of every particle of a system - solely dependent on position
        :param positions: if None, calculates acceleration based on positions of the system;
                          otherwise, uses positions passed as argument to perform calculation
        :return: an (n x 3) matrix, with each entry i corresponding to the acceleration of o body i
        """

        # calculate the magnitude of the distances between bodies
        if positions is None:
            inv_dist_mag3 = nm.ten_norm(self.distances, axis = 2, sqrt = False)
        else:
            distances = self.get_body_distances(positions = positions)
            inv_dist_mag3 = nm.ten_norm(distances, axis=2, sqrt=False)
        # to avoid division by 0 error, and to avoid unnecessary computational costs,
        # any distance which is 0 is set to infinity, so when reciprocating, the magnitude of the force becomes 0
        inv_dist_mag3[inv_dist_mag3 == 0] = np.inf

        # exponentiate; calculates 1/(magnitude of distance)^3
        inv_dist_mag3 = inv_dist_mag3**(-1.5)

        # tensor, with entry (i,j) giving a unit vector for the direction of the force felt by i due to j
        if positions is None:
            acc_direction = inv_dist_mag3[:,:,np.newaxis] * self.distances
            self.acc_direction = acc_direction
        else:
            acc_direction = inv_dist_mag3[:, :, np.newaxis] * distances

        # calculate the acceleration felt by each body, storing in (n x 3) matrix
        acceleration = np.zeros(shape = (self.n, 3))

        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    acceleration[i] += self.masses[j] * acc_direction[i, j]

        acceleration *= self.G

        return acceleration

    def conserved_quantity(self, new_value, old_value, tolerance):
        """
        Checks that a quantity is conserved across iterations of the simulation (within a given tolerance)
        :param new_value: newly calculated quantity
        :param old_value: quantity to which new_value is compared to for conservation
        :param tolerance: allowed absolute difference between new_value and old_value
        :return: True if old_value is within tolerance of new_value
        """

        return (np.abs(new_value - old_value) < tolerance).all()

    def update(self, new_positions, new_velocities, symplectic = True, tolerance = 10e-3):
        """
        Updates the simulation, given newly calculated positions and distances.
        :param new_positions: positions to update the system with (as a Python list or numpy array of dimension (n x 3)
        :param new_velocities: velocities to update the system with (as a Python list or numpy array of dimension (n x 3)
        :param symplectic: if symplectic is True, check that calculated quantities (energy, angular momentum, linear momentum) are conserved
        :param tolerance: allowed absolute error for determining conservation of calculated quantities
        """

        # check: same number of bodies as elements in the position and velocity
        assert (self.n == len(new_positions) and self.n == len(new_velocities)), \
            f"{len(new_positions)} positions given; {len(new_velocities)} velocities given; \
                                    These 2 quantities must be the same."

        # check: vectors are in R^3
        assert (len(new_positions[0]) == 3 and len(new_velocities[0]) == 3)

        # check: no bodies gone beyond escape_tolerance
        if self.escape_tolerance != -1:
            check_exception((nm.ten_norm(new_positions, sqrt = True, axis = 1) <= self.escape_tolerance).all(),
                            BodyEscapeException,
                            "A body escaped beyond the allowed distance from the COM.")

        # if positions and velocities have the correct format, update them
        # also recalculate all the distances between the bodies
        self.positions = new_positions
        self.velocities = new_velocities
        self.get_body_distances()

        # calculate new linear momentum (used for kinetic energy and angular momentum calculation)
        new_linear_momentum = self.get_lmomentum()

        new_total_linear_momentum = np.sum(new_linear_momentum, axis = 0)

        self.linear_momentum = new_linear_momentum
        self.total_linear_momentum = new_total_linear_momentum

        # calculate new angular and total angular momentum
        new_angular_momentum = self.get_amomentum()
        new_total_angular_momentum = np.sum(new_angular_momentum, axis=0)

        # calculate new total energy
        new_energy = self.get_energy()

        # calculate new COM
        new_com = self.get_com()

        # check if quantities are conserved if the integration update is meant to be symplectic
        if (symplectic):
            # check: COM at the origin
            check_exception((abs(new_com) <= 10e-10).all(), COMNotConservedException,f"COM should be 0, but is {new_com}")

            # check: total linear momentum conserved
            check_exception(self.conserved_quantity(new_total_linear_momentum, self.first_linear_momentum, tolerance = tolerance),
                            LinearMomentumNotConservedException,
                            f"Total Linear Momentum was NOT conserved after the update.\nInitial Total Linear Momentum: {self.first_linear_momentum}\nCalculated Total Linear Momentum: {new_total_linear_momentum}\n")


            # check: total angular momentum conserved
            check_exception(self.conserved_quantity(new_total_angular_momentum, self.first_angular_momentum, tolerance = tolerance),
                            AngularMomentumNotConservedException,
                            f"Total Angular Momentum was NOT conserved after the update.\nInitial Total Angular Momentum: {self.first_angular_momentum}\nCalculated Total Angular Momentum: {new_total_angular_momentum}\n")

            # check: total energy conserved
            check_exception(self.conserved_quantity(new_energy, self.first_energy, tolerance = tolerance),
                            EnergyNotConservedException,
                            f"Total Energy was NOT conserved after the update.\nInitial Total Energy: {self.first_energy}\nCalculated Total Energy: {new_energy}\n")


        # set the newly calculated values of the system
        self.angular_momentum = new_angular_momentum
        self.total_angular_momentum = new_total_angular_momentum
        self.energy = new_energy

    def copy(self):
        """
        Copies the NBody instance
        """
        return deepcopy(self)

    def __str__(self):
        return f"Bodies: {self.n}\n" + \
               f"Total Mass: {self.total_mass}\n" + \
               f"Centre of Mass: {self.com}\n" + \
               f"Linear Momentum:\n {self.linear_momentum}\n" + \
               f"Total Linear Momentum: {self.total_linear_momentum}\n" + \
               f"Angular Momentum:\n {self.angular_momentum}\n" + \
               f"Total Angular Momentum: {self.total_angular_momentum}\n" + \
               f"Kinetic Energy: {self.kinetic_energy}\n" \
               f"Gravitational Potential Energy: {self.gpe}\n" \
               f"Total Energy: {self.energy}\n"



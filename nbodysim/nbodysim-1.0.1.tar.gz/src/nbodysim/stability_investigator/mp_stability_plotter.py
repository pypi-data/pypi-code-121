import os
from multiprocessing import Pool
import tqdm

from nbodysim.three_body import *
from nbodysim.exceptions import *
from nbodysim.integrators.leapfrog_3 import Leapfrog3
from nbodysim.stability_investigator.stability_plotter import StabilityPlotter

class MPStabilityPlotter(StabilityPlotter):
    """
    Inherits from StabilityPlotter. Performs the same task, albeit using multiprocessing to speed up the process.
    """
    def __init__(self, perturb, n_trials, collision_tolerance, escape_tolerance, centre_x = 0, centre_y = 0, steps = 10**4, delta = 10**-2, tolerance = 10**-2, adaptive_constant = 0.1, delta_lim = 10**-5):
        """
        :param perturb: the unit amount by which v_x and v_y can be perturbed.
                        That is,any perturbation to vx or vy is a multiple of perturb
        :param n_trials: the number of times that the initial conditions are perturbed to one side of 0.
                         For example, if n_trials = 5, then we will produce a 11 x 11 matrix.
        :param collision_tolerance: maximum distance between 2 bodies allowed before ending simulation
                                    If None, collisions are not considered.
        :param escape_tolerance: maximum distance away from the centre of mass (COM) allowed before ending simulation
                                 If None, escape_tolerance is automatically calculated
                                 If -1, escape_tolerance is not considered
        :param centre_x: the x coordinate of the centre of the stability plot
        :param centre_y: the y coordinate of the centre of the stability plot
        :param steps: the number of steps to integrate for.
                      Since adaptive time step will be used, this is simply used alongside delta to calculate simulation time
        :param delta: time step to use for the integrator. Smaller time steps lead to more accurate orbits.
                      Since adaptive time step will be used, this is simply used alongside steps to calculate simulation time
        :param tolerance: allowed absolute error for determining conservation of calculated quantities.
        :param adaptive_constant: constant resizing factor for adaptive time step
        :param delta_lim: smallest value allowed for the adaptive time step
        """
        super().__init__(perturb, n_trials, collision_tolerance, escape_tolerance, centre_x, centre_y, steps, delta, tolerance, adaptive_constant, delta_lim)

    def get_stability_cell(self, coords):
        """
        Computes the error score for a single cell in the stability matrix
        :param coords: the row and column of the cell (with coords = (row, col)). Used to calculate the perturbations.
        :return: the error score for the NBody instance in coords of the stability matrix
        """

        # extract row and column, in order to calculate perturbation
        row, col = coords

        # the maximum allowed perturbation
        n = self.perturb * self.n_trials

        # the amount by which y component of velocity is changed
        dvy = n - row * self.perturb

        # the amount by which x component of velocity is changed
        dvx = -n + col * self.perturb

        try:
            # check for potential exceptions (either Figure of 8 or adaptive delta) during initialisation
            nbody = get_figure_8(-0.5 * np.array([-0.93240737, -0.86473146, 0]) + np.array([dvx + self.centre_x, dvy + self.centre_y, 0]), -0.24308753,
                                 collision_tolerance=self.collision_tolerance, escape_tolerance=self.escape_tolerance)

            integrator = Leapfrog3(nbody, steps=self.steps, delta=self.delta, tolerance=self.tolerance, adaptive=True,
                                   adaptive_constant=self.adaptive_constant, store_properties=False, delta_lim=self.delta_lim)

            # integrate, and catch any exception in the process
            try:
                integrator.get_orbits()

                # if integration took 10^5 steps (max allowed) return 1. Otherwise, 0.
                if integrator.full_run:
                    return 1
                else:
                    return 0

            except(SmallAdaptiveDeltaException,
                   COMNotConservedException,
                   LinearMomentumNotConservedException,
                   BodyEscapeException,
                   BodyCollisionException,
                   AngularMomentumNotConservedException,
                   EnergyNotConservedException) as e:

                   # return error score (caused during simulation)
                   return self.get_error_score(e, integrator.times[-1])
        except (Figure8InitException,
                SmallAdaptiveDeltaException) as e:

                # return error score (caused during initialisation)
                return self.exception_dict[e.__class__.__name__]

    def get_stability_matrix(self):
        """
        Perturbs Figure 8 orbit, producing a matrix outlining stability regions.
        Uses multiprocessing to compute the stability_matrix.
        :return: a (2*n_trials + 1 x 2*n_trials + 1), with numbers representing errors dependent on how the simulation ended.
                 Error-to-number conversion depedns on exception_dict
        """

        # list containing the arguments to be used when calculating the stability values
        args = []

        # size of the stability_matrix
        n = 2 * self.n_trials + 1

        # compute the arguments in args
        for i in range(n):
            for j in range(n):
                args.append((i, j))

        # calculate number of CPU cores that can be used
        n_cpus = os.cpu_count()

        # use pooling to multiprocess across a list of different arguments
        # use tqdm in order to get progress in calculations
        with Pool(n_cpus) as pool:
            results = list(tqdm.tqdm(pool.imap(func = self.get_stability_cell, iterable = args), total = n*n))

        # results is a 1D array, so reshape into required matrix
        stability_matrix = np.array(results).reshape((n,n))

        return stability_matrix
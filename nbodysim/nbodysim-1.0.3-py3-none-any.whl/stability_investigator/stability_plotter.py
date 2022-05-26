import matplotlib.pyplot as plt
from matplotlib import colors
import os
import json

from nbodysim.three_body import *
from nbodysim.exceptions import *
from nbodysim.integrators.leapfrog_3 import Leapfrog3

class StabilityPlotter():
    """
    Superclass, used when calculating and plotting an stability matrix.
    A stability matrix is a matrix, with each cell containing a NBody instance, on which a simulation is run.
    Each NBody instance is a Figure of 8, albeit with perturbations to its x and y components of velocity (v_x and v_y respectively)
    The outcome of the simulation is associated with a number, which is then placed within the cell.
    The resulting matrix can be plotted.
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

        self.perturb = perturb
        self.n_trials = n_trials
        self.collision_tolerance = collision_tolerance
        self.escape_tolerance = escape_tolerance
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.steps = steps
        self.delta = delta
        self.run_time = steps * delta
        self.tolerance = tolerance
        self.adaptive_constant = adaptive_constant
        self.delta_lim = delta_lim

        # encode errors as numbers
        self.exception_dict = {"SmallAdaptiveDeltaException": 2,
                              "COMNotConservedException": 3,
                              "BodyEscapeException": 4,
                              "BodyCollisionException": 5,
                              "Figure8InitException": 6,
                              "LinearMomentumNotConservedException": 7,
                              "AngularMomentumNotConservedException": 8,
                              "EnergyNotConservedException": 9}

    def get_error_score(self, exception, time_elapsed):
        """
        Modifies the numerical value of an error (as described in the exception_dict),
        by accounting for the time taken (in simulation time units) until the error appears.
        Thus, a higher error_score indicates that the error took longer to appear, so the orbit was more stable
        :param exception: the exception which caused an error in the simulation
        :param time_elapsed: time until the exception appear
        :return: a numerical value, encompassing the type of error, alongside the time taken until the error happens
        """

        # calculate the factor to account for time taken until error occurred
        addon = time_elapsed/self.run_time

        # to avoid errors being confused, ensure that addon never reaches or exceeds 1
        while addon >= 1:
            addon -= 10**-4

        return self.exception_dict[exception.__class__.__name__] + (1 - addon)

    def get_stability_matrix(self):
        """
        Perturbs Figure 8 orbit, producing a matrix outlining stability regions.
        :return: a (2*n_trials + 1 x 2*n_trials + 1), with numbers representing errors dependent on how the simulation ended.
                 Error-to-number conversion depedns on exception_dict
        """

        # calculate size of matrix
        n = 2 * self.n_trials + 1

        # initialise stability matrix
        stability_matrix = np.zeros(shape=(n, n))

        # the amount by which y component of velocity is changed
        dvy = self.perturb * self.n_trials

        for i in range(n):
            # the amount by which x component of velocity is changed
            dvx = -self.perturb * self.n_trials
            for j in range(n):
                print(f"{i},{j}")
                # initialise perturbed figure of 8
                try:
                    # check for potential exceptions (either Figure of 8 or adaptive delta) during initialisation
                    nbody = get_figure_8(-0.5 * np.array([-0.93240737, -0.86473146, 0]) + np.array([dvx + self.centre_x, dvy + self.centre_y, 0]), -0.24308753,
                                         collision_tolerance=self.collision_tolerance, escape_tolerance=self.escape_tolerance)

                    integrator = Leapfrog3(nbody, steps=self.steps, delta=self.delta, tolerance=self.tolerance, adaptive=True,
                                           adaptive_constant=self.adaptive_constant, store_properties=False, delta_lim=self.delta_lim)

                    # integrate, and catch any exception in the process
                    try:
                        integrator.get_orbits()

                        # if adaptive time step took 10^5 steps (max allowed) set value
                        if integrator.full_run:
                            stability_matrix[i, j] = 1

                    except(SmallAdaptiveDeltaException,
                           COMNotConservedException,
                           LinearMomentumNotConservedException,
                           BodyEscapeException,
                           BodyCollisionException,
                           AngularMomentumNotConservedException,
                           EnergyNotConservedException) as e:

                        # set matrix entry according to error
                        stability_matrix[i, j] = self.get_error_score(e, integrator.times[-1])
                except (Figure8InitException,
                        SmallAdaptiveDeltaException) as e:

                    # set matrix entry according to error
                    stability_matrix[i, j] = self.exception_dict[e.__class__.__name__]

                dvx += self.perturb
            dvy -= self.perturb

        return stability_matrix

    def stability_matrix_to_json(self, stability_matrix: np.ndarray, filename):
        """
        Saves calculated stability matrix, alongside other values used during initialisation of instance,
        as JSON.
        :param stability_matrix: the stability matrix to save
        :param filename: the path to which the stability matrix is saved
        :return: 0 if saving was succesful, 1 otherwise
        """
        json_dict = {"perturb": self.perturb,
                     "n_trials": self.n_trials,
                     "collision_tolerance": self.collision_tolerance,
                     "escape_tolerance": self.escape_tolerance,
                     "centre_x": self.centre_x,
                     "centre_y": self.centre_y,
                     "steps": self.steps,
                     "delta": self.delta,
                     "tolerance": self.tolerance,
                     "adaptive_constant": self.adaptive_constant,
                     "delta_lim": self.delta_lim,
                     "stability_matrix": stability_matrix.tolist()}

        try:
            if not os.path.exists(filename):
                open(filename, "w").close()
                zero_file = True
            else:
                zero_file = os.path.getsize(filename) == 0

            with open(filename, "r+") as json_file:

                if zero_file:
                    json_rewrite = {"stabinv": [json_dict]}
                else:
                    json_rewrite = json.load(json_file)

                    if "stabinv" in json_rewrite:
                        assert isinstance(json_rewrite["stabinv"], list)
                        json_rewrite["stabinv"].append(json_dict)
                    else:
                        json_rewrite = {"stabinv": [json_dict], "errors": [json_rewrite]}

                json_file.seek(0)
                json_file.truncate()

                json.dump(json_rewrite, json_file, indent = 2)

            return 0
        except IOError as e:
            print("Error saving stability params")
            print(e)
            return 1

    def plot_stability_matrix(self, stability_matrix = None, n_ticks = 10, grad = False, show = True, save_fig = False, save_matrix = True, **kwargs):
        """
        Plots an stability matrix given the parameters
        :param stability_matrix: the stability matrix to plot. If None, automatically calculates it.
        :param n_ticks: the number of ticks to use when plotting
        :param grad: if True, plot will use a gradient to represent numbers. Otherwise, will use discrete colours for each number.
        :param show: if True, displays the plot
        :param save_fig: if True, saves the resulting image
        :param save_matrix: if True, saves StabilityPlotter arguments (i.e delta_lim), alongside the produced stability matrix, all in JSON
        :param kwargs: expect at most 2 arguments:
                       json_name: file path to JSON file on which to save StabilityPlotter data, should save_matrix be True
                       fig_name: file path to to save the figure produced, should save_fig be True. Automaticlaly generates file path, if none is provided.
        """

        # calculate stability matrix if not provided
        if stability_matrix is None:
            stability_matrix = self.get_stability_matrix()

        # save stability matrix if required
        if save_matrix:
            if "json_name" in kwargs:
                self.stability_matrix_to_json(stability_matrix, kwargs["json_name"])
            else:
                self.stability_matrix_to_json(stability_matrix, "../img_resources/report_data/report_jsons.json")

        # calculate the side length (to one side of 0) required for the plot
        # for example, if perturb = 0.1 and n_trials = 10,
        # we expect that at most we perturb the initial conditions by 1 in the x and y direction (or negative)
        extent_lim = self.n_trials*self.perturb

        # set up the figure and plot the matrix, with numbers giving pixel values
        fig, ax = plt.subplots()

        if grad:
            # plot using continuous colours
            cmap = plt.get_cmap("nipy_spectral")
            cax = ax.imshow(stability_matrix,
                            extent=(-extent_lim - self.perturb * 0.5 + self.centre_x,
                                    extent_lim + self.perturb * 0.5 + self.centre_x,
                                    -extent_lim - self.perturb * 0.5 + self.centre_y,
                                    extent_lim + self.perturb * 0.5 + self.centre_y),
                            cmap=cmap, vmin=0, vmax=10)
        else:
            # plot using discrete colours
            cmap = plt.get_cmap("viridis")
            # since errors are discrete numbers, use this for the cmap
            norm = colors.BoundaryNorm(np.arange(-0.5, 10, 1), cmap.N)

            cax = ax.imshow(stability_matrix,
                            extent=(-extent_lim - self.perturb * 0.5 + self.centre_x,
                                    extent_lim + self.perturb * 0.5 + self.centre_x,
                                    -extent_lim - self.perturb * 0.5 + self.centre_y,
                                    extent_lim + self.perturb * 0.5 + self.centre_y),
                            norm=norm, cmap=cmap, vmin=0, vmax=9)

        # set plot properties
        ax.set_xlabel(r"$\Delta v_x$")
        ax.set_ylabel(r"$\Delta v_y$")
        ax.set_title("Stability of Figure 8 Under Perturbations", pad=20)

        ax.set_xticks(np.arange(-extent_lim + self.centre_x, extent_lim + self.perturb + self.centre_x, step=2 * extent_lim / n_ticks))
        ax.set_yticks(np.arange(-extent_lim + self.centre_y, extent_lim + self.perturb + self.centre_y, step=2 * extent_lim / n_ticks))

        # show a colorbar
        cb = plt.colorbar(cax, ticks = range(0,10))
        cb.set_label("Error Type", labelpad=20)

        plt.tight_layout()

        # save the plot
        if save_fig and "fig_name" in kwargs:
            if kwargs["fig_name"] is None:
                int_to_string = lambda x: str(x).replace(".", "_")
                save_string = f"stability{2*self.n_trials + 1}-perturb{int_to_string(self.perturb)}-time{int(self.steps*self.delta)}-AC{int_to_string(self.adaptive_constant)}-DL{int_to_string(self.delta_lim)}-ET{int_to_string(self.escape_tolerance)}-CT{int_to_string(self.collision_tolerance)}-TOL{int_to_string(self.tolerance)}-({self.centre_x}-{self.centre_y})"
            else:
                save_string = kwargs["fig_name"]

            # ensure that we don't overwrite an already existing image
            idx = 2
            filename = save_string
            save_file = filename + ".png"
            # if we are to overwrite a file, check & modify the new file accordingly
            while os.path.exists(save_file):
                filename = save_string + f"({idx})"
                save_file = filename + ".png"
                idx +=1

            plt.savefig(save_file)

        if show:
            plt.show()


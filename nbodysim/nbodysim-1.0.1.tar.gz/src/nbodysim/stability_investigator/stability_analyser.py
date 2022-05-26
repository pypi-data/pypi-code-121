import json
from multiprocessing import Pool
import numpy as np
import os
import tqdm
from matplotlib import pyplot as plt

from nbodysim.integrators.leapfrog_3 import Leapfrog3
from nbodysim.stability_investigator.stability_plotter import StabilityPlotter
from nbodysim.stability_investigator.mp_stability_plotter import MPStabilityPlotter
from nbodysim.three_body import get_figure_8
from nbodysim import nmath as nm

class StabilityAnalyser():
    """
    Class used to more thoroughly analyse the regions of stability calculated by a StabilityPlotter instance.
    Requires that the stability matrix be calculated or store somewhere.
    It is NOT responsible of calculating it in the first place.
    In particular, considers how any set of stable initial conditions compare to the original Figure of 8,
    assigning a stabiliity score which can then be visualised as a stability matrix
    """

    def __init__(self, stability_plotter: StabilityPlotter, stability_matrix, **kwargs):
        """
        :param stability_plotter: the stability plotter instance to analyse.
                                  If None, requires kwargs.
        :param stability_matrix: the stabiliy matrix to analyse.
                                 If None, requires kwargs.
        :param kwargs: contains arguments, should a stability_plotter or stability_matrix be provided as None
                       - should contain all initialisation arguments of a StabilityPlotter. That is:
                            -> perturb
                            -> n_trials
                            -> collision_tolerance
                            -> escape_tolerance
                            -> centre_x
                            -> centre_y
                            -> steps
                            -> delta
                            -> tolerance
                            -> adaptive_constant
                            -> delta_lim
                        - additionally, if no stability_matrix is provided, should contain information to obtain it from a JSON file
                            -> filename: file path to JSON
                            -> idx: if None, returns all stability matrices found in filename; otherwise, returns the (idx - 1)th matrix found
                            -> use_self: alternatively to idx, use the StabilityPlotter instance to search through the JSON file
                                        & find the stability matrix that would be produced by the StabilityPlotter instance
        """

        self.stability_plotter = stability_plotter

        # if no stability_plotter is provided, use kwargs to initialise
        if stability_plotter is None:
            try:
                self.perturb = kwargs["perturb"]
                self.n_trials = kwargs["n_trials"]
                self.collision_tolerance = kwargs["collision_tolerance"]
                self.escape_tolerance = kwargs["escape_tolerance"]
                self.centre_x = kwargs["centre_x"]
                self.centre_y = kwargs["centre_y"]
                self.steps = kwargs["steps"]
                self.delta = kwargs["delta"]
                self.run_time = self.steps * self.delta
                self.tolerance = kwargs["tolerance"]
                self.adaptive_constant = kwargs["adaptive_constant"]
                self.delta_lim = kwargs["delta_lim"]
                self.stability_plotter = MPStabilityPlotter(perturb=self.perturb, n_trials=self.n_trials, collision_tolerance = self.collision_tolerance, escape_tolerance = self.escape_tolerance, steps = self.steps, delta = self.delta, tolerance = self.tolerance, adaptive_constant = self.adaptive_constant, delta_lim = self.delta_lim)
            except KeyError as e:
                print("StabilityAnalyser initialisation failed, due to a key parameter not being provided.")
                print("Required parameters: perturb, n_trials, collision_tolerance, escape_tolerance, steps,\n"
                      "delta, tolerance, adaptive_constant, delta_lim")

                raise e
        else:
            self.perturb = stability_plotter.perturb
            self.n_trials = stability_plotter.n_trials
            self.collision_tolerance = stability_plotter.collision_tolerance
            self.escape_tolerance = stability_plotter.escape_tolerance
            self.centre_x = stability_plotter.centre_x
            self.centre_y = stability_plotter.centre_y
            self.steps = stability_plotter.steps
            self.delta = stability_plotter.delta
            self.run_time = self.steps * self.delta
            self.tolerance = stability_plotter.tolerance
            self.adaptive_constant = stability_plotter.adaptive_constant
            self.delta_lim = stability_plotter.delta_lim

        if stability_matrix is None:
            try:
                self.stability_matrix = self.stability_matrix_from_json(kwargs["filename"], kwargs["idx"], kwargs["use_self"])
            except KeyError as e:
                print("StabilityAnalyser initialisation failed, due to a key parameter not being provided.")
                print("Required parameters: filename, idx and use_self")

                raise e
        else:
            self.stability_matrix = stability_matrix

        self.updated_stability_matrix = False


    def stability_matrix_from_json(self, filename, idx = None, use_self = False):
        """
        Reads stability_matrix from JSON.
        Should be used to read data from a JSON file created by stability_matrix_to_json in the StabilityPlotter class.
        :param filename: file path to JSON
        :param idx: if None, returns all stability matrices found in filename; otherwise, returns the (idx - 1)th matrix found
        :param use_self: alternatively to idx, use the StabilityPlotter instance to search through the JSON file
                                        & find the stability matrix that would be produced by the StabilityPlotter instance
        :return: if idx is None, a list of stability matrices; otherwise, a stability matrix
        """

        try:
            with open(filename, "r") as json_file:

                # get all the data in the JSON
                sm_json = json.load(json_file)

                # ensure that JSON is in correct format
                if "stabinv" in sm_json:
                    assert isinstance(sm_json["stabinv"], list)
                    sm_dict_list = sm_json["stabinv"]
                    if idx is None:
                        if use_self:

                            self_dict = {"perturb": self.perturb,
                                         "n_trials": self.n_trials,
                                         "collision_tolerance": self.collision_tolerance,
                                         "escape_tolerance": self.escape_tolerance,
                                         "centre_x": self.centre_x,
                                         "centre_y": self.centre_y,
                                         "steps": self.steps,
                                         "delta": self.delta,
                                         "tolerance": self.tolerance,
                                         "adaptive_constant": self.adaptive_constant,
                                         "delta_lim": self.delta_lim}

                            for sm_dict in sm_dict_list:
                                # go through each stability matrix,
                                # and if found, returns the stability matrix with parameters as set during init
                                stability_matrix = np.array(sm_dict.pop("stability_matrix"))
                                common_dict = dict(sm_dict.items() & self_dict.items())
                                if len(common_dict) == 9 or len(common_dict) == 11:
                                    return stability_matrix

                            print(f"No stability_matrix was found in {filename} with parameters {self_dict}")
                            return np.zeros(shape=(1,))
                        else:
                            # if no idx is provided, return all the stability matrices found
                            return np.array([dict["stability_matrix"] for dict in sm_dict_list])
                    else:
                        # ensure that idx is within bounds and return the stability matrix found
                        assert len(sm_dict_list) > idx >= 0, f"Index {idx} out of bounds for dictionary list of length {len(sm_dict_list)} "
                        return np.array((sm_dict_list[idx])["stability_matrix"])
                else:
                    print(f"File {filename} in incorrect format. Should have a single key 'stabinv' with value as a list.")
                    return np.zeros(shape=(1,))

        except IOError as e:
            print(f"An error occurred when attempting to open {filename} ")
            print(e)
            return np.zeros(shape=(1,))

    def get_positions_cell(self, coords):
        """
        Similar to MPStabilityPlotter method get_stability_cell.
        Computes the orbit for a single cell in the stability matrix (expecing the coords to correspond to stable regions in the matrix=
        :param coords:  the row and column of the cell (with coords = (row, col)). Used to calculate the perturbations.
        :return: a dictionary, containing the row and column that lead to the NBody instance,
                 alongside the positions of each body during the orbit.
        """

        # extract row and column, in order to calculate perturbation
        row, col = coords

        # the maximum allowed perturbation
        n = self.perturb * self.n_trials

        # the amount by which y component of velocity is changed
        dvy = n - row * self.perturb

        # the amount by which x component of velocity is changed
        dvx = -n + col * self.perturb

        nbody = get_figure_8(-0.5 * np.array([-0.93240737, -0.86473146, 0]) + np.array([dvx + self.centre_x, dvy + self.centre_y, 0]), -0.24308753,
                                         collision_tolerance=self.collision_tolerance, escape_tolerance=self.escape_tolerance)

        integrator = Leapfrog3(nbody, steps=self.steps, delta=self.delta, tolerance=self.tolerance, adaptive=True,
                               adaptive_constant=self.adaptive_constant, store_properties=False, delta_lim=self.delta_lim)

        integrator.get_orbits()

        return {"row": row,
                "col": col,
                "positions": integrator.position_orbit}

    def get_stable_positions(self):
        """
        Similar to MPStabilityPlotter method get_stability_matrix.
        Using the stability_matrix computed during initialisation, applies get_position_cell for each element of the stability region.
        Uses multiprocessing to compute these values.
        :param coords:  the row and column of the cell (with coords = (row, col)). Used to calculate the perturbations.
        :return: a list of dictionaries, eahc containing the row and column that lead to the NBody instance,
                 alongside the positions of each body during the orbit.
        """

        # list containing the arguments to be used when creating the dictionaries
        args = []

        # size of the stability_matrix
        n = 2 * self.n_trials + 1

        for i in range(n):
            for j in range(n):
                # get the coords if and only if the region is stable
                if self.stability_matrix[i,j] == 0 or self.stability_matrix[i,j] == 1:
                    args.append((i, j))

        # calculate number of CPU cores that can be used
        n_cpus = os.cpu_count()

        # use pooling to multiprocess across a list of different arguments
        # use tqdm in order to get progress in calculations
        with Pool(n_cpus) as pool:
            results = list(tqdm.tqdm(pool.imap(func=self.get_positions_cell, iterable=args), total=len(args)))

        return results

    def get_stability_scores(self, square_size):
        """
        Computes the stability score for each stable orbit.
        This is done by comparing the stable orbit to the original Figure of 8.
        To do this, we change the stable orbit positions to a new set of coordinates,
        such that the 3 body positions can be represented by 2 coordinates, X_1 and X_2.
        If we plot X_1 and X_2 in a grid of squares, we can the count the number of distinct squares that the curve goes through.
        The number of squares is then the stability score.
        :param square_size: the length of a square in the grid
        :return: a list of dictionaries, containing the row, col and positions of the stable NBody instance been experimented,
        alongside the transformed coordinates, X_1 and X_2, and the stability score
        """

        # compute the positions of each of the stable orbits
        stability_positions = self.get_stable_positions()
        stability_scores = []

        # for each stable position, compute the stability score
        for stable_position in stability_positions:

            # use a dictionary to keep track of the squares visited
            visited_squares = {}

            # use the positions to transform to X_1, X_2 coords
            X_1, X_2 = nm.get_relative_normalised_positions(stable_position["positions"])

            # compute the the index of the x coordinate of the square containing X_1
            x = np.floor(X_1/square_size)
            # compute the the index of the y coordinate of the square containing X_1
            y = np.floor(X_2 / square_size)

            # compute a unique number based on x and y
            keys = nm.pair_encoder(x, y)

            # check if a square has been visited before
            for key in keys:
                if key not in visited_squares:
                    visited_squares[key] = 1

            position_dict = stable_position
            position_dict["X_1"] = X_1
            position_dict["X_2"] = X_2
            position_dict["stability_score"] = len(visited_squares)

            stability_scores.append(position_dict)

        return stability_scores

    def update_stability_matrix(self, sb_scores, square_size = 0.01):
        """
        Using a list of dictionaries (containing stability scores), updates the stability matrix.
        Stored as an attribute u_stability_matrix
        :param sb_scores: the stability scores. If None, computes it automatically.
        :param square_size: square_size to be used if sb_scores is None
        """

        # compute stability_scores if not provided
        if sb_scores is None:
            sb_scores = self.get_stability_scores(square_size)

        # intialise updated stability_matrix
        self.u_stability_matrix = self.stability_matrix
        self.updated_stability_matrix = True

        # use the largest stability score to normalise all stability scores between 0 and 1
        normalisation_factor = max([sb_score["stability_score"] for sb_score in sb_scores])
        normalisation_factor = normalisation_factor + 10**(np.floor(np.log10(normalisation_factor)) - 1)

        # for each stability score dictionary, update the stability matrix
        for sb_score in sb_scores:
            stability_value = self.stability_matrix[sb_score["row"], sb_score["col"]] + sb_score["stability_score"]/normalisation_factor
            self.u_stability_matrix[sb_score["row"], sb_score["col"]] = stability_value

    def plot_stability_score(self, sb_score, square_size = 0.01, idx = 0):
        """
        Using a stability score dictionary,
        plots the perturbed Figure of 8 orbit, alongside the orbit in the X_1 and X_2 coordinates
        :param sb_score: the stability score dictionary to use. If None, computes it.
        :param square_size: the square size to use to compute the stability scores
        :param idx: the index of the stability score dictionary of interest within the stability scores list
        """

        # obtain the stability score of interest
        if sb_score is None:
            sb_score: dict = self.get_stability_scores(square_size)[idx]

        # plot the Figure of 8 orbit alongside the X_1,X_2 orbit
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        ax[0].plot(sb_score["positions"][0, :, 0], sb_score["positions"][0, :, 1], c="k")
        ax[0].plot(sb_score["positions"][1, :, 0], sb_score["positions"][1, :, 1], c="k")
        ax[0].plot(sb_score["positions"][2, :, 0], sb_score["positions"][2, :, 1], c="k")
        ax[0].set_title("Figure of 8")
        ax[1].plot(sb_score["X_1"], sb_score["X_2"])
        ax[1].set_title(f"Shifted Coords Figure of 8\nScore: {sb_score['stability_score']}")
        plt.show()

    def plot_stability_scores(self, sb_scores, square_size = 0.01, **kwargs):
        """
        Using a list of stability score dictionaries,
        plots the perturbed Figure of 8 orbit, alongside the orbit in the X_1 and X_2 coordinates.
        Can be used for a list of stability score dictionaries, or a single stability score dictionary
        :param sb_scores: the stability scores dictionary to use. If None, computes it.
        :param square_size: the square size to use to compute the stability scores
        :param kwargs: should contain a single argument:
                        ->idx: the index of the stability score dictionary of interest within the stability scores list
        """

        # compute list of stability scores
        if sb_scores is None:
            sb_scores = self.get_stability_scores(square_size)

        # if idx provided, we want a single stability score dictionary, so get it and plot it
        if "idx" in kwargs:
            sb_score = sb_scores[kwargs["idx"]]
            self.plot_stability_score(sb_score)
        else:
            # otherwise, plot all stability score dictionaries
            for sb_score in sb_scores:
                self.plot_stability_score(sb_score)

    def plot_updated_stability_matrix(self, n_ticks = 10, grad = False, show = True, save_fig = False, save_matrix = True, **kwargs):
        """
        Plots an updated stability matrix, containing information on the stability of the stable regions.
        If the stability matrix wasn't updated, providing a list of stability score dictionaries can be used to update it.
        :param n_ticks: the number of ticks to use when plotting
        :param grad: if True, plot will use a gradient to represent numbers. Otherwise, will use discrete colours for each number.
        :param show: if True, displays the plot
        :param save_fig: if True, saves the resulting image
        :param save_matrix: if True, saves StabilityPlotter arguments (i.e delta_lim), alongside the produced stability matrix, all in JSON
        :param kwargs: expect at most 4 arguments:
                       sb_scores: list of dictionaries containing the stability scores. If None, will be automatically computed.
                       square_size: if sb_scores is None, used to compute them
                       json_name: file path to JSON file on which to save StabilityPlotter data, should save_matrix be True
                       fig_name: file path to to save the figure produced, should save_fig be True. Automaticlaly generates file path, if none is provided.
        """

        if not self.updated_stability_matrix:
            if "sb_scores" in kwargs and "square_size" in kwargs:
                self.update_stability_matrix(kwargs["sb_scores"], kwargs["square_size"])
            else:
                print("sb_scores or square_size not provided as arguments, and stability matrix wasn't updated. Plotting original stability matrix.")
                self.stability_plotter.plot_stability_matrix(stability_matrix = self.stability_matrix, n_ticks=n_ticks, grad = grad, show = show, save_fig = save_fig, save_matrix = save_matrix, **kwargs)

        self.stability_plotter.plot_stability_matrix(stability_matrix = self.u_stability_matrix, n_ticks=n_ticks, grad = grad, show = show, save_fig = save_fig, save_matrix = save_matrix, **kwargs)






from pathlib import Path
import platform
import os
import subprocess
import pkg_resources
import pathlib
import pandas as pd
import numpy as np

from . import results


class Distribution:
    """Class for manipulating PreciSo precipitates distribution.
    """

    def __init__(self, input_file, results_directory, output, nodes, n_samples):
        """Class initializer.


        Parameters
        ----------

        input_file : str or pathlib.Path
            The location of the input file used for this run. Make sure that it's
            correct, as specifying a wrong `input_file` name/path will result in
            erroneous content of the Results object.
        results_directory : str or pathlib.Path
            The folder that contains the files created when invoking PreciSo (C++)
            with input_file.
        output : str
            The standard output captured when executing PreciSo.
        nodes : List of int (optional)
            The id of the node(s) for which we want the precipitates distribution. Default is [0].
        n_samples : int (optional)
            Number of "snapshots" of the precipitates distribution to store in the
            Distribution object. If equal to 2, initial and final distributions are stored.
            If equal to 1, the initial one is stored. If superior to 2, `n_samples` evenly separated
            snapshots are created between initial and final snapshots (those two included).

        Returns
        ----------

        Distribution
            The Distribution object
        """ 

        # Determine precipitates names
        prefix = results.keyword_to_value(input_file, "savedistribution", 1, strict=True)[0]
        precipitates = results.keyword_to_value(input_file, "precipitate", 1, multiple=True)
        distribution_filename = prefix+precipitates[0]+'_0.dat'
        self.n_datapoints = Distribution.get_n_datapoints(distribution_filename, results_directory)
        self.n_samples = n_samples
        steps = np.linspace(0, self.n_datapoints-1, n_samples)
        steps = steps.astype(int)
        times = None

        distribution_images = {"steps": steps, "times": times}

        self.data = Distribution.parse_distrib(self, input_file, results_directory, distribution_images, nodes)

    # def get_distribution(self, precipitate_name, times=None, steps=None, nodes=None):
    #     """Returns the distribution of a precipitate (optionally on a specified
    #     node), at different times and/or steps.

    #     Parameters
    #     ----------

    #     precipitate_name : str
    #         The name of the precipitate to query. It should match the ones found in the
    #         `input_file`.
    #     times : List of floats or int
    #         The different instants when we want a snapshot of the distribution. If no exact match, the closest data point is taken. In case of same distance, the earliest is taken.
    #     steps : List of ints
    #         The different steps at which we want snapshots of the distribution. Has to be less than the total number of steps at which distribution was saved.
    #     nodes : List of int (optional)
    #         The id of the node(s) for which we want the precipitates distribution. Default is 0.

    #     Returns
    #     ----------

    #     Distribution
    #         The Distribution object
    #     """
    #     # if times is not None and steps is not None:
    #     #     raise ValueError("You must specify either t or step")
    #     if nodes is None:
    #         nodes = [0]
    #     if times is None and steps is None:
    #         steps = [-1]
    #     if isinstance(steps, int):
    #         step = [step]

    #     distribution_images = {"steps": steps, "times": times}
    #     # TODO devrait aller chercher l'info dans "DATA"
    #     # return parse_distrib(self.input_file, self.results_directory,
    #     #                     distribution_images, nodes)

    def parse_distrib(self, input_file, results_directory, distribution_images, nodes):
        """Opens and reads the distributions file.

        Parameters
        ----------
        input_file : str or pathlib.Path object
            The location of the input file passed to PreciSo.
        results_directory : str or pathlib.Path object
            The location of the results files created by PreciSo.
        nodes : List of int (optional)
            The id of the node(s) for which we want the precipitates distribution. Default is 0.
        distribution_images : dict
            The steps and/or times at which distributions are to be evaluated. Format is : `distribution_images = {"steps": steps, "times": times}`, with `steps` being an array of ints and `times` an array of floats (in seconds).

        Returns
        ----------

        distributions : dict
            A nested dictionary that contains the data in the form of pandas dataframes.
        """

        # Determine what will be the prefix of the file's name
        prefix = results.keyword_to_value(input_file, "savedistribution", 1, strict=True)[0]
        
        # Determine precipitates names
        precipitates = results.keyword_to_value(
            input_file, "precipitate", 1, multiple=True)

        # Determine total number of nodes
        nodes_total = int(results.keyword_to_value(input_file, "nodes", 1)[0])
        if len(nodes) > nodes_total:
            raise ValueError("Value of varible `nodes` is superior to the number of nodes in input file")

        distribution = {}

        for node in nodes:
            distribution[node] = {}
            for precipitate in precipitates:
                filename = prefix+precipitate+'_'+str(node)+'.dat'
                distribution[node][precipitate] = {}
                
                with open(pathlib.Path(results_directory).joinpath(filename), 'r') as f:
                    text = f.readlines()
                N_data = self.n_datapoints

                for step in distribution_images["steps"]:
                    line_num = int(3 + step * 3)
                    if line_num > len(text):
                        raise ValueError(
                            "Step index larger than actuel number of steps in distribution file {}".format(filename))
                    data = {
                        "R_i": np.fromstring(text[line_num], dtype=float, sep=' '),
                        "N_i": np.fromstring(text[line_num+1], dtype=float, sep=' '),
                        "D_i": np.fromstring(text[line_num+2], dtype=float, sep=' ')
                    }
                    df = pd.DataFrame(data={key: val[1:] for key, val in data.items()})
                    df.R_star = data["R_i"][0]
                    df.time = data["N_i"][0]
                    df.step = step
                    distribution[node][precipitate][step] = df

        return distribution

    def get_n_datapoints(filename, results_directory):
        """Analyses a distribution file and returns the number of datapoints it contains.

        Parameters
        ----------
        input_file : str or pathlib.Path object
            The name of the input file passed to PreciSo.
        results_directory : str or pathlib.Path object
            The location of the results files created by PreciSo.
        nodes : List of int (optional)
            The id of the node(s) for which we want the precipitates distribution. Default is 0.

        Returns
        ----------

        distributions : dict
            A nested dictionary that contains the data in the form of pandas dataframes.
        """
        with open(pathlib.Path(results_directory).joinpath(filename), 'r') as f:
            text = f.readlines()            

            N_lines = len(text)
            # N_lines = sum(1 for _ in f)
            N_data = N_lines / 3
            if N_data != round(N_lines / 3):
                raise ValueError(
                    "Incorrect number of lines in distribution file {}".format(filename))
        return int(N_data - 1)

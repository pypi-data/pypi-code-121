from pathlib import Path
import platform
import os
import subprocess
import pkg_resources
import pathlib
import pandas as pd

from . import distributions


class Results:
    """Class for manipulating PreciSo simulation results.
    
    Parameters
    ----------

            input_file : pathlib.Path object or str
                The path to the input file to use in Preciso. Can be given either as
                a `pathlib.Path` object (recommended as it is cross-plateform) or as
                a `str` that complies with the computer's filesystem.
            results_directory : pathlib.Path object or str
                The path to directory where Preciso wrote its output files. Can be given either as
                a `pathlib.Path` object (recommended as it is cross-plateform) or as
                a `str` that complies with the computer's filesystem.
            output : str
                The standard output captured during the run of preciso.
            nodes : List of int (optional)
                The id of the node(s) for which we want the precipitates distribution. Default is 0.
            n_samples: int
                *Not implemented yet* - The number of "snapshots" of the precipitates distribution we want.

    Attributes
    ----------

        log : str
            The standard output passed by PreciSo during its execution.
        distribution : preciso.Distribution object
            A preciso.Distribution object, that contains all the data related to precipitates size distributions.
        precipitatiton : dict
            A nested dictionary that contains the data in the form of pandas dataframes.
        mechanics :
            A nested dictionary that contains the data in the form of pandas dataframes.

    """

    def __init__(self, input_file, results_directory, output, nodes, n_samples):
        """Class initializer.

        Returns
        ----------

        Results
            The Results object
        """

        list_files = os.listdir(results_directory)
        if 'computation.end' not in list_files:
            raise RuntimeError("No computation.end flag file found in directory {}".format(results_directory))
    


        self.stdout = output
        self.log = Results.parse_log(results_directory)
        # If 'savedistribution' keyword is specified in input file create a 'distribution' attribute to 'results'
        
        if (keyword_to_value(input_file, "savedistribution", 1, strict=False) != []) & (keyword_to_value(input_file, "noPrecipitation", 0, strict=False) == []):
            self.distribution = distributions.Distribution(
                input_file, results_directory, output, nodes, n_samples)  # nodes=nodes, max_samples=max_samples)

        self.precipitation = Results.parse_precipitation(input_file, results_directory)
        self.mechanics = Results.parse_mechanics(input_file, results_directory)

    def __str__(self):
        return self.stdout

    def parse_log(results_directory):
        """Opens and reads the `log.log` file.

        Parameters
        ----------

        results_directory : str or pathlib.Path object
            The location of the results files created by PreciSo. 

        Returns
        ----------

        log : str
            The content of log.log
        """
        with open(pathlib.Path(results_directory).joinpath("log.log"), 'r') as f:
            log = f.read()
        return log

    def parse_precipitation(input_file, results_directory):
        """Opens and reads the "results" files saved by Preciso.

        Parameters
        ----------

        input_file : str or pathlib.Path object
            The location of the input file to search in.
        results_directory : str or pathlib.Path object
            The location of the results files created by PreciSo.

        Returns
        ----------

        results : dict
            A nested dictionary that contains the data in the form of pandas dataframes.
        """
        # Determine number of nodes
        nodes = keyword_to_value(input_file, "nodes", 1)[0]

        results = {}
        for node in range(int(nodes)):
            filename = keyword_to_value(input_file, "savethermodynamics", 1)[0] + "_" + str(node) + ".dat"
            filepath = pathlib.Path(results_directory).joinpath(filename)
            results[node] = pd.read_csv(filepath, header=2, delim_whitespace=True)
            with open(filename, 'r') as f:
                results[node].header = f.readline() + f.readline()

        if results != {}:
            return results
        else:
            raise ValueError("No results could be read using `pd.read_csv({})`.\n Check file existence and formatting.".format(filepath))

    def parse_mechanics(input_file, results_directory):
        """Opens and reads the "mechanics" files saved by Preciso.

        Parameters
        ----------

        input_file : str or pathlib.Path object
            The location of the input file to search in.
        results_directory : str or pathlib.Path object
            The location of the results files created by PreciSo.

        Returns
        ----------

        results : dict
            A nested dictionary that contains the data in the form of pandas dataframes.
        """

        # Determine number of nodes
        mechanic_model = keyword_to_value(input_file, "mechanicModel", 1, strict=False)
        if mechanic_model != []:
            nodes = keyword_to_value(input_file, "nodes", 1)[0]
            results = {}
            for node in range(int(nodes)):
                filename = keyword_to_value(input_file, "savethermodynamics", 1)[0] + "Mechanic" + "_" + str(node) + ".dat"
                filepath = pathlib.Path(results_directory).joinpath(filename)
                results[node] = pd.read_csv(filepath, header=3, delim_whitespace=True)
                with open(filename) as f:
                    results[node].header = f.readline() + f.readline() + f.readline()

            if results != {}:
                return results
            else:
                raise ValueError(
                    "No results could be read using `pd.read_csv({})`.\n Check file existence and formatting.".format(filepath))
        else:
            return 'Mechanics were disabled for this run. See input file.'


def keyword_to_value(input_file, keyword, index, multiple=False, strict=True):
    """Returns the value associated to given keyword in a Preciso InputFile.

    Parameters
    ----------

    input_file : str or pathlib.Path object
        The location of the input file to search in.
    keyword : str
        The keyword you're looking for the value of.
    index : int
        The position of the value in the line. For example with `key foo val`,
        `val` is at position [2] on the line.
    multiple : bool
        Allow multiple occurences of the keyword to be found.
    strict : bool
        Raise an error if no match was found. If False, [] is returned instead.

    Returns
    ----------

    values : list of str
        The values found.

    Examples
    ---------

    >>> import preciso
    >>> preciso.results.keyword_to_value("notebooks/AlMgSi_example.in", "savedistribution", 0)                                                                 
    ['savedistribution']

    >>> preciso.results.keyword_to_value("notebooks/AlMgSi_example.in", "savedistribution", 1)                                                                 
    ['distribution-6351-170']

    >>> preciso.results.keyword_to_value("notebooks/AlMgSi_example.in", "savedistribution", 2)                                                                 
    ['100']

    """
    if not isinstance(keyword, str):
        raise ValueError("Keywords should be of type str")
    if keyword.split() != [keyword]:
        raise ValueError("Keywords can't contain whitespaces.")

    with open(input_file, 'r') as f:
        values = []
        for line in f:
            words = line.split()
            if words != []:
                if keyword == words[0]:
                    values.append(words[index])
                    if not multiple:
                        break
    if values == [] and strict:
        raise RuntimeError("Could not find values of {} keyword in input file {}".format(keyword, input_file))
    return values

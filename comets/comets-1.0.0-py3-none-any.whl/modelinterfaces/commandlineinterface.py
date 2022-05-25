# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ..core.modelinterface import ModelInterface
import tempfile
import json
import subprocess
import time


class CommandLineModelInterface(ModelInterface):
    """
    ModelInterface for a model that is running from the command line and that uses input and output files to set input parameters and to provide output results.
    The user provides a command line to be run from a shell, as well as functions to write input parameters inside a directory and to read output parameters from files in a directory.
    The model runs in a temporary directory with unique name, to ensure no conflicts during parallelization.

    Args:
        cmd (string): Command line to run the model. The command line will be run from inside a temporary folder, so paths should be absolute,
            or relative if refering to files inside the temporary folder.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change during an experiment.
            These parameters will be appended to any additional input ParameterSet set using set_inputs.
        write_input_parameters (callable, optional): Function that takes as input a ParameterSet and the name of a temporary directory.
            This function is responsible for writing the input ParameterSet to a file in this directory, in the required format for the model.
            If no function is provided, the input parameters are written in a JSON format in the file input_file.json in the temporary directory.
        collect_output_results (callable, optional): Function that takes as input the name of a temporary directory and returns the output ParameterSet of the model.
            This function is responsible for collecting the outputs of the model and for returning them as a python dictionary.
            If no function is provided, it is assumed the outputs are written in the file output_file.json in JSON format.
        is_blocking (boolean, optional): Whether the command line cmd is blocking or not. If not, a function model_run_is_finished should be provided. Default to True
        model_run_is_finished (callable, optional): Function that takes as input the name of the temporary directory in which the model is running,
            and returns True if the model run is finished.

    Example
    -------
    .. code-block:: python

        #This example assumes that ~/Path/to/model.py is a python script
        #that reads the file provided by the first argument,
        #computes something with the parameters in this file,
        #and outputs the results in a file provided by the second argument

        cmd = f"python3 ~/Path/to/model.py input_file.txt output_file.txt"

        def write_input_parameters(parameters, directory):
            with open(directory + '/input_file.txt', 'w') as file:
                file.write(json.dumps(parameters))

        def collect_output_results(directory):
            with open(directory + '/output_file.txt', 'r') as file:
                outputs = json.loads(file.read())
            return outputs

        cmdinterface = CommandLineModelInterface(
            cmd,
            cold_input_parameter_set={'x1': 1},
            write_input_parameters=write_input_parameters,
            collect_output_results=collect_output_results,
        )

        cmdinterface.initialize()
        cmdinterface.set_inputs({'x2': 1, 'x3': 2})
        cmdinterface.run()
        cmdinterface.get_outputs(['all'])
        cmdinterface.terminate()

    """

    def __init__(
        self,
        cmd,
        cold_input_parameter_set={},
        write_input_parameters=None,
        collect_output_results=None,
        is_blocking=True,
        model_run_is_finished=None,
    ):
        self.cmd = cmd
        self.cold_input_parameter_set = cold_input_parameter_set
        self.tempdirectory = None
        self.tempdirectoryname = None
        self.is_blocking = is_blocking
        self.write_input_parameters = write_input_parameters
        self.collect_output_results = collect_output_results
        self.model_run_is_finished = model_run_is_finished
        if not self.is_blocking and self.model_run_is_finished is None:
            raise RuntimeError(
                "If the command line is not blocking, a function model_run_is_finished should be provided"
            )
        self.initialize()

    def initialize(self):
        """
        Reset the inputs, outputs, load the cold_input_parameter_set and create a temporary directory to run the simulation
        """
        self.outputs = {}
        self.inputs = {}
        self.tempdirectory = tempfile.TemporaryDirectory(prefix="tmpModel")
        self.tempdirectoryname = self.tempdirectory.name
        self.set_inputs(self.cold_input_parameter_set)

    def set_inputs(self, input_parameter_set={}):
        """
        Set the value of input parameters of the model.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        """
        # Check that the temp directory exists, otherwise it means the model has not been initialized
        if self.tempdirectory is None:
            raise RuntimeError("CommandLineModelInterface is not initialized")

        # Append the input ParameterSet to the inputs that have already been given, such as the cold_input_parameter_set
        self.inputs.update(input_parameter_set)

        # Write the parameters in the temporary directory
        if self.write_input_parameters is not None:
            self.write_input_parameters(self.inputs, self.tempdirectoryname)
        else:
            self.default_write_input_parameters(self.inputs, self.tempdirectoryname)

    def get_outputs(self, parameter_names=[]):
        """
        Return the value of specific output parameters of the model. If parameter_names is ['all'], return all output parameters of the function.

        Args:
            parameter_names: a list of string
        Returns:
            ParameterSet: ParameterSet containing the requested parameters
        """
        # Check that the temp directory exists, otherwise it means the model has not been initialized
        if self.tempdirectory is None:
            raise RuntimeError("CommandLineModelInterface is not initialized")

        # If the command line was not blocking, block until the model run is finished
        if not self.is_blocking:
            while not self.model_run_is_finished(self.tempdirectoryname):
                time.sleep(0.01)

        # Read the output parameters in the temporary directory
        if self.collect_output_results is not None:
            outputs = self.collect_output_results(self.tempdirectoryname)
        else:
            outputs = self.default_collect_output_results(self.tempdirectoryname)

        if parameter_names != ['all']:
            outputs = {key: outputs[key] for key in parameter_names}

        return outputs

    def run(self):
        """
        Run the model by calling the command line in a temporary folder.
        """
        # Check that the temp directory exists, otherwise it means the model has not been initialized
        if self.tempdirectory is None:
            raise RuntimeError("CommandLineModelInterface is not initialized")

        # Run the command line
        subprocess.run(f"cd {self.tempdirectoryname}; " + self.cmd, shell=True)

    def terminate(self):
        """
        Clean the temporary folder.
        """
        self.tempdirectory.cleanup()
        self.tempdirectory = None
        self.tempdirectoryname = None

    def default_write_input_parameters(self, input_parameter_set, directoryname):
        """
        Default function to use if the user doesn't provide a write_input_parameters function.
        This function writes the input_parameter_set to a file input_file.json in a directory directoryname.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
            directoryname (string): the path to a temporary directory
        """
        with open(directoryname + '/input_file.json', 'w') as f:
            json.dump(input_parameter_set, f)

    def default_collect_output_results(self, directoryname):
        """
        Default function to use if the user doesn't provide a collect_output_results function.
        This function reads the output parameters from a file output_file.json in a directory directoryname.

        Args:
            directoryname (string): the path to a temporary directory
        Returns:
            ParameterSet: ParameterSet containing the output parameters
        """
        with open(directoryname + '/output_file.json', 'r') as f:
            outputs = json.load(f)
        return outputs

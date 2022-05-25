# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import glob
import json
import os
import pathlib
import sys
import tempfile

import csm
import pandas

from ..core.modelinterface import ModelInterface, StepModelInterface
from ..utilities import get_logger, suppressstdout


class CosmoInterface(ModelInterface):
    """
    Interface to a Cosmo Tech simulator using Python wrappers.

    Args:
        simulator_path (string): Path to the simulator file inside the folder Simulation/ (without Simulation/ in the path) of the project.
        project_path (string, optional): Path to the project containing the model. This should be an absolute path.
            If not specified, the interface assumes that the current execution folder is inside the project folder.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change during an experiment.
            These parameters will be appended to any additional input ParameterSet set using set_inputs.
        iterations (int, optional): Number of iterations of the main loop of the scheduler to run.
            This assumes that there is one main loop in the scheduler, iterations should be lower than the maximal number of iterations set in the instance.
        temporary_consumers (bool, optional): If true, consumers (of type CSVFileGenericConsumer) will be written to a temporary folder that can be accessed to get the results and that will be cleaned after termination.
            Recommended during parallel execution of the simulator when there are CSVFileGenericConsumers.
            Defaults to False to avoid any impact on performances when there are no consumers.
        amqp_consumer_address (string, optional): If provided, consumers using AMQP to send data to the cloud service (at the provided address) will be instantiated automatically.
        simulation_name (string, optional): Simulation name used to label the data sent using AMQP consumers to the cloud service.
        used_probes (list of string, optional): List of probe instance names that should be used during the simulation. By default all probes are used.
        used_consumers (list of string, optional): List of consumer names that should be used during the simulation. By default all probes are used.
        custom_sim_engine (optional): If provided, replaces the csm.engine used to run the simulation.
        custom_consumers (list of tuple, optional): List of tuples, each containing the information required to instantiate a custom Python consumer. Each tuple should contain, in this order:

            * A class defining the python Consumer (class).
                It needs a Consume method that takes as input a p_probeOutput, in the format defined by the probe.
                It may access self.engine as a replacement to csm.engine.
                It should not inherit from csm.engine.Consumer.
            * Name of the consumer (string). The consumer will be accessible after the simulation with its name as CosmoInterface.<ConsumerName>.
            * Name of the probe that is connected to the consumer (string).


    Examples
    -------
    .. code-block:: python

        #This example assumes that there is a model inventorymanagement in "/home/username/Workspace/inventorymanagement"
        #and that the model has been compiled with the python wrappers activated.

        project = "/home/username/Workspace/inventorymanagement"

        simulator_interface = CosmoInterface(
            "Tests/MinimalSimulation", project_path=project, temporary_consumers=True
        )
        simulator_interface.initialize()
        simulator_interface.set_inputs(
            {
                "Model::{Entity}SupplyChain::{Entity}LogisticsNetwork::{Entity}Inventory1::@OnHandInventory": 300.0
            }
        )
        simulator_interface.run()
        outputs = simulator_interface.get_outputs(
            [
                "Model::{Entity}SupplyChain::{Entity}LogisticsNetwork::{Entity}Inventory1::@ListOfOnHandInventory"
            ]
        )
        consumers_directory = simulator_interface.get_consumers_directory()
        ... # Add code to load the files in the directory consumers_directory directly
        #or get the files as a list of pandas dataframes directly
        consumers = simulator_interface.get_consumers()
        simulator_interface.terminate()

        #Advanced example using a custom consumer

        class CustomConsumer():
            def __init__(self):
                self.memory = []

            def Consume(self, p_probeOutput):
                #Depending on the type of probe, the data coming from the probemay need to be casted to a specific object
                data = self.engine.GenericProbeOutput.Cast(p_probeOutput)
                #Perform some eventual processing of the data here
                self.memory.append(data)

        simulator_interface = CosmoInterface(
            simulator_path = "Tests/MinimalSimulationProbe",
            project_path = project,
            custom_consumers = [(CustomConsumer, "LocalConsumer", "Probe1")]
        )

        simulator_interface.initialize()
        simulator_interface.run()
        for i in interface.LocalConsumer.memory:
            print(i.ToString())
        simulator_interface.terminate()

    """

    def __init__(
        self,
        simulator_path,
        project_path=None,
        cold_input_parameter_set={},
        iterations=None,
        temporary_consumers=False,
        amqp_consumer_address=None,
        simulation_name=None,
        used_probes=None,
        used_consumers=None,
        custom_sim_engine=None,
        custom_consumers=[],
    ):
        self.project_path = project_path
        self.simulator_path = simulator_path
        self.inputs = cold_input_parameter_set
        self.outputs = {}
        self.iterations = iterations
        self.temporary_consumers = temporary_consumers
        self.simulation_name = simulation_name
        self.amqp_consumer_address = amqp_consumer_address
        self.used_probes = used_probes
        self.used_consumers = used_consumers
        self.tempdirectory = None
        self.tempdirectoryname = None
        self.sim = None
        self.custom_sim_engine = custom_sim_engine
        self.custom_consumers = custom_consumers

    def initialize(self):
        """
        Load the simulator,
        keep only used probes and consumers,
        if temporary_consumers is True set up a temporary folder for consumers,
        eventually instantiate amqp consumers and custom consumers,
        load the cold_input_parameter_set,
        run the custom initialization
        """

        # Import csm.engine from the project path
        # This is done at initialization and not in the init since the path may be modified in forked processes
        # Known issue: if csm.engine has already been imported in the same python process but with another project,
        # csm.engine will not be imported again. Importlib.reload will not help either.
        if self.custom_sim_engine is not None:
            self.CosmoEngine = self.custom_sim_engine
        else:
            if self.project_path is not None:
                path_lib = pathlib.Path(self.project_path) / "Generated/Build/Lib"
                path_wrapping = (
                    pathlib.Path(self.project_path) / "Generated/Build/Wrapping"
                )
                sys.path.insert(
                    0,
                    str(path_lib.resolve()),
                )
                sys.path.insert(
                    0,
                    str(path_wrapping.resolve()),
                )
            import csm.engine as CosmoEngine

            self.CosmoEngine = CosmoEngine

        logger = get_logger(__name__)
        logger_engine = self.CosmoEngine.LoggerManager_GetInstance().GetLogger()
        if logger.level == 10:
            logger_engine.SetLogLevel(logger_engine.eDebug)
        elif logger.level == 20:
            logger_engine.SetLogLevel(logger_engine.eInfo)
        elif logger.level == 30:
            logger_engine.SetLogLevel(logger_engine.eWarning)
        elif logger.level == 40:
            logger_engine.SetLogLevel(logger_engine.eError)

        suppress = logger.level >= 20
        # Suppress std output from the simulator when logging level is info, warning or error
        # Works in a notebook but may be bypassed by csmcli when launching a script
        with suppressstdout(suppress):
            self.sim = self.CosmoEngine.LoadSimulator(self.simulator_path)

        # Remove unwanted probes and consumers, if used probes or consumers have been specified
        if self.used_probes is not None:
            for probe in self.sim.GetProbes():
                if probe.GetInstanceName() not in self.used_probes:
                    self.sim.DestroyProbe(probe)
        if self.used_consumers is not None:
            for consumer in self.sim.GetConsumers():
                if consumer.GetName() not in self.used_consumers:
                    self.sim.DestroyConsumer(consumer)

        if self.temporary_consumers:
            # If temporary_consumers is true, for each CSVFileGenericConsumer set its output directory to be a directory inside a temporary folder
            self._setup_temporary_consumers()

        if self.amqp_consumer_address is not None:
            # Instantiate consumers using AMQP to send data to the cloud service
            if self.simulation_name is None:
                self.simulation_name = 'default_simulation_name'
            self.sim.InstantiateAMQPConsumers(
                self.simulation_name, self.amqp_consumer_address
            )

        # Add custom python consumers
        for ConsumerClass, ConsumerName, ProbeName in self.custom_consumers:
            self._add_custom_consumer(ConsumerClass, ConsumerName, ProbeName)

        # Load the cold_input_parameter_set
        self.set_inputs(self.inputs)

        # Run a custom initialization method
        self.custom_initialize()

    def custom_initialize(self):
        """
        Inherit from the CosmoInterface and redefine custom_initialize to add some processing performed at the end of each initialize().
        In this method you have access to csm.engine as self.CosmoEngine and to the simulator as self.sim.
        """

    def custom_postrun(self):
        """
        Inherit from the CosmoInterface and redefine custom_postrun to add some processing after the run of a simulation.
        In this method you have access to csm.engine as self.CosmoEngine and to the simulator as self.sim.
        """

    def _add_custom_consumer(self, ConsumerClass, ConsumerName, ProbeName):
        """
        Add a custom Python Consumer to the simulator.

        Args:
            ConsumerClass (class): A class defining the python Consumer.
                It needs a Consume method that takes as input a p_probeOutput, in the format defined by the probe.
                It may access self.engine as a replacement to csm.engine.
                It should not inherit from csm.engine.Consumer.
            ConsumerName (string): Name of the consumer. The consumer will be accessible with its name as CosmoInterface.<ConsumerName>.
                If not specified, assumes we are running from inside the project folder.
            ProbeName (String): Name of the probe that is connected to the consumer.

        Example
        -------
        .. code-block:: python

            class CustomConsumer():
                def __init__(self):
                    self.memory = []

                def Consume(self, p_probeOutput):
                    data = self.engine.GenericProbeOutput.Cast(p_probeOutput)
                    self.memory.append(data)

            simulator_interface = CosmoInterface(
                simulator_path = "Tests/MinimalSimulationProbe",
                project_path = absolutemodelpath,
                custom_consumers = [(CustomConsumer, "LocalConsumer", "Probe1")]
            )

            simulator_interface.initialize()
            simulator_interface.run()
            for i in interface.LocalConsumer.memory:
                print(i.ToString())


        """

        EngineConsumer = (
            self.CosmoEngine.Consumer
        )  # To avoid name problems when calling self inside the class NewConsumerClass

        class NewConsumerClass(ConsumerClass, EngineConsumer):
            def __init__(self, *args, **kwargs):
                """If an engine is provided, add it to the class as self.engine, then call the constructor of parent classes."""
                try:
                    self.engine = kwargs.pop('engine')
                except KeyError:
                    pass
                ConsumerClass.__init__(self)
                EngineConsumer.__init__(self, *args, **kwargs)

        # Instantiate the new consumer and add it as attribute of the CosmoInterface
        setattr(
            self, ConsumerName, NewConsumerClass(ConsumerName, engine=self.CosmoEngine)
        )

        # Connect the consumer to the probe
        getattr(self, ConsumerName).Connect(self.sim.GetProbe(ProbeName))

    def _setup_temporary_consumers(self):
        """
        Setup a temporary directory and change the output directory of each consumer of type CSVFileGenericConsumer to be inside this temporary folder
        """
        self.tempdirectory = tempfile.TemporaryDirectory(prefix="tmpComets")
        self.tempdirectoryname = self.tempdirectory.name

        self.consumers = []
        for consumer in self.sim.GetConsumers():
            if consumer.GetType() == 'CSVFileGenericConsumer':
                currentoutputdirectory = consumer.GetProperty("OutputDirectory")
                consumername = consumer.GetName()
                consumerfilename = consumer.GetProperty("FileName")
                separator = consumer.GetProperty("Separator")
                consumer.SetProperty(
                    "OutputDirectory",
                    self.tempdirectoryname + '/' + currentoutputdirectory,
                )
                folder_path = (
                    pathlib.Path(self.tempdirectoryname) / currentoutputdirectory
                )
                folder_path.mkdir(parents=True, exist_ok=True)
                self.consumers.append(
                    (
                        consumername,
                        folder_path,
                        consumerfilename,
                        separator,
                    )
                )

    def set_inputs(self, input_parameter_set={}):
        """
        Set the value of input parameters of the model.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        """
        logger = get_logger(__name__)
        for datapath, value in input_parameter_set.items():

            logger.debug("Setting attribute: %s to value %s", datapath, value)
            if isinstance(value, str):
                self.sim.FindAttribute(datapath).SetAsString(value)
            else:
                self.sim.FindAttribute(datapath).SetAsString(json.dumps(value))

    def get_outputs(self, parameter_names=[]):
        """
        Return the value of specific output parameters of the model.
        If parameter_names is ['all'], return all default output parameters of the model
        (at the moment there are no default output parameters)

        TO DO: add a possibility to get all output parameters of the model by getting all attributes of all entities?

        Args:
            parameter_names: a list of string
        Returns:
            ParameterSet: ParameterSet containing the requested parameters
        """
        logger = get_logger(__name__)
        output_parameters = {}
        if parameter_names != ['all']:
            for datapath in parameter_names:
                logger.debug("Getting attribute from datapath: %s", datapath)
                try:
                    # The python wrappers have a method that returns the attribute
                    # with a correct python type. However, this method doesn't work
                    # for all DataTypes in particular composites.
                    output_parameters[datapath] = self.sim.FindAttribute(datapath).Get()

                except ModuleNotFoundError:
                    # If it doesn't work we try to get the attribute as a JSON string
                    # and load it into python from the JSON.
                    try:
                        output_parameters[datapath] = json.loads(
                            self.sim.FindAttribute(datapath).GetAsString()
                        )

                    except json.decoder.JSONDecodeError:
                        output_parameters[datapath] = self.sim.FindAttribute(
                            datapath
                        ).GetAsString()
        else:
            logger.debug("There are not default output parameters")
        logger.debug("Returning output parameters: %s", output_parameters)
        return output_parameters

    def get_consumers_directory(self):
        """
        Returns the location of a folder in which the consumer outputs have been written.

        Returns:
            String: Consumer folder location
        """
        if self.temporary_consumers:
            if self.tempdirectory is None:
                raise RuntimeError("CosmoInterface is not initialized")
            return self.tempdirectoryname
        else:
            raise RuntimeError(
                "Argument temporary_consumers is set to False, consumers are written in their original location"
            )

    def get_consumers(self):
        """
        Returns a list of pandas dataframes corresponding to each file generated by a CSVFileGenericConsumer during the simulation. Requires a valid installation of pandas.

        Returns:
            List[pandas.DataFrame]: List of pandas dataframe for each file generated by a CSVFileGenericConsumer
        """
        if self.temporary_consumers:
            if self.tempdirectory is None:
                raise RuntimeError("CosmoInterface is not initialized")
            dataframes = []
            for consumer in self.consumers:
                folder = consumer[1]
                files = list(folder.glob(consumer[2] + '*.csv'))
                for file in files:
                    df = pandas.read_csv(file, sep=consumer[3])
                    dataframes.append(df)
            return dataframes
        else:
            raise RuntimeError(
                "Argument temporary_consumers is set to False, consumers are written in their original location and should be accessed directly"
            )

    def run(self):
        """
        Run the simulation. If a number of iterations has been set, run this number of iterations.
        """
        logger = get_logger(__name__)
        suppress = logger.level >= 20
        # Suppress std output from the simulator when logging level is info, warning or error
        # Works in a notebook but may be bypassed by csmcli when launching a script
        with suppressstdout(suppress):
            if self.iterations is None:
                self.sim.Run()
            else:
                self.sim.Run(self.iterations)

        self.custom_postrun()

    def terminate(self):
        """
        Destroy the simulator (and the custom consumers), which allows to pickle the cosmointerface.
        It will be necessary to reinitialize the simulator before running it again.
        Clean the temporary folder used to write consumers.
        """
        # Remove all the consumers in case that amqp consumers are still connected to ADX
        if self.sim is not None:
            for consumer in self.sim.GetConsumers():
                self.sim.DestroyConsumer(consumer)
        for ConsumerClass, ConsumerName, ProbeName in self.custom_consumers:
            setattr(self, ConsumerName, None)
        self.sim = None
        if self.tempdirectory is not None:
            self.tempdirectory.cleanup()
        self.tempdirectory = None
        self.tempdirectoryname = None


class CosmoStepInterface(CosmoInterface, StepModelInterface):
    """
    Interface to a Cosmo Tech simulator using Python wrappers and a step-by-step run

    Args:
        simulator_path (string): Path to the simulator inside the folder Simulation/ of the project.
        project_path (string, optional): Path to the project containing the model. This should be an absolute path.
            If not specified, assumes we are running from inside the project folder.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change during an experiment.
            These parameters will be appended to any additional input ParameterSet set using set_inputs.
        iterations (int, optional): Number of iterations of the main loop of the scheduler to run.
            This assumes that there is one main loop in the scheduler, iterations should be lower than the maximal number of iterations set in the instance.
        temporary_consumers (bool, optional): If true, consumers (in particular CSVFileGenericConsumer) will be written to a temporary folder that can be accessed to get the results and that will be cleaned after termination.
            Recommended during parallel execution of the simulator when there are consumers.
            Defaults to False to avoid any impact on performances when there are no consumers.
    """

    def initialize(self, config={}):
        """
        Initialize the simulator from the CosmoInterface class, apply the configuration and run the processes that should take place before the first step.
        """

        super().initialize()
        self.set_inputs(config)
        logger = get_logger(__name__)
        suppress = logger.level >= 20
        # Suppress std output from the simulator when logging level is info, warning or error
        # Works in a notebook but may be bypassed by csmcli when launching a script
        with suppressstdout(suppress):
            self.sim.Run(0)

    def step(self):
        """
        Advance one step of the simulation.
        """
        logger = get_logger(__name__)
        suppress = logger.level >= 20
        # Suppress std output from the simulator when logging level is info, warning or error
        # Works in a notebook but may be bypassed by csmcli when launching a script
        with suppressstdout(suppress):
            self.sim.Run(1)

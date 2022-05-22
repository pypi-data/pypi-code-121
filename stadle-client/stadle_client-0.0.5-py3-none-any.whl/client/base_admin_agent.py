import os
import random
import time
from abc import ABC
from abc import abstractmethod

from stadle.client.client import Client
from stadle.lib.env.handler import EnvironmentHandler
from stadle.lib.logging.logger import Logger
from stadle.lib.util.debug import debug_with_stdout
from stadle.lib.util.helpers import read_config
from stadle.lib.entity.model import BaseModel


class BaseAdminAgent(ABC):
    """
    Base Admin Agent is not an inherited class from the Agent.
    But the Admin Agent has an associative relationship with the Agent.
    Simply the default agent is a component of the Admin agent.
    BaseAdminAgent is an abstract class definition


    Args:
        config_file: configuration file containing admin agent options
        simulation_flag: simulation mode is decided by this flag
        aggregator_ip_address: Ip address of the aggregator
        reg_port: registration port used for the communication
        exch_port: exchange port used for misc activities (unused at the moment)
        agent_name: name used for underlying Client
        model_path: path to save local models
        base_model: base model (PyTorch, Tensorflow model)
        agent_running: enables running the agent in continuously
    """

    def __init__(self, config_file: str = None,
                 simulation_flag=None,
                 comm_protocol: str = None,
                 aggregator_ip_address: str = None,
                 reg_port: str = None,
                 exch_port: str = None,
                 agent_name: str = None,
                 model_path: str = None,
                 token: str = None,
                 base_model: BaseModel = None,
                 agent_running: bool = False):
        pass

    @abstractmethod
    def preload(self):
        """
        loads the base model
        """
        pass

    @abstractmethod
    def initialize(self):
        """
        initializes the models loaded
        """
        pass


class AdminAgent(BaseAdminAgent):
    """
    AdminAgent class represents a specific client used to pass in one time information to the STADLE backend server.

    Args:
        config_file: configuration file containing admin agent options
        simulation_flag: simulation mode is decided by this flag
        aggregator_ip_address: Ip address of the aggregator
        reg_port: registration port used for the communication
        exch_port: exchange port used for misc activities (unused at the moment)
        model_path: path to save local models
        base_model: base model (PyTorch, Tensorflow model)
        agent_running: enables running the agent in continuously (default set to False for Admin Agent)

    Example
    -------

        >>> from stadle import AdminAgent
        >>> from stadle.lib.util import client_arg_parser
        >>> from .minimal_model import MinimalModel # this is a class created by user (PyTorch or Tensorflow Model)
        >>> from stadle.entity.model import BaseModel
        >>> from stadle import BaseModelConvFormat

        >>> base_model = BaseModel("PyTorch-Base-Cloud-Model", MinimalModel(), BaseModelConvFormat.pytorch_format)

        >>> args = client_arg_parser()
        >>> admin_agent = AdminAgent(config_file=args.config_path,
        >>>                             simulation_flag=args.simulation,
        >>>                             aggregator_ip_address=args.aggregator_ip,
        >>>                             reg_port=args.reg_port,
        >>>                             exch_port=args.exch_port,
        >>>                             model_path=args.model_path,
        >>>                             base_model=base_model,
        >>>                             agent_running=args.agent_running)
        >>> admin_agent.preload()
        >>> admin_agent.initialize()

    """

    def __init__(self, config_file: str = None, simulation_flag=None, comm_protocol: str = None, aggregator_ip_address: str = None,
                 reg_port: str = None, exch_port: str = None, agent_name: str = None, model_path: str = None, token: str = None,
                 base_model: object = None, agent_running: bool = False):
        super().__init__(config_file, simulation_flag, comm_protocol, aggregator_ip_address, reg_port, exch_port, agent_name,
                         model_path, base_model, agent_running)

        self._log = Logger(self.__class__.__name__.__repr__())
        self._log.logger.info(f"Agent initialized at {time.time()}")

        # Waiting 1 sec, optimize this sleep time if needed
        wait_time = 1 * random.random()
        time.sleep(wait_time)

        # Unique ID in the system
        self.id = None
        self._env_handler = EnvironmentHandler()

        # Read config
        if config_file is None:
            config_file = self._env_handler.admin_agent_config_path

        self.config = read_config(config_file)
        self._log.logger.debug(f'Config loaded: {self.config}')

        default_config = read_config(self._env_handler.admin_agent_config_path)
        default_keys = {k for k in default_config.keys() if k not in self.config.keys()}

        for k in default_keys:
            self.config[k] = default_config[k]

        """
        Commented to not repeat same output in admin agent and client init

        if (default_keys):
            logging.info('The following configuration parameters were not specified in the config file nor the command line:')
            for k in default_keys:
                logging.info(f'\t{k} - setting to default value of {default_config[k]}')
        """

        # Check command line argvs
        if simulation_flag is None:
            self.simulation_flag = bool(self.config['simulation'])
        else:
            self.simulation_flag = simulation_flag
            self.config['simulation'] = simulation_flag

        if comm_protocol == None:
            self.comm_protocol = self.config['comm_protocol']
        else:
            self.comm_protocol = comm_protocol
            self.config['comm_protocol'] = comm_protocol

        # Comm. info to join the FL platform
        if aggregator_ip_address == None:
            self.aggr_ip = self.config['aggr_ip']
        else:
            self.aggr_ip = aggregator_ip_address
            self.config['aggr_ip'] = aggregator_ip_address

        self.wsprefix = f'ws://{self.aggr_ip}:'
        self.msend_port = 0  # later updated based on welcome message

        # ports setting
        if reg_port is None:
            self.reg_port = self.config['reg_port']
        else:
            self.reg_port = reg_port
            self.config['reg_port'] = reg_port

        if exch_port is None:
            self.exch_port = self.config['exch_port']
        else:
            self.exch_port = exch_port
            self.config['exch_port'] = exch_port

        self.agent_running = agent_running

        # TODO: @George setting up the model_path to read the base model from file
        #   instead of user written class for base model

        if agent_name is None:
            self.agent_name = self.config['agent_name']
        else:
            self.agent_name = agent_name
            self.config['agent_name'] = agent_name

        if model_path is None:
            self.model_path = self.config['model_path']
        else:
            self.model_path = model_path
            self.config['model_path'] = model_path

        if isinstance(base_model, BaseModel):
            self.base_model = base_model
        else:
            raise ValueError(f"Base Model must be provided with type {type(BaseModel)}")

        debug_with_stdout(self.__class__.__name__.__str__(), "init", f"Starting upload of base model \n{self.base_model}")

        # if there is no directory to save models
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        self._cl = Client(comm_protocol=self.comm_protocol, aggregator_ip_address=self.aggr_ip, reg_port=self.reg_port, agent_name=self.agent_name,
                          agent_running=self.agent_running, token=token, config_file=config_file)

    def preload(self):
        """
        loads the base model
        """
        self._cl.load_base_model(self.base_model)

    def initialize(self):
        """
        initializes the models loaded
        """
        self._cl.initialize_models()

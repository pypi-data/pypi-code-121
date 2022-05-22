import argparse
import asyncio
import datetime
import logging
import os
import pickle
import random
import sys
import time
from threading import Thread
from typing import Dict

import numpy as np

from stadle.lib.entity.model import BaseModel
from stadle.lib.env.handler import EnvironmentHandler
from stadle.lib.util import client_arg_parser
from stadle.lib.util.debug import debug_with_stdout
from stadle.lib.util.helpers import read_config, get_id, \
    save_model_file, load_model_file, read_state, write_state, is_sgm_received, \
    get_ip, compatible_data_dict_read, \
    compatible_performance_dict_read, generate_performance_dict
from stadle.lib.util.messengers import generate_lmodel_update_message, generate_participate_message, \
    generate_initialize_model_message
from stadle.lib.util.model_conversion import extract_weights_dict
# Client states
from stadle.lib.util.states import ClientState, AgentMsgType, SGMDistributionMsgLocation, AggMsgType, \
    BaseModelConvFormat # this import is ambiguos
from stadle.lib.util.communication_handler import CommunicationHandler

if (EnvironmentHandler.pt_installed_flag()):
    from torch import nn

logging.basicConfig(level=logging.INFO)


class Client:
    """
    Client class instance provides the communication interface
    between Agent's ML logic and an aggregator

    Args:
        config_file: path to client configuration file
        simulation_flag: flag to determine to run simulation mode or not
        aggregator_ip_address: ip address of the aggregator
        reg_port: port used for registration and main communication
        exch_port: exchange port for additional tasks (not used at the moment)
        model_path: path to save local models
        agent_running: flag to set the client running continuously

    Example
    --------

        >>> cl = Client(aggregator_ip_address="localhost",
        >>>        reg_port=8765,
        >>>        exch_port=8766,
        >>>        model_path="./data/model",
        >>>        simulation_flag=True,
        >>>        agent_running=True)
        >>> # Example params for potential use in training termination condition
        >>> training_count = 0
        >>> sg_arrival_count = 0
        >>> # Placeholder dataset objects for training and evaluating performance
        >>> train_data = None
        >>> test_data = None
        >>> # merged_model holds the semi-global model for the current round
        >>> # Semi-global model weights merged with base model architecture
        >>> merged_model = None
        >>> time.sleep(5)
        >>> while judge_termination(training_count, sg_arrival_count):
        >>>     # Check status of client to determine next action
        >>>     client_state = cl.read_agent_state()
        >>> # Semi-global model received by client
        >>>     if (client_state == ClientState.sg_ready):
        >>>         # Get SG model weights from client
        >>>         sg_models = cl.load_model()
        >>>         # Get current base model from client
        >>>         base_model = cl.get_base_model()
        >>>         # Merge SG weights with base model to produce SG model
        >>>         merged_model = base_model.get_merged_model(sg_models['models'])
        >>>         # Change state to begin local training process
        >>>         cl.tran_state(ClientState.training)
        >>>         # Get example performance metrics of SG model
        >>>         acc, loss_test = compute_performance(merged_model, test_data, False)
        >>>         logging.debug(f'--- SG Training accuracy: {acc} ---')
        >>> # Client ready to begin local training process
        >>>     elif (client_state == ClientState.training):
        >>>         # Train SG model on training data
        >>>         trained_model, loss_training = training(merged_model, train_data)
        >>>         # Extract weights from trained local model
        >>>         trained_model_dict = extract_weights_dict(trained_model, cl.get_base_model().type)
        >>>         training_count += 1
        >>>         logging.debug(f'--- Training Done ---')
        >>>         # Check if client state changed during local training
        >>>         client_state = cl.read_agent_state()
        >>>         if (client_state == ClientState.sg_ready):
        >>>             # Client received new SG weights before local training could complete
        >>>             logging.debug(f'--- The training was too slow. A new set of SG modes are available. ---')
        >>>         else:
        >>>             # Compute performance of local trained model on test dataset
        >>>             acc, loss_test = compute_performance(trained_model, test_data, True)
        >>>             # Create dict to store performance metrics for DB storage, GUI viewing
        >>>             performance_dict = cl.create_performance_data(False, acc, acc, loss_training, 0.0, loss_test)
        >>>             logging.debug(f'--- Training accuracy: {acc} ---')
        >>>             # Save trained model weights and performance metrics, then send to aggregator
        >>>             cl.save_model(trained_model_dict, performance_dict)
        >>>             cl.send_model()
        >>>             logging.debug(f'--- Normal transition: The trained local models saved ---')
        >>>             # Change client state to begin local model transmission
        >>>             cl.tran_state(ClientState.sending)

    """

    def __init__(self,
                 config_file: str = None,
                 simulation_flag=None,
                 comm_protocol: str = None,
                 aggregator_ip_address: str = None,
                 reg_port: str = None,
                 exch_port: str = None,
                 token: str = None,
                 agent_name: str= None,
                 model_path: str = None,
                 agent_running: bool = True,
                 max_round: int = -1):

        logging.debug(f"Agent initialized at {time.time()}")

        # Waiting 1 sec, optimize this sleep time if needed
        wait_time = 1 * random.random()
        time.sleep(wait_time)

        # Unique ID in the system
        self.id = None
        self._training_finalized = False
        self._env_handler = EnvironmentHandler()

        # Read config
        if config_file is None:
            config_file = self._env_handler.agent_config_path
            logging.warning(
                "NOTICE: No config file path was specified - using default agent config file")
            logging.warning(
                "To use a specific config file, specify the path using the CLI argument --config_file when running the agent")

        self.config = read_config(config_file)
        logging.debug(f'Config loaded: {self.config}')

        default_config = read_config(self._env_handler.agent_config_path)
        default_keys = {k for k in default_config.keys() if k not in self.config.keys()}

        for k in default_keys:
            self.config[k] = default_config[k]

        if (default_keys):
            logging.info('The following configuration parameters were not specified in the config file')
            logging.info('Placeholder values will be taken from default config - these will be replaced by constructor arguments')
            for k in default_keys:
                logging.info(f'\t{k} - setting to default value of {default_config[k]}')

        # Check command line argvs
        parse_flag = lambda s: (str(s).lower() == 'true') 

        if simulation_flag is None:
            self.simulation_flag = parse_flag(self.config['simulation'])
        else:
            self.simulation_flag = simulation_flag
            self.config['simulation'] = simulation_flag

        if comm_protocol == None:
            self.comm_protocol = self.config['comm_protocol']
        else:
            self.comm_protocol = comm_protocol
            self.config['comm_protocol'] = comm_protocol

        self.comm_handler = CommunicationHandler(self.comm_protocol, verbose=self.simulation_flag)

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

        if token is None:
            self.token = self.config['token']
        else:
            self.token = token
            self.config['token'] = token

        if agent_name is None:
            self.agent_name = self.config['agent_name']
        else:
            self.agent_name = agent_name
            self.config['agent_name'] = agent_name

        if model_path is None:
            self.model_path = self.config['model_path'] + f'/{self.agent_name}'
        else:
            self.model_path = model_path + f'/{self.agent_name}'
            self.config['model_path'] = model_path + f'/{self.agent_name}'

        debug_with_stdout(self.__class__.__name__.__str__(), "init", self.config)

        if ('check_bm_type' in self.config):
            self.check_bm_type = parse_flag(self.config['check_bm_type'])
        else:
            self.check_bm_type = True

        # Get agent's IP address
        self.agent_ip = get_ip()

        # if there is no directory to save models
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        # Update agent ID or assign randomized ID
        agent_id_file_name = "agent_id"
        self.id = get_id(self.model_path, agent_id_file_name)

        self.lmfile = self.config['local_model_file_name']
        self.sgmfile = self.config['semi_global_model_file_name']
        self.statefile = self.config['state_file_name']

        # Aggregation round - later updated by the info from the aggregator
        self.round = 0

        # State indicator
        self.waiting_flag = ClientState.waiting_sgm

        # Initialization
        self.init_weights_flag = parse_flag(self.config['init_weights_flag'])

        self.version = 1.0

        self.agent_running = agent_running

        self.exch_active = agent_running

        self.isRegistered = False

        self.polling_interval = 3

        self.is_finite = False

        self.max_iterations = max_round if max_round > 0 else 10000

        self.base_model = None

        self.num_samples = 1

        self.register_agent()

        if self.agent_running == True:
            self.start_model_exchange_routine()

        logging.debug(f'--- Your IP is {self.agent_ip} ---')

    async def participate(self):
        """
        Send the first message to join an aggregator
        Register agent info in DB and
        Receive state/comm info from the aggregator
        :return:
        """

        try:
            # Create a participation message
            msg = generate_participate_message(self)

            resp = await self.comm_handler.send_msg(msg, f'{self.aggr_ip}:{self.reg_port}')

            if self.agent_running:
                while (resp[0] == AggMsgType.welcome):
                    await asyncio.sleep(5)
                    resp = await self.comm_handler.send_msg(msg, f'{self.aggr_ip}:{self.reg_port}')

            if resp[0] == AggMsgType.welcome:
                # Parse the response message
                # including some port info and the actual round number
                self.isRegistered = True
                self.round = resp[1]
                self.exch_port = resp[2]
                self.msend_port = resp[3]
                logging.debug(f"--- Init Response: {resp[0]} ---")
                # State transition to waiting_sgm
                self.tran_state(ClientState.waiting_sgm)

            elif resp[0] == AggMsgType.update:
                # Parse the response message
                # including some port info and the actual round number
                self.isRegistered = True
                self.round = resp[1]
                self.exch_port = resp[2]
                self.msend_port = resp[3]
                logging.debug(f"--- Init Response: {resp[0]} ---")
                self.save_model_from_message(resp[4])

            elif resp[0] == AggMsgType.registration_failed:
                self.isRegistered = False
                logging.error(f"--- Init Response: {resp[1]}, system exits. ---")
                sys.exit()

            elif resp[0] == AggMsgType.max_agents_reached:
                logging.error("--- Max agents connected to aggregator - cannot connect ---")
                sys.exit()

        except Exception as e:
            logging.error(f"--- Cannot connect to the aggregator \n\t{e}---")
            sys.exit()

    async def send_initial_models(self):
        """
        Send a message to initialize the first model
        :return:
        """
        logging.debug(f'--- sending initial model. current round: {self.round} ---')

        # Read the local models to tell the structure to the aggregator
        # (not necessarily trained)
        try:
            data_dict, performance_dict = load_model_file(
                self.model_path, self.lmfile)
        except:
            logging.error("Cannot load local models!")
            return

        rand_id, gene_time, models, model_id, self.version, base_model = \
            compatible_data_dict_read(data_dict)
        logging.debug(models)

        performance_id, performance_dict = compatible_performance_dict_read(performance_dict)
        logging.debug(models)

        wsaddr = f'{self.wsprefix}{self.reg_port}'
        try:
            # Create an initialize model message
            msg = generate_initialize_model_message(self, model_id, models, gene_time, performance_dict,
                                                    base_model)
            await self.comm_handler.send_msg(msg, f'{self.aggr_ip}:{self.reg_port}', resp_required=False)
        except:
            logging.error("--- cannot connect to the aggregator ---")

        # TODO Receive models in a resp message as one option
        # State transition to waiting_sgm
        self.tran_state(ClientState.waiting_sgm)

    async def model_exchange_loop(self):
        """
        Check the progress of training and send the updated models
        once the training is done
        :return:
        """
        if self.is_finite == True:
            logging.debug(f'--- this is a finite model exchange routine with max iterations {self.max_iterations} ---')
        else:
            logging.debug(f'--- this is an infinite model exchange routine ---')

        loop_count = 0
        while self.exch_active:

            # Number of iterations if clearly specified by users
            if self.is_finite == True and loop_count == self.max_iterations:
                self.agent_running = False

            # stop runnign if the flag is False
            if not self.agent_running:
                logging.debug(f"--- system stops.. ----")
                return

            # Periodically check the state
            state = read_state(self.model_path, self.statefile)

            # ready to send models
            if state == ClientState.sending:

                logging.debug('--- Local model is ready to be sent to the aggregator ---')

                # Read the models from the local file
                data_dict, performance_dict = load_model_file(
                    self.model_path, self.lmfile)

                _, _, models, model_id, _, _ = compatible_data_dict_read(
                    data_dict)

                performance_id, performance_dict = compatible_performance_dict_read(performance_dict)
                upd_msg = generate_lmodel_update_message(
                    self.id, model_id, models, performance_dict, self.num_samples)

                try:
                    await self.comm_handler.send_msg(upd_msg, f'{self.aggr_ip}:{self.msend_port}', resp_required=False)
                    logging.debug('--- Local Models Sent ---')

                    # State transition to waiting_sgm
                    self.tran_state(ClientState.waiting_sgm)
                    logging.debug('--- state transition to waiting_sgm ---')
                except Exception as e:
                    logging.error(f"--- connection lost with the aggregator ---\n{e}")

            # Polling for sg model update
            elif state == ClientState.waiting_sgm or state == ClientState.training:

                logging.debug(f'--- polling to see if there is any update ---')

                msg = list()
                msg.append(AgentMsgType.waiting_sgm)  # 0
                msg.append(self.round)
                msg.append(self.id)
                msg.append(self.exch_active)

                try:
                    resp = await self.comm_handler.send_msg(msg, f'{self.aggr_ip}:{self.msend_port}')

                    if resp[0] == AggMsgType.update:
                        logging.debug(f'--- SG Model Received ---')
                        self.save_model_from_message(resp)
                    elif resp[0] == AggMsgType.max_agents_reached:
                        logging.error(f'--- Max agents connected to aggregator, sgm poll failed ---')
                    else:
                        logging.debug(f'--- SG Model is NOT ready ---')
                except Exception as e:
                    logging.error(f"--- connection lost with the aggregator ---\n{e}")

            # just increment the loop count
            loop_count += 1

            # sleeping for polling interval
            await asyncio.sleep(self.polling_interval)

    def save_model_from_message(self, sgm_msg):

        # pass (model_id, SG_models) to an app
        data_dict = dict()
        data_dict['model_id'] = sgm_msg[int(
            SGMDistributionMsgLocation.model_id)]
        data_dict['models'] = sgm_msg[int(
            SGMDistributionMsgLocation.sg_models)]
        self.round = sgm_msg[int(SGMDistributionMsgLocation.round)]

        # Save the received SG models to the local file
        if self.version == 0.5:
            save_model_file(data_dict['models'], self.model_path, self.sgmfile)
        elif self.version >= 0.6:
            save_model_file(data_dict, self.model_path, self.sgmfile)

        base_model = sgm_msg[int(SGMDistributionMsgLocation.base_model)]

        if (base_model is not None):
            self.update_internal_base_model(base_model)

        # State transition to waiting_sgm
        self.tran_state(ClientState.sg_ready)

    def update_internal_base_model(self, base_model):
        if self.base_model == None:
            self.base_model = base_model
        else:
            temp = self.base_model.obj
            self.base_model = base_model
            self.base_model.obj = temp

    # not in use now
    async def wait_models(self, websocket, path):
        """
        Waiting for SG models from the aggregator
        :param websocket:
        :param path:
        :return:
        """
        sgm_msg = pickle.loads(await websocket.recv())
        logging.debug(f'--- SG Model Received ---')
        logging.debug(f'Models: {sgm_msg}')
        self.save_model_from_message(sgm_msg)

    # ---- APIs ---- #

    def create_performance_data(self,
                                init_flag: bool = False,
                                performance: float = 0.0,
                                accuracy: float = 0.0,
                                loss_training: float = 0.0,
                                loss_valid: float = 0.0,
                                loss_test: float = 0.0,
                                f_score: float = 0.0,
                                reward: float = 0.0,
                                model_type: int = 0,
                                prev_perf_dict: Dict[str, np.array] = dict()):

        return generate_performance_dict(
            init_flag, performance, accuracy, loss_training, loss_valid,
            loss_test, f_score, reward, model_type, prev_perf_dict)

    def tran_state(self, state: ClientState):
        """
        Change the state of the agent
        State is indicated in two places: (1) local file 'state' and (2) waiting_flag
        :param state: ClientState
        :return:
        """
        self.waiting_flag = state
        write_state(self.model_path, self.statefile, self.waiting_flag)

    def change_running_flag(self, state):
        self.agent_running = state

    def _start_routine(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(self.model_exchange_loop()))
        # loop.run_forever() # <- Needed?

    def register_agent(self):

        if self.simulation_flag == True:
            print(f"Default token [{self.token}] is used...")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.participate())

        # Redundant but just in case...
        if self.isRegistered == False:
            logging.debug("Registration unsuccessful")
            sys.exit()

    def initialize_models(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.send_initial_models())

    def start_model_exchange_routine(self):
        self.agent_running = True
        th = Thread(target=self._start_routine)
        th.start()

    def stop_model_exchange_routine(self):
        self.agent_running = False
        self._training_finalized = True

    @property
    def training_finalized(self) -> bool:
        return self._training_finalized

    @property
    def federated_training_round(self) -> int:
        return int(self.round)

    def save_model(self, models=dict(), performance_dict=dict(), model_path=None, local_model_file_name=None):

        if model_path == None:
            model_path = self.model_path

        if local_model_file_name == None:
            local_model_file_name = self.lmfile

        save_model_file(models, model_path, local_model_file_name, performance_dict)
        logging.debug(f'--- Model Saved ---')

    def send_model(self, models=None, performance_dict=dict(), model_path=None, local_model_file_name=None):

        if model_path == None:
            model_path = self.model_path

        if local_model_file_name == None:
            local_model_file_name = self.lmfile

        if models != None:
            self.save_model(models, performance_dict, model_path, local_model_file_name)

        # send model by writing sending state
        write_state(model_path, self.statefile, ClientState.sending)

    def read_agent_state(self):
        state = read_state(self.model_path, self.statefile)
        return state

    def load_model(self, model_path=None):

        if model_path == None:
            model_path = self.model_path

        models = None
        if is_sgm_received(model_path, self.sgmfile):
            models, _ = load_model_file(model_path, self.sgmfile)
        else:
            models, _ = load_model_file(model_path, self.lmfile)

        return models

    def set_exch_active(self, exch_active: bool):
        self.exch_active = exch_active

    # API function for admin agent to perform base model init/update through aggregator
    def load_base_model(self, base_model: BaseModel):
        if (base_model.type == None):
            logging.debug(
                "Resolving model format from model object is currently not supported - please specify the model "
                "format using \'BaseModelConvFormat.pytorch\' or \'BaseModelConvFormat.pytorch\'")
            raise ValueError("Ambiguous model conversion from unknown format")

        if (base_model.name == None):
            gen_time = time.time()
            formatted_time = datetime.datetime.fromtimestamp(gen_time).strftime('%m-%d-%Y_%H:%M:%S')
            base_model.name = f'model_{formatted_time}'

        base_model.prep_for_pickle()

        model_dict = {
            'models': base_model.weights,
            'base_model': base_model
        }
        self.save_model(model_dict)

    def set_num_samples(self, num_samples):
        self.num_samples = num_samples

    def isRegistered(self):
        return self.isRegistered

    def get_base_model(self):
        return self.base_model

    def set_bm_obj(self, obj):
        self.base_model.obj = obj

    @property
    def maximum_rounds(self) -> int:
        return self.max_iterations

    @maximum_rounds.setter
    def maximum_rounds(self, max_rounds: int) -> None:
        self.max_iterations = max_rounds


class BasicClient(Client):
    def __init__(self, config_file: str = None,
                 simulation_flag: bool = None,
                 comm_protocol: str = None,
                 aggregator_ip_address: str = None,
                 reg_port: str = None,
                 exch_port: str = None,
                 token: str = None,
                 agent_name: str = None,
                 model_path: str = None,
                 agent_running: bool = None,
                 cl_args = None
                 ):
        if (cl_args != None):
            if cl_args.config_path:
                config_file = cl_args.config_path
            if cl_args.simulation:
                simulation_flag = cl_args.simulation
            if cl_args.comm_protocol:
                comm_protocol = cl_args.comm_protocol
            if cl_args.aggregator_ip:
                aggregator_ip_address = cl_args.aggregator_ip
            if cl_args.reg_port:
                reg_port = cl_args.reg_port
            if cl_args.exch_port:
                exch_port = cl_args.exch_port
            if cl_args.token:
                token = cl_args.token
            if cl_args.model_path:
                model_path = cl_args.model_path
            if cl_args.agent_name:
                agent_name = cl_args.agent_name
            if cl_args.agent_running:
                agent_running = cl_args.agent_running

        if agent_running is None:
            agent_running = True

        super().__init__(config_file=config_file, simulation_flag=simulation_flag,
                         comm_protocol=comm_protocol, aggregator_ip_address=aggregator_ip_address,
                         reg_port=reg_port, exch_port=exch_port, token=token, agent_name=agent_name,
                         model_path=model_path, agent_running=agent_running)

    def disconnect(self):
        self.stop_model_exchange_routine()

    def send_trained_model(self, trained_model, perf_values = {}):
        # Extract weights from trained local model
        trained_model_dict = extract_weights_dict(trained_model, self.get_base_model().type)

        client_state = self.read_agent_state()

        if client_state == ClientState.sg_ready:
            # Client received new SG weights before local training could complete
            logging.debug(f'--- The training was too slow. A new SG model is available. ---')
            return False
        else:
            performance_dict = self.create_performance_data(**perf_values)

            # Save trained model weights and performance metrics, then send to aggregator
            self.save_model(trained_model_dict, performance_dict)
            self.send_model()
            logging.debug(f'--- Normal transition: The trained local models saved ---')

            # Change client state to begin local model transmission
            self.tran_state(ClientState.sending)
            return True

    def wait_for_sg_model(self):
        # Semi-global model received by client
        while (self.read_agent_state() != ClientState.sg_ready):
            time.sleep(5)

        # Get SG model weights from client
        sg_models = self.load_model()

        # Get current base model from client
        base_model = self.get_base_model()

        # Merge SG weights with base model to produce SG model
        merged_model = base_model.get_merged_model(sg_models['models'])

        # Change state to begin local training process
        self.tran_state(ClientState.training)
        return merged_model

class IntegratedClient(Client):

    def __init__(self, config_file: str = None,
                 simulation_flag: bool = None,
                 comm_protocol: str = None,
                 aggregator_ip_address: str = None,
                 reg_port: str = None,
                 exch_port: str = None,
                 token: str = None,
                 agent_name: str = None,
                 model_path: str = None,
                 agent_running: bool = None,
                 cl_args = None
                 ):
        if (cl_args != None):
            if cl_args.config_path:
                config_file = cl_args.config_path
            if cl_args.simulation:
                simulation_flag = cl_args.simulation
            if cl_args.comm_protocol:
                comm_protocol = cl_args.comm_protocol
            if cl_args.aggregator_ip:
                aggregator_ip_address = cl_args.aggregator_ip
            if cl_args.reg_port:
                reg_port = cl_args.reg_port
            if cl_args.exch_port:
                exch_port = cl_args.exch_port
            if cl_args.token:
                token = cl_args.token
            if cl_args.model_path:
                model_path = cl_args.model_path
            if cl_args.agent_name:
                agent_name = cl_args.agent_name
            if cl_args.agent_running:
                agent_running = cl_args.agent_running

        if agent_running is None:
            agent_running = True

        super().__init__(config_file=config_file, simulation_flag=simulation_flag,
                         comm_protocol=comm_protocol, aggregator_ip_address=aggregator_ip_address,
                         reg_port=reg_port, exch_port=exch_port, token=token, agent_name=agent_name,
                         model_path=model_path, agent_running=agent_running)

        self._termination_fn = None
        self._termination_fn_kwargs = None
        self._training_count = 0
        self._training_fn = None
        self._testing_fn = None
        self._validation_fn = None
        self._training_data = None
        self._testing_data = None
        self._validation_data = None
        self._training_kwargs = None
        self._testing_kwargs = None
        self._validation_kwargs = None

    def set_termination_function(self, fn, **kwargs):
        self._termination_fn = fn
        self._termination_fn_kwargs = kwargs if kwargs else {}

    def set_training_function(self, fn, training_data, **kwargs):
        self._training_fn = fn
        self._training_data = training_data
        self._training_kwargs = kwargs if kwargs else {}

    def set_testing_function(self, fn, testing_data, **kwargs):
        self._testing_fn = fn
        self._testing_data = testing_data
        self._testing_kwargs = kwargs if kwargs else {}

    def set_validation_function(self, fn, validation_data, **kwargs):
        self._validation_fn = fn
        self._validation_data = validation_data
        self._validation_kwargs = kwargs if kwargs else {}

    def _train(self, model, data, **kwargs):
        return self._training_fn(model, data, **kwargs)

    def _test(self, model, data, **kwargs):
        return self._testing_fn(model, data, **kwargs)

    def _validate(self, model, data, **kwargs):
        """
            Given a model and the test dataset, compute performance of model
            on test dataset
        """
        return self._validation_fn(model, data, **kwargs)

    def is_final(self, callable, **kwargs):
        return callable(**kwargs)

    def __call__(self, *args, **kwargs):
        self._execute(args, kwargs)

    def start(self):
        self._execute()

    def stop(self):
        # TODO: implement a way to gracefully shutdown a client
        pass

    def _execute(self, *args, **kwargs):
        # Example params for potential use in training termination condition

        # Placeholder dataset objects for training and evaluating performance

        # merged_model holds the semi-global model for the current round
        # Semi-global model weights merged with base model architecture
        merged_model = None

        time.sleep(5)

        while self.is_final(self._termination_fn, **self._termination_fn_kwargs):
            # Check status of client to determine next action
            client_state = self.read_agent_state()

            # Semi-global model received by client
            if client_state == ClientState.sg_ready:
                # Get SG model weights from client
                sg_models = self.load_model()

                # Get current base model from client
                base_model = self.get_base_model()

                # Merge SG weights with base model to produce SG model
                merged_model = base_model.get_merged_model(sg_models['models'])

                # Change state to begin local training process
                self.tran_state(ClientState.training)

                # Get example performance metrics of SG model
                acc, loss_test = self._validate(merged_model, self._validation_data,
                                                      **self._validation_kwargs)
                logging.debug(f'--- SG Training accuracy: {acc} ---')

            # Client ready to begin local training process
            elif client_state == ClientState.training:
                # Train SG model on training data
                trained_model, loss_training = self._train(merged_model, self._training_data, **self._training_kwargs)

                # Extract weights from trained local model
                trained_model_dict = extract_weights_dict(trained_model, self.get_base_model().type)
                self._training_count += 1
                logging.debug(f'--- Training Done ---')

                # Check if client state changed during local training
                client_state = self.read_agent_state()

                if client_state == ClientState.sg_ready:
                    # Client received new SG weights before local training could complete
                    logging.debug(f'--- The training was too slow. A new set of SG modes are available. ---')
                else:
                    # Compute performance of local trained model on test dataset
                    acc, loss_test = self._validate(trained_model, self._validation_data,
                                                          **self._validation_kwargs)
                    # Create dict to store performance metrics for DB storage, GUI viewing
                    performance_dict = self.create_performance_data(False, acc, acc, loss_training, 0.0, loss_test)
                    logging.debug(f'--- Training accuracy: {acc} ---')

                    # Save trained model weights and performance metrics, then send to aggregator
                    self.save_model(trained_model_dict, performance_dict)
                    self.send_model()
                    logging.debug(f'--- Normal transition: The trained local models saved ---')

                    # Change client state to begin local model transmission
                    self.tran_state(ClientState.sending)

            time.sleep(1)


def run_client():
    """
        Required Configuration Parameters:

             config_file: str = None,
             simulation_flag=None,
             aggregator_ip_address: str = None,
             reg_port: str = None,
             exch_port: str = None,
             model_path: str = None,
             agent_running: bool = False
        """

    parser = argparse.ArgumentParser(description='Evaluate Client arguments')
    parser.add_argument('--config_path', metavar='cfp', type=str,
                        help='database server configuration path')
    parser.add_argument('--simulation', action='store_true', required=False, default=False,
                        help='simulation or not (if flag added simulation mode)')
    parser.add_argument('--aggregator_ip', metavar='ip', type=str, help="Ip address of the aggregator server")
    parser.add_argument('--reg_port', metavar='p', type=str, help="registration port")
    parser.add_argument('--exch_port', metavar='p', type=str, help="exchange port")
    parser.add_argument('--model_path', metavar='m_path', type=str, help="model path")
    parser.add_argument('--agent_running', action='store_true', required=False, default=False,
                        help='agent running or not (if flag added simulation mode)')

    args = parser.parse_args()

    cl = Client(config_file=args.config_path, simulation_flag=args.simulation,
                aggregator_ip_address=args.aggregator_ip,
                reg_port=args.reg_port, exch_port=args.exch_port, model_path=args.model_path,
                agent_running=args.agent_running)
    # cl.register_agent()
    cl.start_model_exchange_routine()
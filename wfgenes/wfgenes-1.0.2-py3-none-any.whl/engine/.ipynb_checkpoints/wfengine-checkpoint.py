"""A simple workflow engine"""

import threading
import uuid
import os
import subprocess as sp
from time import sleep
from fireworks.core.rocket_launcher import launch_rocket
from fireworks.queue.queue_launcher import launch_rocket_to_queue
from fireworks import Workflow, Firework, PyTask, FWorker
from fireworks.core.launchpad import LaunchPad
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
from fireworks.utilities.fw_utilities import get_fw_logger
from fireworks.utilities.fw_utilities import create_datestamp_dir
from prettytable import PrettyTable
from wfquery import WFQuery




class WFEngine(FWSerializable):
    """A simple engine to manage workflows"""

    thread = None
    event = None

    def __init__(self, launchpad, qadapter=None, wf_query=None, name=None,
                 launchdir='.', sleep_time=30):
        """
        Args:
            launchpad (LaunchPad): a launchpad to establish connection to a
                FireWorks database
            qadapter (CommonAdapter, None): a qadapter for submitting batch jobs
            wf_query (dict, None): a workflow query
            name (str, None): name of the engine; if None one will be generated
            launchdir (str): launch directory for both interactive and batch jobs
            sleep_time (int): launcher thread awakes every `sleep_time` seconds
        """
        self.launchpad = launchpad
        self.qadapter = qadapter
        self.wf_ids = ([] if wf_query is None else
                       self.launchpad.get_wf_ids(wf_query))
        self.launchdir = launchdir
        self.sleep_time = sleep_time
        self.name = name if name is not None else str(uuid.uuid4())
        if qadapter is not None:
            self.fworker_qlaunch = FWorker(name=self.name, category='batch')
        else:
            self.fworker_qlaunch = None
        self.fworker_rlaunch = FWorker(name=self.name, category='interactive')
    @property
    def name(self):
        """get the name of the engine"""
        return self.__name

    @name.setter
    def name(self, new_name):
        """set the name of the engine"""
        self.__name = new_name
        self.fworker_qlaunch = FWorker(name=self.__name, category='batch')
        self.fworker_rlaunch = FWorker(name=self.__name, category='interactive')

    def show_nodes_status(self):
        """Display the status summary of the nodes"""
        wfq = WFQuery(self.launchpad, wf_query={'nodes': {'$in': self.wf_ids}})
        fw_info = wfq.get_fw_info()
        if len(fw_info) > 0:
            columns = fw_info[0].keys()
            table = PrettyTable(columns)
            for fwk in fw_info:
                table.add_row([fwk[i] for i in columns])
            print(table)
        else:
            print('No nodes')

    def show_wf_status(self):
        """Display the status summary of the workflows"""
        wfq = WFQuery(self.launchpad, wf_query={'nodes': {'$in': self.wf_ids}})
        wfq.get_wf_info()

    def status_summary(self):
        """Display a status summary of workflows and nodes"""
        self.show_wf_status()
        print('Nodes summary:')
        self.show_nodes_status()

    def show_launcher_status(self):
        """Check whether a launcher thread is running"""
        if self.thread:
            if self.thread.is_alive():
                print('launcher thread is currently running')
            else:
                print('launcher thread not started')
        else:
            print('launcher thread not created')

    def status_detail(self, *fw_ids):
        """
        Print a detailed status of specified nodes

        Args:
            fw_ids ([int]): One or more fw_ids of the nodes
        """
        for fw_id in fw_ids:
            fw_dict = self.launchpad.get_fw_dict_by_id(fw_id)
            if fw_dict['state'] == 'FIZZLED':
                launch = fw_dict['launches'][-1]
                exception = launch['action']['stored_data']['_exception']
                print(str(fw_id), exception['_stacktrace'])
            return fw_dict    

    def get_failed(self):
        """
        Get failed job ids

        Returns:
            ([int]): a list of fw_ids of failed jobs
        """
        wfq = WFQuery(self.launchpad, wf_query={'nodes': {'$in': self.wf_ids}},
                      fw_query={'state': 'FIZZLED'})
        return wfq.get_fw_ids()

    def qlaunch(self, fw_id):
        """
        Launch a batch node by submitting a job to the queuing system

        Args:
            fw_id (int): a fwd_id of the node to launch
        """
        assert fw_id in self.get_fw_ids(), 'invalid fw_id'
        assert self.qadapter is not None, 'qadapter is not defined'
        assert self.fworker_qlaunch is not None, 'qlaunch worker is not defined'
        launch_rocket_to_queue(self.launchpad, self.fworker_qlaunch,
                               self.qadapter, reserve=True,
                               create_launcher_dir=True,
                               launcher_dir=self.launchdir,
                               fw_id=fw_id)

    def rlaunch(self, fw_id):
        """
        Launch an interactive node

        Args:
            fw_id (int): a fwd_id of the node to launch
        """
        assert fw_id in self.get_fw_ids(), 'invalid fw_id'
        init_dir = os.getcwd()
        log_dir = self.launchpad.get_logdir()
        logger = get_fw_logger('interactive', l_dir=log_dir)
        launch_dir = create_datestamp_dir(init_dir, logger, prefix='launcher_')
        try:
            os.chdir(launch_dir)
            launch_rocket(self.launchpad, self.fworker_rlaunch, fw_id)
        except Exception:
            os.chdir(init_dir)
            raise
        finally:
            os.chdir(init_dir)

    def check_lostjobs(self, time=14400):
        """
        Detect nodes that have been launched but not updated within the
        specified time. The state of such nodes is set to FIZZLED.

        Args:
            time (int): minimim time in seconds since last update, default: 4h

        Returns:
            lost_fw_ids ([int]): a list of fw_ids of the lost runs
        """
        fw_query = {'fw_id': {'$in': self.get_fw_ids()}}
        lostjobs = self.launchpad.detect_lostruns(expiration_secs=time,
                                                  fizzle=True, query=fw_query)
        lost_fw_ids = lostjobs[1]
        if len(lost_fw_ids) != 0:
            string = 'Lost jobs detected: {}.'
            print(string.format(lost_fw_ids))  # this should be made as log
        return lost_fw_ids

    @recursive_serialize
    def to_dict(self):
        """
        Dump the engine object to a dictionary

        Returns:
            (dict): a dictionary with all parameters needed to call __init__
        """
        return {'launchpad': self.launchpad,
                'qadapter': self.qadapter,
                'wf_query': {'nodes': {'$in': self.wf_ids}},
                'launchdir': self.launchdir,
                'name': self.__name,
                'sleep_time': self.sleep_time}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        """
        Construct an engine from a dictionary

        Args:
            m_dict (dict): a dict with all parameters needed to call __init__

        Returns:
            FWEngine object
        """
        launchpad = LaunchPad.from_dict(m_dict.get('launchpad'))
        qadapter = m_dict.get('qadapter')
        wf_query = m_dict.get('wf_query')
        name = m_dict.get('name')
        launchdir = m_dict.get('launchdir')
        sleep_time = m_dict.get('sleep_time')
        return cls(launchpad=launchpad, qadapter=qadapter, wf_query=wf_query,
                   name=name, launchdir=launchdir, sleep_time=sleep_time)

    def start(self):
        """Start a launcher thread"""
        if self.thread and self.thread.is_alive():
            print('Warning: launcher thread is already running')
        else:
            self.event = threading.Event()
            self.thread = threading.Thread(target=self.launcher,
                                           args=(self.event, ))
            self.thread.start()

            
    def stop(self):
        """Gracefully stop the launcher thread if it is running"""
        if self.event and not self.event.is_set():
            self.event.set()
            print('stopping the launcher thread')

    def launcher(self, stop_event):
        """
        The main loop of the launcher

        Args:
            stop_event (threading.Event): an object used to quit the launcher
        """
        while not stop_event.is_set():
            wf_query = {'nodes': {'$in': self.wf_ids}}
            fw_query = {'state': 'READY',
                        'spec._category': {'$in': ['batch', 'interactive']}}
            fw_ids = self.launchpad.get_fw_ids_in_wfs(wf_query, fw_query)
            for fw_id in fw_ids:
                input_config = self.launchpad.get_fw_dict_by_id(fw_id)
                category = input_config['spec'].get('_category', None)
                if category == 'batch':
                    # Launch the job on the cluster
                    self.qlaunch(fw_id)
                else:
                    # Launch the job locally
                    self.rlaunch(fw_id)
            sleep(self.sleep_time)
        print('launcher thread stopped')

    def get_fw_ids(self):
        """
        Return the list of nodes currently included in the engine

        Returns:
            (list): fw_ids of the nodes
        """
        wf_query = {'nodes': {'$in': self.wf_ids}}
        return self.launchpad.get_fw_ids_in_wfs(wf_query)

    def add_node(self, func, inputs, outputs=[], name=None, kwargs={}):
        """
        Add a python function node to an existing workflow

        Args:
            func (str): a function name with an optional module name in the
                format 'module.function'
            inputs ([tuple]): a list of positional arguments for the provided
                function. Every input is described by a tuple
                (fw_id, name, value) with the following elements:
                    The fw_id of a parent node providing the input; if the
                        input is provided as a constant value, then None should
                        be specified.
                    The name of the input as provided in the list of outputs of
                    the parent node;
                    The value of the input; if output data from a parent node
                        is used as input, then this should be set to None.

            outputs ([str]): names of the outputs
        """

        node_ids = list(set(i[0] for i in inputs if i[0] is not None))
        # check that all parent nodes are in the managed wfs
        msg = 'some parent nodes are not in engine'
        assert all(n in self.get_fw_ids() for n in node_ids), msg
        # check that all parent nodes are in one worfklow
        qres = self.launchpad.get_wf_ids({'nodes': {'$in': node_ids}})
        assert len(qres) > 0, 'no valid parent nodes defined'
        assert len(qres) == 1, 'some parent nodes are not in one workflow'
        # later, add all upstream fireworks of the nodes from other workflows
        # later check the outputs of parent nodes to match the inputs
        inps = [i[1] for i in inputs]
        # check that any equal inputs have the same source
        msg = 'input "{}" has more than one source'
        for inp in set(inps):
            sources = set(i[0] for i in inputs if i[1] == inp)
            assert len(sources) == 1, msg.format(inp)

        task = PyTask(func=func, inputs=inps, outputs=outputs, kwargs=kwargs)
        spec = {}
        spec['_dupefinder'] = {'_fw_name': 'DupeFinderExact'}
        spec['_category'] = 'interactive'  # fix later as arg
        # spec['_fworker'] = ? (if category not interactive) fix this
        # spec['_qadapter'] = ? (if category not interactive) fix this
        locs = {i[1]: i[2] for i in inputs if i[0] is None}
        spec.update(locs)
        wflow = Workflow([Firework(tasks=[task], spec=spec, name=name)])
        self.launchpad.append_wf(wflow, fw_ids=node_ids)

    def add_workflow(self, workflow=None, fw_id=None):
        """
        Add a workflow to the engine
        Either a workflow object or a fw_id must be defined.

        Args:
            workflow (Workflow, None): a workflow object
            fw_id (int, None): a fw_id of a workflow existing on the launchpad
        """
        assert workflow is not None or fw_id is not None
        assert not (workflow is not None and fw_id is not None)
        if fw_id is None:
            assert isinstance(workflow, (Workflow, Firework))
            fw_id = list(self.launchpad.add_wf(workflow).values())[0]
        else:
            assert isinstance(fw_id, int)
            assert fw_id not in self.get_fw_ids(), 'workflow already in engine'
            fw_ids = self.launchpad.get_fw_ids({'fw_id': fw_id})
            assert len(fw_ids) == 1, 'no workflow with this id'
        self.wf_ids.append(fw_id)
        self.launchpad.m_logger.info('Added wf_id: {}'.format(fw_id))

    def remove_workflow(self, fw_id):
        """
        Remove a workflow from the engine (but not deleted from launchpad)

        Args:
            fw_id (int): a fw_id of a node in the workflow to remove
        """
        self.wf_ids.remove(fw_id)
        self.launchpad.m_logger.info('Removed wf_id: {}'.format(fw_id))

    def update_node(self, fw_id, update_dict):
        """
        Update (modify) a workflow node
        Only nodes in WAITING, READY and FIZZLED states can be modified.

        Args:
           fw_id (int): the fw_id of the node to modify
           update_dict (dict): a dictionary with the updates to perform
        """
        state = self.launchpad.get_fw_by_id(fw_id).state
        assert state in ['WAITING', 'READY', 'FIZZLED']
        self.launchpad.update_spec([fw_id], update_dict)

    def rerun_node(self, fw_id):
        """
        Rerun a workflow node
        Only nodes in COMPLETED and FIZZLED states can be rerun.

        Args:
            fw_id: the fw_id of the node to rerun
        """
        state = self.launchpad.get_fw_by_id(fw_id).state
        assert state in ['COMPLETED', 'FIZZLED', 'RESERVED']
        self.launchpad.rerun_fw(fw_id)

    def update_rerun_node(self, fw_id, update_dict):
        """
        Update (modify) and rerun a workflow node combined in one function
        Only nodes in COMPLETED, WAITING, READY and FIZZLED states can be
        processed.

        Args:
            fw_id (int): the fw_id of the node to process
            update_dict (dict): a dictionary with the updates to perform
        """
        state = self.launchpad.get_fw_by_id(fw_id).state
        assert state in ['COMPLETED', 'WAITING', 'READY', 'FIZZLED']
        if state == 'COMPLETED':
            self.launchpad.defuse_fw(fw_id)
            self.launchpad.update_spec([fw_id], update_dict)
            self.launchpad.reignite_fw(fw_id)
        elif state in ['WAITING', 'READY']:
            self.launchpad.update_spec([fw_id], update_dict)
        elif state == 'FIZZLED':
            self.launchpad.update_spec([fw_id], update_dict)
            self.launchpad.rerun_fw(fw_id)

    def cancel_job(self, fw_id, restart=False, pause=False):
        """
        Cancel the execution of a node in RESERVED or RUNNING state
        Either restart or pause can be set to True if required.

        Args:
            fw_id (int): the fw_id of the node to cancel
            restart (bool): rerun after cancelling a RUNNING node
            pause (bool): pause after cancelling a RUNNING node
        """
        assert not (restart and pause)
        state = self.launchpad.get_fw_by_id(fw_id).state
        assert state in ['RESERVED', 'RUNNING'], 'Job not in necessary state'
        fw_dict = self.launchpad.get_fw_dict_by_id(fw_id)
        category = fw_dict['spec'].get('_category', None)
        assert category == 'batch', 'Not a batch job'
        reserve_id = self.launchpad.get_reservation_id_from_fw_id(fw_id)
        self.exec_cancel(reserve_id)
        self.check_jobcancel(reserve_id)
        if state == 'RESERVED':
            self.launchpad.cancel_reservation_by_reservation_id(reserve_id)
        elif state == 'RUNNING':
            assert (restart is True or pause is True), 'Either restart or pause should be true'
            if restart:
                self.launchpad.rerun_fw(fw_id)
            else:
                self.launchpad.defuse_fw(fw_id)

    def exec_cancel(self, res_id):
        """Execute the slurm cancel command"""
        if os.system(f'scancel {res_id}') != 0:
            raise RuntimeError('Error executing command \"scancel\"')
        self.launchpad.m_logger.info('Cancelled res_id: {}'.format(res_id))

    def check_jobcancel(self, res_id):
        """Execute the slurm sacct command"""
        output = sp.getoutput(f'sacct -j {res_id}')
        if 'CANCELLED' not in output:
            raise RuntimeError('Error job is not cancelled')
    


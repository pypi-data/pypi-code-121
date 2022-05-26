# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Generic process to automatically setup a cluster from within a job.
Leverages MPI to synchronize setup between nodes, and execute
a provided command to start/stop (ex: ray start).

This script is the generic class on which other framework-specific
classes will be derived (ex: Ray, Dask, ...).
"""
import logging
import subprocess
from typing import Any, List
import uuid
import time

from shrike._core import experimental
from shrike.distributed import EXPERIMENTAL_WARNING_MSG
from shrike.distributed.mpi_driver import MultiNodeMPIDriver


class ClusterAutoSetupHandler:
    # NOTE: not even sure we need tags, but let's do it
    COMM_TAG_CLUSTER_SETUP = 42
    COMM_TAG_SETUP_FINISHED = 43
    COMM_TAG_CLUSTER_SHUTDOWN = 44

    def __init__(self, mpi_init_mode: int = None):
        """Generic initialization for all script classes.

        Args:
            mpi_init_mode (int): mode to initialize MPI (default: THREAD)
        """
        self.logger = logging.getLogger(__name__)

        # keep those for initialization later
        self.multinode_driver = MultiNodeMPIDriver(mpi_init_mode=mpi_init_mode)

        # this will be used to collect cluster config
        self._setup_config = {}

    def run_cli_command(self, cli_command: List[str], timeout: int = 60):
        """Runs subprocess for a cli setup command"""
        self.logger.info(f"Launching cli with command: {cli_command}")
        cli_command_call = subprocess.run(
            cli_command,
            # stdout=PIPE,
            # stderr=PIPE,
            universal_newlines=True,
            check=False,  # will not raise an exception if subprocess fails
            timeout=timeout,  # TODO: more than a minute would be weird?
            # env=custom_env
        )
        self.logger.info(f"return code: {cli_command_call.returncode}")

        if cli_command_call.returncode != 0:
            raise RuntimeError("Cli command returned code != 0")

        return cli_command_call.returncode

    #################
    # SETUP METHODS #
    #################

    def setup_config_add_key(self, key: str, value: Any) -> None:
        self._setup_config[key] = value

    def setup_config_get_key(self, key: str, default_value: Any = None) -> Any:
        return self._setup_config.get(key, default_value)

    # For specific setups, override methods below

    def setup_local(self):
        """Setup method if custom_sync_setup=False"""
        self.logger.info(f"{self.__class__.__name__}.setup_local() called.")

    def setup_head_node(self):
        """Setup to run only on head node"""
        self.logger.info(
            f"{self.__class__.__name__}.setup_head_node() called to set up HEAD node."
        )
        self.setup_config_add_key("_session_id", str(uuid.uuid4()))

    def setup_cluster_node(self):
        """Setup to run only on non-head cluster nodes"""
        self.logger.info(f"{self.__class__.__name__}.setup_cluster_node() called.")

    def head_node_teardown(self):
        """Un-setup a cluster node"""
        self.logger.info(f"{self.__class__.__name__}.head_node_teardown() called.")

    def cluster_node_teardown(self):
        """Un-setup a cluster node"""
        self.logger.info(f"{self.__class__.__name__}.cluster_node_teardown() called.")

    ############
    # MPI COMM #
    ############

    def broadcast_config_from_head_to_cluster_nodes(self):
        """[HEAD only] Sends the cluster setup params to each non-head node"""
        self.logger.info(
            f"Sending cluster setup from head to cluster nodes: {self._setup_config}"
        )
        for i in range(1, self.multinode_driver.get_multinode_config().world_size):
            self.multinode_driver.get_comm().send(
                self._setup_config,
                i,
                tag=ClusterAutoSetupHandler.COMM_TAG_CLUSTER_SETUP,
            )

    def listen_cluster_setup_from_head_node(self):
        """[NODE only] Waits for head node to send cluster setup params"""
        self._setup_config = self.multinode_driver.get_comm().recv(
            source=0, tag=ClusterAutoSetupHandler.COMM_TAG_CLUSTER_SETUP
        )
        self.logger.info(f"Obtained cluster setup from head node: {self._setup_config}")

    def wait_on_nodes_setup_ready(self):
        """[HEAD only] Waits for each node to report completion of their setup"""
        self.logger.info("Checking setup status from each node...")

        # loop on each node in the world and wait for status
        for i in range(1, self.multinode_driver.get_multinode_config().world_size):
            status = self.multinode_driver.get_comm().recv(
                source=i, tag=ClusterAutoSetupHandler.COMM_TAG_SETUP_FINISHED
            )
            self.logger.info(f"Node #{i}: {status}")

            if status != "OK":
                raise RuntimeError(f"Node #{i} failed to setup, status=={status}.")

    def report_node_setup_complete(self):
        """[NODE only] Report to head that this node setup is complete"""
        self.logger.info("Reporting status OK to head node.")
        self.multinode_driver.get_comm().send(
            "OK", 0, tag=ClusterAutoSetupHandler.COMM_TAG_SETUP_FINISHED
        )

    def broadcast_shutdown_signal(self):
        """[HEAD only] Sends message to shutdown to all nodes"""
        for i in range(1, self.multinode_driver.get_multinode_config().world_size):
            self.logger.info(f"Broadcasting shutdown message to node #{i}")
            self.multinode_driver.get_comm().send(
                "SHUTDOWN", i, tag=ClusterAutoSetupHandler.COMM_TAG_CLUSTER_SHUTDOWN
            )

    def non_block_wait_for_shutdown(self):
        """[NODE only] Checks if head node has sent shutdown message"""
        return self.multinode_driver.get_comm().iprobe(
            source=0, tag=ClusterAutoSetupHandler.COMM_TAG_CLUSTER_SHUTDOWN
        )

    ##################
    # SCRIPT METHODS #
    ##################

    def initialize_run(self):
        """Initialize the component run, opens/setups what needs to be"""
        self.logger.info(f"Call to {self.__class__.__name__}.initialize_run()...")

        # initialize mpi comm
        self.multinode_driver.initialize()
        multinode_config = self.multinode_driver.get_multinode_config()

        if multinode_config.multinode_available:
            # initialize setup accross nodes
            if multinode_config.main_node:
                # run setup on head node
                self.setup_head_node()

                # send cluster config to all other nodes
                self.broadcast_config_from_head_to_cluster_nodes()

                # then wait for all nodes to finish setup
                self.wait_on_nodes_setup_ready()
            else:
                # get cluster setup from head node using mpi
                self.listen_cluster_setup_from_head_node()

                # run setup on cluster node
                self.setup_cluster_node()

                # then report that setup is complete
                self.report_node_setup_complete()
        else:
            # run custom method for setup
            self.setup_local()

    def finalize_run(self):
        """Finalize the run, close what needs to be"""
        self.logger.info(f"Call to {self.__class__.__name__}.finalize_run()...")

        multinode_config = self.multinode_driver.get_multinode_config()

        if multinode_config.multinode_available:
            # properly teardown all nodes
            if multinode_config.main_node:
                # run teardown on head node
                self.head_node_teardown()

                # send signal to teardown to each node
                self.broadcast_shutdown_signal()
            else:
                # wait for teardown signal from head node
                while True:
                    self.logger.info("Waiting for teardown signal from HEAD node...")

                    if self.non_block_wait_for_shutdown():
                        break

                    time.sleep(10)

                # run teardown on cluster
                self.cluster_node_teardown()

        # clean exit from driver
        self.multinode_driver.finalize()


###########################
# USER FRIENDLY FUNCTIONS #
###########################

_SETUP_HANDLER = None


@experimental(EXPERIMENTAL_WARNING_MSG)
def init() -> Any:
    """User-friendly function to initialize the script using ClusterAutoSetupHandler"""
    global _SETUP_HANDLER
    _SETUP_HANDLER = ClusterAutoSetupHandler()
    _SETUP_HANDLER.initialize_run()

    if _SETUP_HANDLER.multinode_driver.get_multinode_config().main_node:
        return _SETUP_HANDLER.multinode_driver.get_multinode_config()
    else:
        return None


@experimental(EXPERIMENTAL_WARNING_MSG)
def shutdown():
    """User-friendly function to teardown the script using ClusterAutoSetupHandler"""
    global _SETUP_HANDLER
    if _SETUP_HANDLER is not None:
        _SETUP_HANDLER.finalize_run()

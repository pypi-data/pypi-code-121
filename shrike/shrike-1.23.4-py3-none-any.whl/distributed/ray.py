# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Helper code to run Ray distributed scripts [EXPERIMENTAL]
"""
import logging
import uuid
import time
import socket

import ray

from shrike._core import experimental
from shrike.distributed import EXPERIMENTAL_WARNING_MSG
from shrike.distributed.cluster_auto_setup import ClusterAutoSetupHandler


class RayClusterSetupHandler(ClusterAutoSetupHandler):
    def __init__(self):
        """Constructor"""
        super().__init__()

        # ray init settings
        self.head_address = "auto"
        self.head_port = 6379
        self.redis_password = None

    #################
    # SETUP METHODS #
    #################

    def setup_local(self):
        """Setup method if custom_sync_setup=False"""
        self.logger.info(f"{self.__class__.__name__}.setup_local() called.")
        # nothing to do here

    def setup_head_node(self):
        """Setup to run only on head node"""
        self.logger.info(
            f"{self.__class__.__name__}.setup_head_node() called to set up HEAD node."
        )
        # create setup config
        local_hostname = socket.gethostname()
        local_ip = socket.gethostbyname(local_hostname)
        self.logger.info(f"Obtained IP from socket: {local_ip}")

        self.head_address = local_ip
        self.head_port = 6379
        self.redis_password = str(uuid.uuid4())

        # record what's needed to setup cluster nodes
        self.setup_config_add_key("head_address", self.head_address)
        self.setup_config_add_key("head_port", self.head_port)
        self.setup_config_add_key("redis_password", self.redis_password)

        # on head node, init should use "auto"
        self.head_address = "auto"

        # run ray cli
        ray_setup_command = [
            "ray",
            "start",
            "--head",
            f"--port={self.head_port}",
            f"--redis-password={self.redis_password}",
        ]
        self.run_cli_command(ray_setup_command)

    def setup_cluster_node(self):
        """Setup to run only on non-head cluster nodes"""
        self.logger.info(f"{self.__class__.__name__}.setup_cluster_node() called")
        self.head_address = self.setup_config_get_key("head_address")
        self.head_port = self.setup_config_get_key("head_port")
        self.redis_password = self.setup_config_get_key("redis_password")

        # run ray cli
        ray_setup_command = [
            "ray",
            "start",
            f"--address={self.head_address}:{self.head_port}",
            f"--redis-password={self.redis_password}",
        ]
        self.run_cli_command(ray_setup_command)

    def head_node_teardown(self):
        """Un-setup a cluster node"""
        self.logger.info(f"{self.__class__.__name__}.head_node_teardown() called")
        self.run_cli_command(["ray", "stop", "--force", "-v"])

    def cluster_node_teardown(self):
        """Un-setup a cluster node"""
        self.logger.info(f"{self.__class__.__name__}.cluster_node_teardown() called")
        self.run_cli_command(["ray", "stop", "--force", "-v"])


###########################
# USER FRIENDLY FUNCTIONS #
###########################

_SETUP_HANDLER = None


@experimental(EXPERIMENTAL_WARNING_MSG)
def init(address=None, _redis_password=None):
    """User-friendly function to initialize the script using ClusterAutoSetupHandler"""
    global _SETUP_HANDLER
    _SETUP_HANDLER = RayClusterSetupHandler()
    _SETUP_HANDLER.initialize_run()

    multinode_config = _SETUP_HANDLER.multinode_driver.get_multinode_config()
    if multinode_config is None:
        raise Exception(
            "init() needs multinode_driver.get_multinode_config() which is None."
        )
    elif not multinode_config.multinode_available:
        # we're running single node or local
        return ray.init(address=address, _redis_password=_redis_password)
    elif multinode_config.main_node:
        if _SETUP_HANDLER.redis_password is None:
            ray_init_retval = ray.init(address="auto")
        elif isinstance(_SETUP_HANDLER.redis_password, str):
            ray_init_retval = ray.init(
                address="auto", _redis_password=_SETUP_HANDLER.redis_password
            )
        else:
            raise ValueError(
                "Value in redis_password is of wrong type"
                + " {type(_SETUP_HANDLER.redis_password)}"
            )

        # making absolutely sure all nodes are there...
        for _ in range(60):
            logging.getLogger(__name__).info(
                "Waiting for ray cluster to reach available nodes size..."
                + f"[{len(ray.nodes())}/{multinode_config.world_size}]"
            )
            if len(ray.nodes()) >= multinode_config.world_size:
                break
            time.sleep(1)
        else:
            raise Exception(
                "Could not reach maximum number of nodes before 60 seconds."
            )

        return ray_init_retval
    else:
        return None


@experimental(EXPERIMENTAL_WARNING_MSG)
def shutdown():
    """User-friendly function to teardown the script using ClusterAutoSetupHandler"""
    global _SETUP_HANDLER
    if _SETUP_HANDLER is not None:
        _SETUP_HANDLER.finalize_run()

        # use shutdown only if we're on main node
        if _SETUP_HANDLER.multinode_driver.get_multinode_config().main_node:
            ray.shutdown()

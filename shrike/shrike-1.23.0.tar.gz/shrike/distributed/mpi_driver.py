# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
"Driver" for MPI communication
"""
import logging
import traceback
from dataclasses import dataclass


@dataclass
class MultiNodeConfig:
    world_size: int = 1
    world_rank: int = 0
    multinode_available: bool = False
    main_node: bool = True


class MultiNodeMPIDriver:
    """Handling MPI initialization in a separate class
    so we can patch/mock it during unit testing of MultiNodeScript"""

    def __init__(self, mpi_init_mode=None):
        """Constructor"""
        self.logger = logging.getLogger(__name__)
        self._multinode_config = None
        self._mpi_module = None
        self._mpi_init_mode = mpi_init_mode

    def _mpi_import(self):
        self.logger.info("Importing mpi4py...")
        # doing our own initialization of MPI to have fine-grain control
        import mpi4py

        mpi4py.rc.initialize = False
        mpi4py.rc.finalize = False
        from mpi4py import MPI

        return MPI

    def get_multinode_config(self) -> MultiNodeConfig:
        """Get internal multinode config"""
        if self._multinode_config:
            return self._multinode_config
        else:
            raise Exception("Multinode config is None, use initialize() first.")

    def get_comm(self):
        """Returns the communicator"""
        if self._mpi_module:
            return self._mpi_module.COMM_WORLD
        else:
            raise Exception(
                "MPI.COMM_WORLD was requested but MPI was never initialized"
                + "please use mpi_init_mode!=None."
            )

    def initialize(self):
        """Initialize the driver"""
        self.logger.info(f"Call to {self.__class__.__name__}.initialize()")
        self._mpi_module = self._mpi_import()

        # init mpi and use comm to detect mpi config
        try:
            if self._mpi_init_mode is None:
                self.logger.info("Running MPI.Init()")
                self._mpi_module.Init()
            else:
                self.logger.info(
                    f"Running MPI.Init_thread(required={self._mpi_init_mode})"
                )
                self._mpi_module.Init_thread(required=self._mpi_init_mode)
        except self._mpi_module.Exception:
            self.logger.warning(
                f"Exception occured during MPI init:\n{traceback.format_exc()}"
            )

        _comm = self._mpi_module.COMM_WORLD
        try:
            self._multinode_config = MultiNodeConfig(
                _comm.Get_size(),  # world_size
                _comm.Get_rank(),  # world_rank
                (_comm.Get_size() > 1),  # mpi_available
                (_comm.Get_rank() == 0),  # main_node
            )
            self.logger.info(f"MPI detection results: {self._multinode_config}")
        except BaseException:
            self.logger.warning(traceback.format_exc())
            self._multinode_config = MultiNodeConfig(
                1,  # world_size
                0,  # world_rank
                False,  # mpi_available
                True,  # main_node
            )
            self.logger.critical(
                "MPI detection failed, switching to single node:"
                + f" {self._multinode_config}"
                + f" see traceback below:\n{traceback.format_exc()}"
            )

    def finalize(self):
        """Finalize/close resources used by the driver"""
        self.logger.info(f"Call to {self.__class__.__name__}.finalize()")
        if self._mpi_module is None:
            self.logger.warning(
                "MPIHandler.finalize() was called but MPI was never instanciated"
            )
        elif self._mpi_module.Is_initialized() and not self._mpi_module.Is_finalized():
            self.logger.info("MPI was initialized, calling MPI.finalize()")
            self._mpi_module.Finalize()
        else:
            self.logger.warning(
                "MPIHandler.finalize() was called,"
                + f" but MPI.Is_initialized={self._mpi_module.Is_initialized()}"
                + f"and MPI.Is_finalized={self._mpi_module.Is_finalized()}"
            )

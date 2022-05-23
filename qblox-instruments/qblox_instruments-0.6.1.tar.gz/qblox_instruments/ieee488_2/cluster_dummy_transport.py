# ----------------------------------------------------------------------------
# Description    : Transport layer (abstract, IP, file, dummy)
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import json

from typing import Dict, Optional
from qblox_instruments import ClusterType
from qblox_instruments.ieee488_2 import DummyTransport, QcmQrmDummyTransport


# -- class -------------------------------------------------------------------

class ClusterDummyTransport(DummyTransport):
    """
    Class to replace Cluster device with dummy device to support software
    stack testing without hardware. The class implements all mandatory,
    required and Cluster specific SCPI calls. Call reponses are largely
    artifically constructed to be inline with the call's functionality (e.g.
    `*IDN?` returns valid, but artificial IDN data.) To assist development,
    the Q1ASM assembler has been completely implemented. Please have a look
    at the call's implentation to know what to expect from its response.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        dummy_cfg: Dict,
        scope_acq_cfg_format: str,
        qcm_seq_cfg_format: str,
        qrm_seq_cfg_format: str,
    ):
        """
        Create Cluster dummy transport class.

        Parameters
        ----------
        dummy_cfg : Dict
            Dictionary of dummy module types (e.g. Cluster QCM, Cluster QRM).
            Each key of the dictionary is a slot index with a dummy type
            specification of type :class:`~qblox_instruments.ClusterType`.
        scope_acq_cfg_format : str
            Configuration format based on
            `struct.pack <https://docs.python.org/3/library/struct.html>`_
            format used to calculate scope acquisition configuration
            transaction size.
        qcm_seq_cfg_format : str
            QCM sequencer configuration format based on
            `struct.pack <https://docs.python.org/3/library/struct.html>`_
            format used to calculate scope acquisition configuration
            transaction size.
        qrm_seq_cfg_format : str
            QRM sequencer configuration format based on
            `struct.pack <https://docs.python.org/3/library/struct.html>`_
            format used to calculate scope acquisition configuration
            transaction size.

        Returns
        ----------

        Raises
        ----------
        """

        # Initialize base class
        super().__init__(
            dummy_cfg["0"] if "0" in dummy_cfg else ClusterType._CLUSTER_MM
        )

        # Set number of slots
        self._num_slots = 20

        # Configure module dummy transports
        self._modules = {}
        for slot_idx in range(1, self._num_slots + 1):
            if str(slot_idx) in dummy_cfg:
                self._modules[str(slot_idx)] = QcmQrmDummyTransport(
                    dummy_cfg[str(slot_idx)],
                    scope_acq_cfg_format,
                    qcm_seq_cfg_format,
                    qrm_seq_cfg_format,
                )
            else:
                self._modules[str(slot_idx)] = None

        # Set command list
        self._cmds["STATus:GENeral:STATE?"] = self._get_system_state
        self._cmds["*MODS?"] = self._get_mods_info
        self._cmds["BP:MODules?"] = self._get_modules_present

    # ------------------------------------------------------------------------
    def _execute_cmd(
        self,
        cmd_parts: list,
        cmd_params: list,
        cmd_args: list,
        bin_in: Optional[bytes] = None
    ) -> None:
        """
        Execute associated command method found in command dictionary.
        If the command is intended for a slot as indicated by the first
        command part being "SLOT#", the command is executed by the
        associated module.

        Parameters
        ----------
        cmd_parts : list
            Reformated command sections
        cmd_params : list
            Command parameters
        cmd_args : list
            Command arguments
        bin_in : Optional[bytes]
            Binary data that needs to be send by the command.

        Returns
        ----------

        Raises
        ----------
        """

        # If command is intended for a slot, remove the slot specification
        # and execute the command on the module instead.
        if cmd_parts[0] == "SLOT#":
            cmd_parts.pop(0)
            slot = cmd_params.pop(0)
            if slot in self._modules:
                mod = self._modules[slot]
                mod._execute_cmd(cmd_parts, cmd_params, cmd_args, bin_in)

                # Copy results and errors from module.
                self._data_out = mod._data_out
                self._bin_out = mod._bin_out
                for error in mod._system_error:
                    self._system_error.append(error)
                mod._system_error = []
            else:
                self._system_error.append(
                    "Module in slot {} is not available.".format(slot)
                )
        else:
            super()._execute_cmd(cmd_parts, cmd_params, cmd_args, bin_in)

    # ------------------------------------------------------------------------
    def _get_system_state(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        """
        Get system status.

        Parameters
        ----------
        cmd_params : list
            Command parameters indicated by '#' in the command.
        cmd_args : list
            Command arguments.
        bin_in : bytes
            Binary input data.

        Returns
        ----------

        Raises
        ----------
        """

        super()._get_system_state(cmd_params, cmd_args, bin_in)
        for slot_idx in self._modules:
            if self._modules[slot_idx] is not None:
                self._modules[slot_idx]._get_system_state(
                    cmd_params,
                    cmd_args,
                    bin_in
                )

                flags = self._modules[slot_idx]._data_out.split(";")[1]
                flags = flags.split(",")[:-1]
                flags = ["SLOT {} {}".format(slot_idx, flag) for flag in flags]

                self._data_out += ",".join(flags)
                if len(flags) > 0:
                    self._data_out += ","

    # ------------------------------------------------------------------------
    def _get_mods_info(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        """
        Get information about the modules in the Cluster (i.e. IDN and RF indication).

        Parameters
        ----------
        cmd_params : list
            Command parameters indicated by '#' in the command.
        cmd_args : list
            Command arguments.
        bin_in : bytes
            Binary input data.

        Returns
        ----------

        Raises
        ----------
        """

        mod_info = {}
        for slot_idx in self._modules:
            if self._modules[slot_idx] is not None:
                self._modules[slot_idx]._get_idn([], [], None)
                mod_info["SLOT " + slot_idx] = {
                    "IDN": self._modules[slot_idx]._data_out,
                    "RF": self._modules[slot_idx].is_rf_type
                }

        self._bin_out = self._encode_bin(json.dumps(mod_info).encode("utf-8"))

    # ------------------------------------------------------------------------
    def _get_modules_present(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        """
        Get modules present in the Cluster.

        Parameters
        ----------
        cmd_params : list
            Command parameters indicated by '#' in the command.
        cmd_args : list
            Command arguments.
        bin_in : bytes
            Binary input data.

        Returns
        ----------

        Raises
        ----------
        """

        mod_present = 0
        for slot_idx in self._modules:
            if self._modules[slot_idx] is not None:
                mod_present |= 1 << (int(slot_idx) - 1)

        self._data_out = mod_present

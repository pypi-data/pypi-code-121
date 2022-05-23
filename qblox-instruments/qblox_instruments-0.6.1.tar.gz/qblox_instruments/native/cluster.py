# ----------------------------------------------------------------------------
# Description    : Cluster native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from typing import Any, Dict, Optional, Tuple, Union
from functools import partial
from qblox_instruments import InstrumentClass, InstrumentType, TypeHandle
from qblox_instruments import DeviceInfo, resolve
from qblox_instruments.ieee488_2 import IpTransport, ClusterDummyTransport
from qblox_instruments.scpi import Cluster as ClusterScpi

import qblox_instruments.native.generic_func as gf


# -- class -------------------------------------------------------------------

class Cluster(ClusterScpi):
    """
    Class that provides the native API for the Cluster. It provides methods
    to control all functions and features provided by the Cluster.

    Note that the bulk of the functionality of this class is contained in the
    :mod:`~qblox_instruments.native.generic_func` module so that this
    functionality can be shared between instruments.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        identifier: str,
        port: Optional[int] = None,
        debug: Optional[int] = None,
        dummy_cfg: Optional[Dict] = None,
    ):
        """
        Creates Cluster native interface object.

        Parameters
        ----------
        identifier : str
            Instrument identifier. See :func:`~qblox_instruments.resolve()`
            for more information.
        port : Optional[int]
            Instrument port. If None, this will be determined automatically.
        debug : Optional[int]
            Debug level (0 | None = normal, 1 = no version check, >1 = no
            version or error checking).
        dummy_cfg : Optional[Dict]
            Configure as dummy using this configuration. For each slot that
            needs to be occupied by a module add the slot index as key and
            specify the type of module in the slot using the type
            :class:`~qblox_instruments.ClusterType`.

        Returns
        ----------

        Raises
        ----------
        RuntimeError
            Instrument cannot be reached due to invalid IP configuration.
        ConnectionError
            Instrument type is not supported.
        """

        # Create transport layer (dummy or socket interface)
        if dummy_cfg is not None:
            self._transport = ClusterDummyTransport(
                dummy_cfg,
                gf.get_acq_scope_config_format(),
                gf.get_sequencer_config_format(False),
                gf.get_sequencer_config_format(True),
            )
            if debug is None:
                debug = 1
        else:
            addr_info = resolve(identifier)
            if addr_info.protocol != "ip":
                raise RuntimeError(
                    "Instrument cannot be reached due to invalid IP configuration. "
                    "Use qblox-pnp tool to rectify; serial number is {}".format(addr_info.address)
                )
            host = addr_info.address
            if port is None:
                port = addr_info.scpi_port
            self._transport = IpTransport(host=host, port=port)
            if debug is None:
                debug = 0

        # Initialize parent class.
        super().__init__(self._transport, debug)

        # Set instrument type handle
        model = DeviceInfo.from_idn(super()._get_idn()).model
        self._type_handle = TypeHandle(model)
        if not self._type_handle.is_mm_type:
            raise ConnectionError(
                "Unsupported instrument type detected ({})".format(self.instrument_type)
            )

        # Get a dictionary of SCPI and native functions that the functions in
        # the generic_func module require to operate. Create a function
        # reference container that we use to pass references to those functions
        # to functions in the generic_func module.
        self._funcs = gf.FuncRefs(self)
        for attr_name in self._funcs.funcs.keys():
            if (self._funcs.funcs[attr_name] is None and
               hasattr(super(), attr_name)):
                self._funcs.register(getattr(super(), attr_name))

        # Set module specific type and FuncRefs handles
        self._mod_handles = {}
        slot_info = self._get_mods_info()
        for slot_str in slot_info.keys():
            slot = int(slot_str.split(" ")[1])

            # Module type handle
            model = DeviceInfo.from_idn(slot_info[slot_str]["IDN"]).model
            mod_type_handle = TypeHandle(model)
            mod_type_handle._is_rf_type = bool(slot_info[slot_str]["RF"])

            # Module FuncRefs
            mod_funcs = self._create_module_funcrefs(slot)

            # Update module handles dictionary
            self._mod_handles[str(slot)] = {
                "type_handle": mod_type_handle,
                "func_refs": mod_funcs,
            }

    # ------------------------------------------------------------------------
    def _create_module_funcrefs(self, slot: int) -> gf.FuncRefs:
        """
        Create function reference container object for a specific slot. This
        means that SCPI and native layer methods are customized using
        functools.partial to operate on a specific slot. The resulting methods
        are added to the function reference container, so that they can be used
        by the generic_func module.

        Parameters
        ----------
        slot : int
            Slot index to create function reference container for.

        Returns
        ----------
        FuncRefs
            Function reference container specific to single slot.


        Raises
        ----------
        """

        # Non-slot specific attributes
        funcs = gf.FuncRefs(self)
        funcs.register(getattr(super(), "_write"))
        funcs.register(getattr(super(), "_read_bin"))
        funcs.register(getattr(super(), "_flush_line_end"))

        # Slot specific attributes
        rb = super()._read_bin
        part_cmd = "SLOT{}:SEQuencer".format(slot)
        awg_wlist_rb = gf.create_read_bin(rb, part_cmd + "{}:AWG:WLISt?")
        acq_wlist_rb = gf.create_read_bin(rb, part_cmd + "{}:ACQ:WLISt?")
        acq_data_rb = gf.create_read_bin(rb, part_cmd + '{}:ACQ:ALISt:ACQuisition:DATA? "{}"')
        acq_list_rb = gf.create_read_bin(rb, part_cmd + "{}:ACQ:ALISt?")

        funcs.register(awg_wlist_rb, "_get_awg_waveforms")
        funcs.register(acq_wlist_rb, "_get_acq_weights")
        funcs.register(acq_data_rb, "_get_acq_acquisition_data")
        funcs.register(acq_list_rb, "_get_acq_acquisitions")
        funcs.register(partial(self._is_qrm_type, slot), "is_qrm_type")

        # Remaining slot specific attributes
        for attr_name in funcs.funcs.keys():
            if (funcs.funcs[attr_name] is None and
               hasattr(super(), attr_name)):
                attr = partial(getattr(super(), attr_name), slot)
                funcs.register(attr, attr_name)

        return funcs

    # ------------------------------------------------------------------------
    @property
    def instrument_class(self) -> InstrumentClass:
        """
        Get instrument class (e.g. Pulsar, Cluster).

        Parameters
        ----------

        Returns
        ----------
        InstrumentClass
            Instrument class

        Raises
        ----------
        """

        return self._type_handle.instrument_class

    # ------------------------------------------------------------------------
    @property
    def instrument_type(self) -> InstrumentType:
        """
        Get instrument type (e.g. MM, QRM, QCM).

        Parameters
        ----------

        Returns
        ----------
        InstrumentType
            Instrument type

        Raises
        ----------
        """

        return self._type_handle.instrument_type

    # ------------------------------------------------------------------------
    def _present_at_init(self, slot: int) -> Tuple:
        """
        Get an indication of module presence during initialization of this
        object for a specific slot in the Cluster and return the associated
        module type handle and function reference container if present.

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        TypeHandle
            Module type handle
        FuncRefs
            Function reference container

        Raises
        ----------
        KeyError
            Module is not available.
        """

        if str(slot) in self._mod_handles:
            return (
                self._mod_handles[str(slot)]["type_handle"],
                self._mod_handles[str(slot)]["func_refs"],
            )
        else:
            raise KeyError("Module at slot {} is not available.".format(slot))

    # ------------------------------------------------------------------------
    def _module_type(self, slot: int) -> InstrumentType:
        """
        Get indexed module's type (e.g. QRM, QCM).

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        InstrumentType
            Module type

        Raises
        ----------
        """

        type_handle, _ = self._present_at_init(slot)
        return type_handle.instrument_type

    # ------------------------------------------------------------------------
    def _is_qcm_type(self, slot: int) -> bool:
        """
        Return if indexed module is of type QCM.

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        bool
            True if module is of type QCM.

        Raises
        ----------
        """

        type_handle, _ = self._present_at_init(slot)
        return type_handle.is_qcm_type

    # ------------------------------------------------------------------------
    def _is_qrm_type(self, slot: int) -> bool:
        """
        Return if indexed module is of type QRM.

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        bool:
            True if module is of type QRM.

        Raises
        ----------
        """

        type_handle, _ = self._present_at_init(slot)
        return type_handle.is_qrm_type

    # ------------------------------------------------------------------------
    def _is_rf_type(self, slot: int) -> bool:
        """
        Return if indexed module is of type QCM-RF or QRM-RF.

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        bool:
            True if module is of type QCM-RF or QRM-RF.

        Raises
        ----------
        """

        type_handle, _ = self._present_at_init(slot)
        return type_handle.is_rf_type

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_scpi_commands)
    def _get_scpi_commands(self) -> Dict:
        return gf.get_scpi_commands(self._funcs)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_idn)
    def get_idn(self) -> Dict:
        return gf.get_idn(self._funcs)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_system_state)
    def get_system_state(self) -> gf.SystemState:
        return gf.get_system_state(self._funcs)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_acq_scope_config)
    def _set_acq_scope_config(self, slot: int, config: Dict) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_acq_scope_config(funcs, config)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_scope_config)
    def _get_acq_scope_config(self, slot: int) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_acq_scope_config(funcs)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_acq_scope_config_val)
    def _set_acq_scope_config_val(self, slot: int, param: str, val: Any) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_acq_scope_config_val(funcs, param, val)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_scope_config_val)
    def _get_acq_scope_config_val(self, slot: int, param: str) -> Any:
        _, funcs = self._present_at_init(slot)
        return gf.get_acq_scope_config_val(funcs, param)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_program)
    def _set_sequencer_program(self, slot: int, sequencer: int, program: str) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequencer_program(funcs, sequencer, program)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config)
    def _set_sequencer_config(self, slot: int, sequencer: int, config: Dict) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequencer_config(funcs, sequencer, config)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config)
    def _get_sequencer_config(self, slot: int, sequencer: int) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_sequencer_config(funcs, sequencer)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config_val)
    def _set_sequencer_config_val(self, slot: int, sequencer: int, param: str, val: Any) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequencer_config_val(funcs, sequencer, param, val)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config_val)
    def _get_sequencer_config_val(self, slot: int, sequencer: int, param: str) -> Any:
        _, funcs = self._present_at_init(slot)
        return gf.get_sequencer_config_val(funcs, sequencer, param)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config_rotation_matrix)
    def _set_sequencer_config_rotation_matrix(self, slot: int, sequencer: int, phase_incr: float) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequencer_config_rotation_matrix(funcs, sequencer, phase_incr)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config_rotation_matrix)
    def _get_sequencer_config_rotation_matrix(self, slot: int, sequencer: int) -> float:
        _, funcs = self._present_at_init(slot)
        return gf.get_sequencer_config_rotation_matrix(funcs, sequencer)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_channel_map)
    def _set_sequencer_channel_map(self, slot: int, sequencer: int, output: int, enable: bool) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequencer_channel_map(funcs, sequencer, output, enable)

    # -------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_channel_map)
    def _get_sequencer_channel_map(self, slot: int, sequencer: int, output: int) -> bool:
        _, funcs = self._present_at_init(slot)
        return gf.get_sequencer_channel_map(funcs, sequencer, output)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.arm_sequencer)
    def arm_sequencer(self, slot: Optional[int] = None, sequencer: Optional[int] = None) -> None:
        if slot is not None:
            self._present_at_init(slot)
        else:
            slot = ""  # Arm sequencers across all modules

        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Arm all sequencers within a module

        return gf.arm_sequencer(
            self._funcs,
            "SLOT{}:SEQuencer{}".format(slot, sequencer)
        )

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.start_sequencer)
    def start_sequencer(self, slot: Optional[int] = None, sequencer: Optional[int] = None) -> None:
        if slot is not None:
            self._present_at_init(slot)
        else:
            slot = ""  # Start sequencers across all modules

        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Start all sequencers within a module

        return gf.start_sequencer(
            self._funcs,
            "SLOT{}:SEQuencer{}".format(slot, sequencer)
        )

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.stop_sequencer)
    def stop_sequencer(self, slot: Optional[int] = None, sequencer: Optional[int] = None) -> None:
        if slot is not None:
            self._present_at_init(slot)
        else:
            slot = ""  # Stop sequencers across all modules

        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Stop all sequencers within a module

        return gf.stop_sequencer(
            self._funcs,
            "SLOT{}:SEQuencer{}".format(slot, sequencer)
        )

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_state)
    def get_sequencer_state(self, slot: int, sequencer: int, timeout: int = 0, timeout_poll_res: float = 0.02) -> gf.SequencerState:
        _, funcs = self._present_at_init(slot)
        return gf.get_sequencer_state(funcs, sequencer, timeout, timeout_poll_res)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_waveforms)
    def _add_waveforms(self, slot: int, sequencer: int, waveforms: Dict) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.add_waveforms(funcs, sequencer, waveforms)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_waveform)
    def _delete_waveform(self, slot: int, sequencer: int, name: str = "", all: bool = False) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.delete_waveform(funcs, sequencer, name, all)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_waveforms)
    def get_waveforms(self, slot: int, sequencer: int) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_waveforms(funcs, sequencer)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_weights)
    def _add_weights(self, slot: int, sequencer: int, weights: Dict) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.add_weights(funcs, sequencer, weights)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_weight)
    def _delete_weight(self, slot: int, sequencer: int, name: str = "", all: bool = False) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.delete_weight(funcs, sequencer, name, all)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_weights)
    def get_weights(self, slot: int, sequencer: int) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_weights(funcs, sequencer)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acquisition_state)
    def get_acquisition_state(self, slot: int, sequencer: int, timeout: int = 0, timeout_poll_res: float = 0.02) -> bool:
        _, funcs = self._present_at_init(slot)
        return gf.get_acquisition_state(funcs, sequencer, timeout, timeout_poll_res)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_acquisitions)
    def _add_acquisitions(self, slot: int, sequencer: int, acquisitions: Dict) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.add_acquisitions(funcs, sequencer, acquisitions)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_acquisition)
    def _delete_acquisition(self, slot: int, sequencer: int, name: str = "", all: bool = False) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.delete_acquisition(funcs, sequencer, name, all)

    # -------------------------------------------------------------------------
    @gf.copy_docstr(gf.store_scope_acquisition)
    def store_scope_acquisition(self, slot: int, sequencer: int, name: str) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.store_scope_acquisition(funcs, sequencer, name)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_acquisition_data)
    def _get_acq_acquisition_data(self, slot: int, sequencer: int, name: str) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_acq_acquisition_data(self, funcs, sequencer, name)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acquisitions)
    def get_acquisitions(self, slot: int, sequencer: int) -> Dict:
        _, funcs = self._present_at_init(slot)
        return gf.get_acquisitions(funcs, sequencer)

    # ------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequence)
    def _set_sequence(self, slot: int, sequencer: int, sequence: Union[str, Dict[str, Any]], validation_enable: bool = True) -> None:
        _, funcs = self._present_at_init(slot)
        return gf.set_sequence(funcs, sequencer, sequence, validation_enable)

    # ------------------------------------------------------------------------
    def _get_modules_present(self, slot: int) -> bool:
        """
        Get an indication of module presence for a specific slot in the Cluster.

        Parameters
        ----------
        slot : int
            Slot index ranging from 1 to 20.

        Returns
        ----------
        bool
            Module presence.

        Raises
        ----------
        """

        return (int(super()._get_modules_present()) >> (slot - 1)) & 1 == 1

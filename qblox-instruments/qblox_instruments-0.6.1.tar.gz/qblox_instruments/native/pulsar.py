# ------------------------------------------------------------------------------
# Description    : Pulsar native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ------------------------------------------------------------------------------


# -- include -------------------------------------------------------------------

from typing import Any, Dict, Optional, Union
from qblox_instruments import InstrumentClass, InstrumentType, TypeHandle, PulsarType
from qblox_instruments import DeviceInfo, resolve
from qblox_instruments.ieee488_2 import IpTransport, PulsarDummyTransport, Ieee488_2
from qblox_instruments.scpi import PulsarQcm, PulsarQrm

import qblox_instruments.native.generic_func as gf


# -- class ---------------------------------------------------------------------

class Pulsar:
    """
    Class that provides the native API for the Pulsar. It provides methods to
    control all functions and features provided by the Pulsar, like sequencer,
    waveform and acquistion handling.

    This class is build upon the :class:`~qblox_instruments.scpi.PulsarQcm`
    and :class:`~qblox_instruments.scpi.PulsarQrm` classes through
    composition. This allows us to create a generic native Pulsar class that
    supports both Pulsar types, but only exposes the relevant interfaces,
    while also keeping the SCPI classes automatically generated for fast
    prototyping and development. On instantiation, this class probes the
    connected device to see which Pulsar SCPI interface to support and adds
    all respective attributes to this class. Afterwards, this class can be
    used as if it inherits from it's respective Pulsar SCPI interface with all
    features and functionality available.

    Note that the bulk of the functionality of this class is contained in the
    :mod:`~qblox_instruments.native.generic_func` module so that this
    functionality can be shared between instruments.
    """

    # --------------------------------------------------------------------------
    def __init__(
        self,
        identifier: str,
        port: Optional[int] = None,
        debug: Optional[int] = None,
        dummy_type: Optional[PulsarType] = None,
    ):
        """
        Creates Pulsar native interface object.

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
        dummy_type : Optional[PulsarType]
            Configure as dummy module of specified type.

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
        if dummy_type is not None:
            self._transport = PulsarDummyTransport(
                dummy_type,
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

        # Create a Pulsar QCM object to create a instrument type handle
        # object. The instrument might not be a Pulsar QCM but we are only
        # going to call mandatory SCPI commands for now which each instrument
        # should support. We are going to enable debug mode to bypass any
        # version check.
        scpi = PulsarQcm(self._transport, debug=1)
        model = DeviceInfo.from_idn(scpi._get_idn()).model
        self._type_handle = TypeHandle(model)

        # Create the correct instrument object
        instrument_types = {
            InstrumentType.QCM: PulsarQcm,
            InstrumentType.QRM: PulsarQrm,
        }
        if self.instrument_type not in instrument_types:
            raise ConnectionError(
                "Unsupported instrument type detected ({})".format(self.instrument_type)
            )
        intrument = instrument_types[self.instrument_type]
        self._scpi = intrument(self._transport, debug)

        # Add attributes of the connected Pulsar's SCPI interface to this
        # class, but only add them if it does not already exist to prevent
        # overloading native interface attributes.
        attr_names = list(Ieee488_2.__dict__.keys())
        attr_names += list(intrument.__dict__.keys())
        for attr_str in attr_names:
            attr = getattr(self._scpi, attr_str)
            if callable(attr) and not hasattr(self, attr_str):
                setattr(self, attr_str, attr)

        # Get a dictionary of SCPI and native functions that the functions in
        # the generic_func module require to operate. Create a function
        # reference container that we use to pass references to those
        # functions to functions in the generic_func module.
        rb = self._scpi._read_bin
        awg_wlist_rb = gf.create_read_bin(rb, "SEQuencer{}:AWG:WLISt?")
        acq_wlist_rb = gf.create_read_bin(rb, "SEQuencer{}:ACQ:WLISt?")
        acq_data_rb = gf.create_read_bin(rb, 'SEQuencer{}:ACQ:ALISt:ACQuisition:DATA? "{}"')
        acq_list_rb = gf.create_read_bin(rb, "SEQuencer{}:ACQ:ALISt?")

        self._funcs = gf.FuncRefs(self)
        self._funcs.register(awg_wlist_rb, "_get_awg_waveforms")
        self._funcs.register(acq_wlist_rb, "_get_acq_weights")
        self._funcs.register(acq_data_rb, "_get_acq_acquisition_data")
        self._funcs.register(acq_list_rb, "_get_acq_acquisitions")
        self._funcs.register(lambda: self.is_qrm_type, "is_qrm_type")

        for attr_name in self._funcs.funcs.keys():
            if (self._funcs.funcs[attr_name] is None and
               hasattr(self._scpi, attr_name)):
                self._funcs.register(getattr(self._scpi, attr_name))

        # Set instrument RF type specification
        self._type_handle._is_rf_type = bool(self._scpi._get_lo_hw_present())

    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    @property
    def instrument_type(self) -> InstrumentType:
        """
        Get instrument type (e.g. QRM, QCM).

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

    # --------------------------------------------------------------------------
    @property
    def is_qcm_type(self) -> bool:
        """
        Return if module is of type QCM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QCM.

        Raises
        ----------
        """

        return self._type_handle.is_qcm_type

    # --------------------------------------------------------------------------
    @property
    def is_qrm_type(self) -> bool:
        """
        Return if module is of type QRM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QRM.

        Raises
        ----------
        """

        return self._type_handle.is_qrm_type

    # --------------------------------------------------------------------------
    @property
    def is_rf_type(self) -> bool:
        """
        Return if module is of type QCM-RF or QRM-RF.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QCM-RF or QRM-RF.

        Raises
        ----------
        """

        return self._type_handle.is_rf_type

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_scpi_commands)
    def _get_scpi_commands(self) -> Dict:
        return gf.get_scpi_commands(self._funcs)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_idn)
    def get_idn(self) -> Dict:
        return gf.get_idn(self._funcs)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_system_state)
    def get_system_state(self) -> gf.SystemState:
        return gf.get_system_state(self._funcs)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_acq_scope_config)
    def _set_acq_scope_config(self, config: Dict) -> None:
        return gf.set_acq_scope_config(self._funcs, config)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_scope_config)
    def _get_acq_scope_config(self) -> Dict:
        return gf.get_acq_scope_config(self._funcs)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_acq_scope_config_val)
    def _set_acq_scope_config_val(self, param: str, val: Any) -> None:
        return gf.set_acq_scope_config_val(self._funcs, param, val)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_scope_config_val)
    def _get_acq_scope_config_val(self, param: str) -> Any:
        return gf.get_acq_scope_config_val(self._funcs, param)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_program)
    def _set_sequencer_program(self, sequencer: int, program: str) -> None:
        return gf.set_sequencer_program(self._funcs, sequencer, program)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config)
    def _set_sequencer_config(self, sequencer: int, config: Dict) -> None:
        return gf.set_sequencer_config(self._funcs, sequencer, config)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config)
    def _get_sequencer_config(self, sequencer: int) -> Dict:
        return gf.get_sequencer_config(self._funcs, sequencer)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config_val)
    def _set_sequencer_config_val(self, sequencer: int, param: str, val: Any) -> None:
        return gf.set_sequencer_config_val(self._funcs, sequencer, param, val)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config_val)
    def _get_sequencer_config_val(self, sequencer: int, param: str) -> Any:
        return gf.get_sequencer_config_val(self._funcs, sequencer, param)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_config_rotation_matrix)
    def _set_sequencer_config_rotation_matrix(self, sequencer: int, phase_incr: float) -> None:
        return gf.set_sequencer_config_rotation_matrix(self._funcs, sequencer, phase_incr)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_config_rotation_matrix)
    def _get_sequencer_config_rotation_matrix(self, sequencer: int) -> float:
        return gf.get_sequencer_config_rotation_matrix(self._funcs, sequencer)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequencer_channel_map)
    def _set_sequencer_channel_map(self, sequencer: int, output: int, enable: bool) -> None:
        return gf.set_sequencer_channel_map(self._funcs, sequencer, output, enable)

    # ---------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_channel_map)
    def _get_sequencer_channel_map(self, sequencer: int, output: int) -> bool:
        return gf.get_sequencer_channel_map(self._funcs, sequencer, output)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.arm_sequencer)
    def arm_sequencer(self, sequencer: Optional[int] = None) -> None:
        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Arm all sequencers

        return gf.arm_sequencer(self._funcs, "SEQuencer{}".format(sequencer))

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.start_sequencer)
    def start_sequencer(self, sequencer: Optional[int] = None) -> None:
        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Start all sequencers

        return gf.start_sequencer(self._funcs, "SEQuencer{}".format(sequencer))

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.stop_sequencer)
    def stop_sequencer(self, sequencer: Optional[int] = None) -> None:
        if sequencer is not None:
            gf.check_sequencer_index(sequencer)
        else:
            sequencer = ""  # Stop all sequencers

        return gf.stop_sequencer(self._funcs, "SEQuencer{}".format(sequencer))

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_sequencer_state)
    def get_sequencer_state(self, sequencer: int, timeout: int = 0, timeout_poll_res: float = 0.02) -> gf.SequencerState:
        return gf.get_sequencer_state(self._funcs, sequencer, timeout, timeout_poll_res)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_waveforms)
    def _add_waveforms(self, sequencer: int, waveforms: Dict) -> None:
        return gf.add_waveforms(self._funcs, sequencer, waveforms)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_waveform)
    def _delete_waveform(self, sequencer: int, name: str = "", all: bool = False) -> None:
        return gf.delete_waveform(self._funcs, sequencer, name, all)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_waveforms)
    def get_waveforms(self, sequencer: int) -> Dict:
        return gf.get_waveforms(self._funcs, sequencer)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_weights)
    def _add_weights(self, sequencer: int, weights: Dict) -> None:
        return gf.add_weights(self._funcs, sequencer, weights)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_weight)
    def _delete_weight(self, sequencer: int, name: str = "", all: bool = False) -> None:
        return gf.delete_weight(self._funcs, sequencer, name, all)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_weights)
    def get_weights(self, sequencer: int) -> Dict:
        return gf.get_weights(self._funcs, sequencer)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acquisition_state)
    def get_acquisition_state(self, sequencer: int, timeout: int = 0, timeout_poll_res: float = 0.02) -> bool:
        return gf.get_acquisition_state(self._funcs, sequencer, timeout, timeout_poll_res)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.add_acquisitions)
    def _add_acquisitions(self, sequencer: int, acquisitions: Dict) -> None:
        return gf.add_acquisitions(self._funcs, sequencer, acquisitions)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.delete_acquisition)
    def _delete_acquisition(self, sequencer: int, name: str = "", all: bool = False) -> None:
        return gf.delete_acquisition(self._funcs, sequencer, name, all)

    # ---------------------------------------------------------------------------
    @gf.copy_docstr(gf.store_scope_acquisition)
    def store_scope_acquisition(self, sequencer: int, name: str) -> None:
        return gf.store_scope_acquisition(self._funcs, sequencer, name)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acq_acquisition_data)
    def _get_acq_acquisition_data(self, sequencer: int, name: str) -> Dict:
        return gf.get_acq_acquisition_data(self, self._funcs, sequencer, name)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.get_acquisitions)
    def get_acquisitions(self, sequencer: int) -> Dict:
        return gf.get_acquisitions(self._funcs, sequencer)

    # --------------------------------------------------------------------------
    @gf.copy_docstr(gf.set_sequence)
    def _set_sequence(self, sequencer: int, sequence: Union[str, Dict[str, Any]], validation_enable: bool = True) -> None:
        return gf.set_sequence(self._funcs, sequencer, sequence, validation_enable)

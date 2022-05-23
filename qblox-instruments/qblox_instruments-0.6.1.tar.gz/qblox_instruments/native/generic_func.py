# ----------------------------------------------------------------------------
# Description    : Generic native interface functions
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import copy
import sys
import dis
import numpy
import struct
import re
import time
import json
import fastjsonschema

from enum import Enum
from collections import namedtuple
from functools import wraps, partial
from typing import Any, Callable, Dict, List, Optional, Union
from inspect import getmembers, isfunction
from qblox_instruments import DeviceInfo
from qblox_instruments.scpi import scpi_error_check


# -- definitions -------------------------------------------------------------

# State enum base class
class StateEnum(Enum):
    """
    State enum base class that arranges child enum string representations.
    """

    def __repr__(self) -> str:
        return "<{}.{}>".format(str(type(self)).split("'")[1], self.name)

    def __str__(self) -> str:
        return str(self.name)

    def __eq__(self, other: Any) -> bool:
        if type(self) == type(other):
            return str(self) == str(other)
        elif other in [str(val) for val in type(self)]:
            return str(self) == other
        else:
            raise KeyError("{} is not of type {}".format(other, type(self)))

    def __key__(self):
        return str(self)

    def __hash__(self):
        return hash(self.__key__())


# State tuple base class
class StateTuple:
    """
    State tuple base class that arranges child tuple string representations.
    """

    def __str__(self) -> str:
        # Status, flags and slot_flags are inherited from the child class
        # using virtual inheritance, so we retrieve these attributes through
        # getattr to not upset Pylint
        status = getattr(self, "status")
        flags = getattr(self, "flags")
        if len(flags) > 0:
            flags = ", ".join([str(flag) for flag in flags])
        else:
            flags = "NONE"
        pretty_str = "Status: {}, Flags: {}".format(status, flags)

        if hasattr(self, "slot_flags"):
            slot_flags = getattr(self, "slot_flags")
            pretty_str += ", Slot flags: {}".format(slot_flags)

        return pretty_str


# System status enum
class SystemStatus(StateEnum):
    """
    System status enum.
    """

    BOOTING = "System is booting."
    OKAY = "System is okay."
    CRITICAL = "An error indicated by the flags occured, but has been resolved."
    ERROR = "An error indicated by the flags is occuring."


# System status flags enum
class SystemStatusFlags(StateEnum):
    """
    System status flags enum.
    """

    CARRIER_PLL_UNLOCKED = "Carrier board PLL is unlocked."
    FPGA_PLL_UNLOCKED = "FPGA PLL is unlocked."
    LO_PLL_UNLOCKED = "Local oscillator PLL is unlocked."
    FPGA_TEMPERATURE_OUT_OF_RANGE = "FPGA temperature is out-of-range."
    CARRIER_TEMPERATURE_OUT_OF_RANGE = "Carrier board temperature is out-of-range."
    AFE_TEMPERATURE_OUT_OF_RANGE = "Analog-frontend board temperature is out-of-range."
    LO_TEMPERATURE_OUT_OF_RANGE = "Local oscillator board temperature is out-of-range."
    BACKPLANE_TEMPERATURE_OUT_OF_RANGE = "Backplane board temperature is out-of-range."
    MODULE_NOT_CONNECTED = "Module is not connected."
    MODULE_FIRMWARE_INCOMPATIBLE = "Module firmware is incompatible with the rest of the system."


# Namedtuple representing the slot status flags
NUM_SLOTS = 20
class SystemStatusSlotFlags(namedtuple(
    "SystemStatusSlotFlags",
    ["slot{}".format(slot) for slot in range(1, NUM_SLOTS+1)])
):
    """
    Tuple containing lists of Cluster slot status flag enums of type
    :class:`~qblox_instruments.SystemStatusFlags`. Each Cluster slot has its
    own status flag list attribute named `slot<X>`.
    """

    __name__ = "SystemStatusSlotFlags"
    __slots__ = ()
    def __new__(cls, slot_flags: Dict = {}):
        slot_flag_lists = NUM_SLOTS *[[]]
        for slot in range(0, NUM_SLOTS):
            slot_str = "slot{}".format(slot+1)
            if slot_str in slot_flags:
                slot_flag_lists[slot] = slot_flags[slot_str]
        return super().__new__(cls, *slot_flag_lists)

    def __repr__(self):
        slot_str_list = []
        for slot in range(0, NUM_SLOTS):
            if len(self[slot]) > 0:
                slot_str_list.append("slot{}={}".format(slot+1, self[slot]))
        return "{}({})".format(self.__name__, ", ".join(slot_str_list))

    def __str__(self):
        slot_str_list = []
        for slot in range(0, NUM_SLOTS):
            for flag in self[slot]:
                slot_str_list.append("SLOT{}_{}".format(slot+1, flag))
        if len(slot_str_list) > 0:
            return ", ".join(slot_str_list)
        else:
            return "NONE"


# Namedtuple representing the system status
class SystemState(namedtuple("SystemState", ["status", "flags", "slot_flags"]), StateTuple):
    """
    System status tuple returned by :func:`!get_system_state`. The tuple
    contains a system status enum of type
    :class:`~qblox_instruments.SystemStatus`, a list of associated system
    status flag enums of type
    :class:`~qblox_instruments.SystemStatusFlags` and a tuple of type
    :class:`~qblox_instruments.SystemStatusSlotFlags` containing Cluster slot
    status flags.
    """

    pass

SystemState.status.__doc__ = """
System status enum of type :class:`~qblox_instruments.SystemStatus`.
"""
SystemState.flags.__doc__ = """
List of system status flag enums of type
:class:`~qblox_instruments.SystemStatusFlags`.
"""
SystemState.slot_flags.__doc__ = """
Tuple of type :class:`~qblox_instruments.SystemStatusSlotFlags containing
Cluster slot status flags
"""


# Sequencer status enum
class SequencerStatus(StateEnum):
    """
    Sequencer status enum.
    """

    IDLE = "Sequencer waiting to be armed and started."
    ARMED = "Sequencer is armed and ready to start."
    RUNNING = "Sequencer is running."
    Q1_STOPPED = "Classical part of the sequencer has stopped; waiting for real-time part to stop."
    STOPPED = "Sequencer has completely stopped."


# Sequencer status flags enum
class SequencerStatusFlags(StateEnum):
    """
    Sequencer status flags enum.
    """

    DISARMED = "Sequencer was disarmed."
    FORCED_STOP = "Sequencer was stopped while still running."
    SEQUENCE_PROCESSOR_Q1_ILLEGAL_INSTRUCTION = "Classical sequencer part executed an unknown instruction."
    SEQUENCE_PROCESSOR_RT_EXEC_ILLEGAL_INSTRUCTION = "Real-time sequencer part executed an unknown instruction."
    SEQUENCE_PROCESSOR_RT_EXEC_COMMAND_UNDERFLOW = "Real-time sequencer part command queue underflow."
    AWG_WAVE_PLAYBACK_INDEX_INVALID_PATH_0 = "AWG path 0 tried to play an unknown waveform."
    AWG_WAVE_PLAYBACK_INDEX_INVALID_PATH_1 = "AWG path 1 tried to play an unknown waveform."
    ACQ_WEIGHT_PLAYBACK_INDEX_INVALID_PATH_0 = "Acquisition path 0 tried to play an unknown weight."
    ACQ_WEIGHT_PLAYBACK_INDEX_INVALID_PATH_1 = "Acquisition path 1 tried to play an unknown weight."
    ACQ_SCOPE_DONE_PATH_0 = "Scope acquisition for path 0 has finished."
    ACQ_SCOPE_OUT_OF_RANGE_PATH_0 = "Scope acquisition data for path 0 was out-of-range."
    ACQ_SCOPE_OVERWRITTEN_PATH_0 = "Scope acquisition data for path 0 was overwritten."
    ACQ_SCOPE_DONE_PATH_1 = "Scope acquisition for path 1 has finished."
    ACQ_SCOPE_OUT_OF_RANGE_PATH_1 = "Scope acquisition data for path 1 was out-of-range."
    ACQ_SCOPE_OVERWRITTEN_PATH_1 = "Scope acquisition data for path 1 was overwritten."
    ACQ_BINNING_DONE = "Acquisition binning completed."
    ACQ_BINNING_FIFO_ERROR = "Acqusition binning encountered internal FIFO error."
    ACQ_BINNING_COMM_ERROR = "Acqusition binning encountered internal communication error."
    ACQ_BINNING_OUT_OF_RANGE = "Acquisition binning data out-of-range."
    ACQ_INDEX_INVALID = "Acquisition tried to process an invalid acquisition."
    ACQ_BIN_INDEX_INVALID = "Acquisition tried to process an invalid bin."
    OUTPUT_OVERFLOW = "Output overflow."
    CLOCK_INSTABILITY = "Clock source instability occurred."


# Namedtuple representing the sequencer status
class SequencerState(namedtuple("SequencerState", ["status", "flags"]), StateTuple):
    """
    Sequencer status tuple returned by :func:`!get_sequencer_state`. The tuple
    contains a sequencer status
    enum of type :class:`~qblox_instruments.SequencerStatus` and a list of
    associated sequencer status flag
    enums of type :class:`~qblox_instruments.SequencerStatusFlags`.
    """

    pass

SequencerState.status.__doc__ = """
Sequencer status enum of type :class:`~qblox_instruments.SequencerStatus`.
"""
SequencerState.flags.__doc__ = """
List of sequencer status flag enums of type
:class:`~qblox_instruments.SequencerStatusFlags`.
"""


# JSON schema to validate sequence dictionaries with
QCM_SEQUENCE_JSON_SCHEMA = {
    "title": "Sequence container",
    "description": "Contains all waveforms, weights and acquisitions and a program required for a sequence.",
    "type": "object",
    "required": ["program", "waveforms"],
    "properties": {
        "program": {
            "description": "Sequencer assembly program in string format.",
            "type": "string",
        },
        "waveforms": {
            "description": "Waveform dictionary containing one or multiple AWG waveform(s).",
            "type": "object",
        },
        "weights": {
            "description": "Weight dictionary containing one or multiple acquisition weights(s).",
            "type": "object",
        },
        "acquisitions": {
            "description": "Acquisition dictionary containing information about one or multiple acquisition(s).",
            "type": "object",
        },
    },
}

# JSON schema to validate QRM sequence dictionaries with
QRM_SEQUENCE_JSON_SCHEMA = copy.deepcopy(QCM_SEQUENCE_JSON_SCHEMA)
QRM_SEQUENCE_JSON_SCHEMA["required"] = [
    "program",
    "waveforms",
    "weights",
    "acquisitions",
]

# JSON schema to validate wavefrom and weight dictionaries with
WAVE_JSON_SCHEMA = {
    "title": "Waveform/weight container",
    "description": "Waveform/weight dictionary for a single waveform.",
    "type": "object",
    "required": ["data"],
    "properties": {
        "data": {
            "description": "List of waveform samples.",
            "type": "array"
        },
        "index": {
            "description": "Optional waveform index number.",
            "type": "number"
        },
    },
}

# JSON schema to validate acquisition dictionaries with
ACQ_JSON_SCHEMA = {
    "title": "Acquisition container",
    "description": "Acquisition dictionary for a single acquisition.",
    "type": "object",
    "required": ["num_bins"],
    "properties": {
        "num_bins": {
            "description": "Number of bins in acquisition.",
            "type": "number"
        },
        "index": {
            "description": "Optional waveform index number.",
            "type": "number"
        },
    },
}


# -- class -------------------------------------------------------------------

class FuncRefs:
    """
    Function reference container intended to hold references to methods of the
    instrument's SCPI and native interfaces that are called by methods in
    :mod:`~qblox_instruments.native.generic_func`. In effect, this class enables
    passing parametrized methods to the
    :mod:`~qblox_instruments.native.generic_func` functions so that those
    functions can be reused between different instruments.
    """

    # ------------------------------------------------------------------------
    def __init__(self, instrument: Optional[Any] = None):
        """
        Create function reference container.

        Parameters
        ----------
        instrument : Any
            Instrument parent object of the function references.

        Returns
        ----------

        Raises
        ----------
        """

        # Store instrument reference
        self._instrument = instrument

        # Create list of instrument function names referenced in this module's
        # functions and manually add any missing functions that the
        # convenience method failed to pick up.
        func_names = FuncRefs._get_referenced_funcs(sys.modules[__name__])
        func_names.append("_write")
        func_names.append("_flush_line_end")
        func_names.append("_get_awg_waveforms")
        func_names.append("_get_acq_weights")
        func_names.append("_get_acq_acquisition_data")
        func_names.append("_get_acq_acquisitions")

        # Create dictionary of instrument functions and associated attributes.
        # Initialize the associated attributes to None since they are not
        # registered yet.
        self._funcs = {}
        for name in func_names:
            self._funcs[name] = None

        # Add instrument functions as temporary attributes to this class, so
        # that when called it throws a NotImplemented exception. Do this
        # through a wrapper function to ensure that the function name is
        # unique in each error string. These attributes should be overwritten
        # using the register method after this class is instantiated.
        def create_unique_func(name: str) -> Callable[..., None]:
            def raise_not_implemented_error(*args, **kwargs) -> None:
                raise NotImplementedError(
                    '"{}" has not yet been registered to this function reference container.'.format(name)
                )
            return raise_not_implemented_error

        for name in func_names:
            setattr(self, name, create_unique_func(name))

    # ------------------------------------------------------------------------
    @property
    def instrument(self) -> Any:
        """
        Return function references parent object.

        Parameters
        ----------

        Returns
        ----------
        Any
            Instrument parent object of the function references.

        Raises
        ----------
        """

        return self._instrument

    # ------------------------------------------------------------------------
    @property
    def funcs(self) -> Dict:
        """
        Return dictionary of instrument function names and their associate
        references, referenced in this module's functions so that the
        referenced functions can be registered to this object using the
        register method.

        Parameters
        ----------

        Returns
        ----------
        dict
            Dictionary of required instrument function names and associated
            references.

        Raises
        ----------
        """

        return self._funcs

    # ------------------------------------------------------------------------
    def register(self, ref: Callable[[Any], Any], attr_name: Optional[str] = None) -> None:
        """
        Register function reference as attribute to object.

        Parameters
        ----------
        ref : Callable[[Any], Any]
            Function reference to register.
        attr_name : Optional[str]
            Attribute name to register function to. If attribute name
            is not provided. The function is registered to the name of
            the reference argument.

        Returns
        ----------

        Raises
        ----------
        AttributeError
            Could not get name of reference.
        KeyError
            Attribute name is not found in function name list.
        """

        if attr_name is None:
            if hasattr(ref, "__name__"):
                attr_name = ref.__name__
            else:
                raise AttributeError(
                    "Could not get name of function reference."
                )

        if attr_name in self.funcs:
            self.funcs[attr_name] = ref
            setattr(self, attr_name, ref)
        else:
            raise KeyError(
                "Attribute name that is being registered ({}) is not in the instrument function list".format(attr_name)
            )

    # ------------------------------------------------------------------------
    @staticmethod
    def _get_referenced_funcs(module: Any, arg_name: str = "funcs") -> List:
        """
        Get all referenced instrument function names using FuncRefs for the
        functions in the given Python module. This method looks very
        specifically for the use of the input argument name specified by
        arg_name of type FuncRefs to find any referenced function names. Note
        that this is a convenience method that does not work for all use
        cases. For instance, it does not work for decorated functions.

        Parameters
        ----------
        arg_name : str
            Argurment name to search for.

        Returns
        ----------
        List
            List of required instrument function names.

        Raises
        ----------
        """

        # Get functions from module, disassemble them and search for FuncRefs
        # references using name specified by input argument. Finally split
        # out the function and attribute calls and return the found results.
        funcs = []
        for func in getmembers(module, isfunction):
            instr_list = list(dis.Bytecode(func[1]))
            for idx, instr in enumerate(instr_list):
                if instr.opname == "LOAD_FAST" and instr.argval == arg_name:
                    next_instr = instr_list[idx + 1]
                    if ((next_instr.opname == "LOAD_METHOD" or
                       next_instr.opname == "LOAD_ATTR") and not
                       hasattr(FuncRefs, next_instr.argval)):
                        funcs.append(instr_list[idx + 1].argval)

        return list(set(funcs))


# -- decorator ---------------------------------------------------------------

def copy_docstr(src_func):
    """
    Decorator that copies the docstring from the provided function to the
    decorated function.

    Parameters
    ----------
    src_func
        Function from which to copy the docstring.

    Returns
    ----------

    Raises
    ----------
    """

    def actual_copy_docstr(func):
        @wraps(func)
        def decorator_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        decorator_wrapper.__doc__ = src_func.__doc__
        return decorator_wrapper

    return actual_copy_docstr


# -- helper functions --------------------------------------------------------

def check_sequencer_index(sequencer: int) -> None:
    """
    Check if sequencer index is within range. We just check if the index is a
    positive integer here, because sending a negative number breaks the
    underlying SCPI command. The upperbound is checked by the instrument.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------

    Raises
    ----------
    ValueError
        Sequencer index is out-of-range (i.e. < 1).
    """

    if sequencer < 0:
        raise ValueError(
            "Sequencer index is out-of-range ({})".format(sequencer)
        )


# ----------------------------------------------------------------------------
def check_qrm_type(is_qrm_type: bool) -> None:
    """
    Check if module is of type QRM. If not throw a NotImplemented exception.
    This helper function can be used to catch execution of QRM functionality
    on non-QRM type modules.

    Parameters
    ----------
    is_qrm_type : bool
        Is QRM module type.

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    if not is_qrm_type:
        raise NotImplementedError(
            "This functionality not available on this module."
        )


# ----------------------------------------------------------------------------
def create_read_bin(
    read_bin_func: Callable[[str, bool], bytes],
    cmd: str
) -> Callable[[Optional[int], Optional[str]], bytes]:
    """
    Create binary read function that can provide a binary read with a
    preconfigured command. This is usefull for functions like
    `_get_awg_waveforms`, that need a specific binary read command to kick
    off a stream of binary blocks.

    Parameters
    ----------
    read_bin_func : Callable[[str, bool], bytes]
        SCPI layer binary read method.
    cmd : str
        Unformated command string.

    Returns
    ----------
    Callable[[Optional[int], Optional[str]], bytes]
        Binary read function with preconfigured command that takes the
        optional sequencer index and optional name string as arguments.

    Raises
    ----------
    """

    def read_bin(sequencer: Optional[int] = None, name: Optional[str] = None) -> bytes:
        if sequencer is None:
            new_cmd = cmd
        else:
            if name is None:
                new_cmd = cmd.format(sequencer)
            else:
                new_cmd = cmd.format(sequencer, name)
        return read_bin_func(new_cmd, False)
    return read_bin


# -- functions ---------------------------------------------------------------

# Note that the arguments in the docstrings of the following functions do not
# reflect the arguments of the functions themselves. Instead they reflect the
# arguments of the native instrument layer's methods that call these
# functions. The copy_docstr decorator is used to copy the docstring to the
# calling method, so that not only the functionality but also the docstring
# can be shared across the methods of the native instrument layers.

def get_scpi_commands(funcs: FuncRefs) -> Dict:
    """
    Get SCPI commands and convert to dictionary.

    Parameters
    ----------

    Returns
    ----------
    dict
        Dictionary containing all available SCPI commands, corresponding
        parameters, arguments and Python methods and finally a descriptive
        comment.

    Raises
    ----------
    """

    # Split function
    def split(cmd_elem: str) -> List:
        if cmd_elem != "None" and cmd_elem != "":
            return cmd_elem.split(",")
        else:
            return []

    # Format command string
    cmds = funcs._get_scpi_commands()
    cmd_elem_list = cmds.split(";")[:-1]
    cmd_list = numpy.reshape(cmd_elem_list, (int(len(cmd_elem_list) / 9), 9))
    cmd_dict = {
        cmd[0]: {
            "scpi_in_type": split(cmd[1]),
            "scpi_out_type": split(cmd[2]),
            "python_func": cmd[3],
            "python_in_type": split(cmd[4]),
            "python_in_var": split(cmd[5]),
            "python_out_type": split(cmd[6]),
            "comment": cmd[8].replace("\t", "\n"),
        } for cmd in cmd_list
    }
    return cmd_dict


# ----------------------------------------------------------------------------
def get_idn(funcs: FuncRefs) -> Dict:
    """
    Get device identity and build information and convert them to a
    dictionary.

    Parameters
    ----------

    Returns
    ----------
    dict
        Dictionary containing manufacturer, model, serial number and build
        information. The build information is subdivided into FPGA firmware,
        kernel module software, application software and driver software build
        information. Each of those consist of the version, build date,
        build Git hash and Git build dirty indication.

    Raises
    ----------
    """

    return DeviceInfo.from_idn(funcs._get_idn()).to_idn_dict()


# ----------------------------------------------------------------------------
def get_system_state(funcs: FuncRefs) -> SystemState:
    """
    Get general system state and convert it to a
    :class:`~qblox_instruments.SystemState`.

    Parameters
    ----------

    Returns
    ----------
    SystemStatus
        Tuple containing general system status and corresponding flags.

    Raises
    ----------
    """

    # Format status string
    state = funcs._get_system_state()
    state_elem_list = re.sub(" |-", "_", state).split(";")
    if state_elem_list[-1] != "":
        state_flag_list = state_elem_list[-1].split(",")[:-1]
    else:
        state_flag_list = []

    # Split system status flags from slot status flags
    system_flags = []
    slot_flags = {}
    for flag in state_flag_list:
        flag_parts = flag.split("_")
        if flag_parts[0] != "SLOT":
            system_flags.append(SystemStatusFlags[flag])
        else:
            slot = "slot" + flag_parts[1]
            flag = SystemStatusFlags['_'.join(flag_parts[2:])]
            if slot not in slot_flags:
                slot_flags[slot] = [flag]
            else:
                slot_flags[slot].append(flag)

    return SystemState(
        SystemStatus[state_elem_list[0]],
        system_flags,
        SystemStatusSlotFlags(slot_flags),
    )


# ----------------------------------------------------------------------------
def get_acq_scope_config_format() -> str:
    """
    Get format for converting the configuration dictionary to a C struct.

    Parameters
    ----------

    Returns
    ----------
    str
        String compatible with struct package.

    Raises
    ----------
    """

    acq_scope_cfg_format = "I????II"
    acq_scope_float_cfg_format = "ff"

    return acq_scope_cfg_format + acq_scope_float_cfg_format


# ----------------------------------------------------------------------------
def set_acq_scope_config(funcs: FuncRefs, config: Dict) -> None:
    """
    Set configuration of the scope acquisition. The configuration consists of
    multiple parameters in a C struct format. If an invalid sequencer index
    is given or the configation struct does not have the correct format, an
    error is set in system error.

    Parameters
    ----------
    config : dict
        Configuration dictionary.

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    # Get current configuration and merge dictionaries. Also checks if module is a QRM.
    cfg_dict = {**get_acq_scope_config(funcs), **config}

    # Set new configuration
    cfg = [
        # Scope acquisition
        cfg_dict["sel_acq"],               # Acquisition select
        cfg_dict["avg_en_acq_path_0"],     # Averaging enable path 0
        cfg_dict["avg_en_acq_path_1"],     # Averaging enable path 1
        cfg_dict["trig_mode_acq_path_0"],  # Trigger mode path 0
        cfg_dict["trig_mode_acq_path_1"],  # Trigger mode path 1
        0,                                 # Trigger level path 0 (unused)
        0,                                 # Trigger level path 1 (unused)

        # Scope acquisition floating point values to be converted
        cfg_dict["trig_lvl_acq_path_0_float"],  # Trigger level path 0 as float
        cfg_dict["trig_lvl_acq_path_1_float"],  # Trigger level path 1 as float
    ]

    funcs._set_acq_scope_config(struct.pack(get_acq_scope_config_format(), *cfg))


# ----------------------------------------------------------------------------
def get_acq_scope_config(funcs: FuncRefs) -> Dict:
    """
    Get configuration of the scope acquisition. The configuration consists of
    multiple parameters in a C struct format. If an invalid sequencer index is
    given, an error is set in system error.

    Parameters
    ----------

    Returns
    ----------
    dict
        Configuration dictionary.

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    cfg = struct.unpack(get_acq_scope_config_format(), funcs._get_acq_scope_config())
    cfg_dict = {
        # Scope acquisition
        "sel_acq":              cfg[0],
        "avg_en_acq_path_0":    cfg[1],
        "avg_en_acq_path_1":    cfg[2],
        "trig_mode_acq_path_0": cfg[3],
        "trig_mode_acq_path_1": cfg[4],
        "trig_lvl_acq_path_0":  cfg[5],
        "trig_lvl_acq_path_1":  cfg[6],

        # Scope acquisition floating point values
        "trig_lvl_acq_path_0_float": cfg[7],
        "trig_lvl_acq_path_1_float": cfg[8],
    }
    return cfg_dict


# --------------------------------------------------------------------------
def set_acq_scope_config_val(funcs: FuncRefs, param: str, val: Any) -> None:
    """
    Set value of specific scope acquisition parameter.

    Parameters
    ----------
    param : str
        Parameter name.
    val: Any
        Value to set parameter to.

    Returns
    ----------

    Raises
    ----------
    """

    set_acq_scope_config(funcs, {param: val})


# --------------------------------------------------------------------------
def get_acq_scope_config_val(funcs: FuncRefs, param: str) -> Any:
    """
    Get value of specific scope acquisition parameter.

    Parameters
    ----------
    param : str
        Parameter name.

    Returns
    ----------
    Any
        Parameter value.

    Raises
    ----------
    """

    return get_acq_scope_config(funcs)[param]


# ----------------------------------------------------------------------------
def set_sequencer_program(funcs: FuncRefs, sequencer: int, program: str) -> None:
    """
    Assemble and set Q1ASM program for the indexed sequencer. If assembling
    failes, an RuntimeError is thrown with the assembler log attached.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    program : str
        Q1ASM program.

    Returns
    ----------

    Raises
    ----------
    RuntimeError
        Assembly failed.
    """

    check_sequencer_index(sequencer)
    try:
        funcs._set_sequencer_program(sequencer, program)
    except:
        print(funcs.get_assembler_log())
        raise


# ----------------------------------------------------------------------------
def get_sequencer_config_format(is_qrm_type: bool) -> str:
    """
    Get format for converting the configuration dictionary to a C struct.

    Parameters
    ----------

    Returns
    ----------
    str
        String compatible with struct package.

    Raises
    ----------
    """

    seq_proc_cfg_format = "?I"
    awg_cfg_format = "??IIIIIIIIIII?IIIIIII??I"
    awg_float_cfg_format = "fdffffff"
    acq_cfg_format = "II?IIIq"
    acq_float_cfg_format = "ffd"

    qcm_cfg_format = seq_proc_cfg_format
    qcm_cfg_format += awg_cfg_format
    qcm_cfg_format += awg_float_cfg_format

    qrm_cfg_format = qcm_cfg_format
    qrm_cfg_format += acq_cfg_format
    qrm_cfg_format += acq_float_cfg_format

    return qrm_cfg_format if is_qrm_type else qcm_cfg_format


# ----------------------------------------------------------------------------
def set_sequencer_config(funcs: FuncRefs, sequencer: int, config: Dict) -> None:
    """
    Set configuration of the indexed sequencer. The configuration consists
    dictionary containing multiple parameters that will be converted into a
    C struct supported by the Pulsar QRM.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    config : dict
        Configuration dictionary.

    Returns
    ----------

    Raises
    ----------
    """

    # Get current configuration and merge dictionaries.
    check_sequencer_index(sequencer)
    cfg_dict = {**get_sequencer_config(funcs, sequencer), **config}

    # Set new configuration
    cfg = [
        # Sequence processor
        cfg_dict["sync_en"],  # Sequence processor synchronization enable
        0,                    # Sequence processor program counter start (unused)

        # AWG
        cfg_dict["cont_mode_en_awg_path_0"],            # Continuous mode enable for AWG path 0
        cfg_dict["cont_mode_en_awg_path_1"],            # Continuous mode enable for AWG path 1
        cfg_dict["cont_mode_waveform_idx_awg_path_0"],  # continuous mode waveform index for AWG path 0
        cfg_dict["cont_mode_waveform_idx_awg_path_1"],  # Continuous mode waveform index for AWG path 1
        cfg_dict["upsample_rate_awg_path_0"],           # Upsample rate for AWG path 0
        cfg_dict["upsample_rate_awg_path_1"],           # Upsample rate for AWG path 1
        0,                                              # Gain for AWG path 0         (unused)
        0,                                              # Gain for AWG path 1         (unused)
        0,                                              # Offset for AWG path 0       (unused)
        0,                                              # Offset for AWG path 1       (unused)
        0,                                              # Phase increment; ultra-fine (unused)
        0,                                              # Phase increment; fine       (unused)
        0,                                              # Phase increment; coarse     (unused)
        0,                                              # Phase increment; sign       (unused)
        0,                                              # Phase; ultra-fine           (unused)
        0,                                              # Phase; fine                 (unused)
        0,                                              # Phase; coarse               (unused)
        0,                                              # Mixer correction matrix a11 (unsued)
        0,                                              # Mixer correction matrix a12 (unsued)
        0,                                              # Mixer correction matrix a21 (unsued)
        0,                                              # Mixer correction matrix a22 (unsued)
        cfg_dict["mod_en_awg"],                         # Modulation enable for AWG paths 0 and 1
        cfg_dict["mrk_ovr_en"],                         # Marker override enable
        cfg_dict["mrk_ovr_val"],                        # Marker override value

        # AWG floating point values to be converted
        cfg_dict["phase_offs_degree"],                     # Phase offset in degrees
        cfg_dict["freq_hz"],                               # Frequency in Hz
        cfg_dict["gain_awg_path_0_float"],                 # Gain for AWG path 0 as float
        cfg_dict["gain_awg_path_1_float"],                 # Gain for AWG path 1 as float
        cfg_dict["offset_awg_path_0_float"],               # Offset for AWG path 0 as float
        cfg_dict["offset_awg_path_1_float"],               # Offset for AWG path 1 as float
        cfg_dict["mixer_corr_phase_offset_degree_float"],  # NCO compensation for mixer: phase offset
        cfg_dict["mixer_corr_gain_ratio_float"],           # NCO compensation for mixer: gain imbalance
    ]

    if funcs.is_qrm_type():
        cfg += [
            # Acquisition
            cfg_dict["upsample_rate_acq_path_0"],     # Upsample rate for acquisition path 0
            cfg_dict["upsample_rate_acq_path_1"],     # Upsample rate for acquisition path 1
            cfg_dict["demod_en_acq"],                 # Demodulation enable
            cfg_dict["non_weighed_integration_len"],  # Non weighed integration length
            0,                                        # Rotation matrix A11 (unused)
            0,                                        # Rotation matrix A12 (unused)
            0,                                        # Discretization threshold (unused)

            # Acquisition floating point values to be converted
            cfg_dict["rotation_matrix_a11"],  # Rotation matrix A11
            cfg_dict["rotation_matrix_a12"],  # Rotation matrix A12
            cfg_dict["discr_threshold"],      # Discretization threshold
        ]

    funcs._set_sequencer_config(
        sequencer,
        struct.pack(get_sequencer_config_format(funcs.is_qrm_type()), *cfg)
    )


# ----------------------------------------------------------------------------
def get_sequencer_config(funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get configuration of the indexed sequencer. The configuration consists
    dictionary containing multiple parameters that will be converted from a C
    struct provided by the Pulsar QRM.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Configuration dictionary.

    Raises
    ----------
    """

    check_sequencer_index(sequencer)
    cfg = struct.unpack(
        get_sequencer_config_format(funcs.is_qrm_type()),
        funcs._get_sequencer_config(sequencer),
    )

    cfg_dict = {
        # Sequence processor
        "sync_en": cfg[0],

        # AWG
        "cont_mode_en_awg_path_0":           cfg[2],
        "cont_mode_en_awg_path_1":           cfg[3],
        "cont_mode_waveform_idx_awg_path_0": cfg[4],
        "cont_mode_waveform_idx_awg_path_1": cfg[5],
        "upsample_rate_awg_path_0":          cfg[6],
        "upsample_rate_awg_path_1":          cfg[7],
        "mod_en_awg":                        cfg[23],
        "mrk_ovr_en":                        cfg[24],
        "mrk_ovr_val":                       cfg[25],

        # AWG floating point values
        "phase_offs_degree":                    cfg[26],
        "freq_hz":                              cfg[27],
        "gain_awg_path_0_float":                cfg[28],
        "gain_awg_path_1_float":                cfg[29],
        "offset_awg_path_0_float":              cfg[30],
        "offset_awg_path_1_float":              cfg[31],
        "mixer_corr_phase_offset_degree_float": cfg[32],
        "mixer_corr_gain_ratio_float":          cfg[33],
    }

    if funcs.is_qrm_type():
        cfg_dict = {**cfg_dict, **{
            # Acquisition
            "upsample_rate_acq_path_0":    cfg[34],
            "upsample_rate_acq_path_1":    cfg[35],
            "demod_en_acq":                cfg[36],
            "non_weighed_integration_len": cfg[37],

            # Acquisition floating point values
            "rotation_matrix_a11": cfg[41],
            "rotation_matrix_a12": cfg[42],
            "discr_threshold":     cfg[43]},
        }
    return cfg_dict


# --------------------------------------------------------------------------
def set_sequencer_config_val(
    funcs: FuncRefs,
    sequencer: int,
    param: str,
    val: Any
) -> None:
    """
    Set value of specific sequencer parameter.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    param : str
        Parameter name.
    val : Any
        Value to set parameter to.

    Returns
    ----------

    Raises
    ----------
    """

    set_sequencer_config(funcs, sequencer, {param: val})


# --------------------------------------------------------------------------
def get_sequencer_config_val(
    funcs: FuncRefs,
    sequencer: int,
    param: str
) -> Any:
    """
    Get value of specific sequencer parameter.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    param : str
        Parameter name.

    Returns
    ----------
    Any
        Parameter value.

    Raises
    ----------
    """

    return get_sequencer_config(funcs, sequencer)[param]


# ----------------------------------------------------------------------------
def set_sequencer_config_rotation_matrix(
    funcs: FuncRefs,
    sequencer: int,
    phase_incr: float
) -> None:
    """
    Sets the integration result phase rotation matrix in the acquisition path.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    phase_incr : float
        Phase increment in degrees.

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    cfg_dict = {
        "rotation_matrix_a11": numpy.cos(numpy.deg2rad(360 - phase_incr)),
        "rotation_matrix_a12": numpy.sin(numpy.deg2rad(360 - phase_incr)),
    }
    set_sequencer_config(funcs, sequencer, cfg_dict)


# ----------------------------------------------------------------------------
def get_sequencer_config_rotation_matrix(
    funcs: FuncRefs,
    sequencer: int
) -> float:
    """
    Gets the integration result phase rotation matrix in the acquisition path.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    float
        Phase increment in degrees.

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    cfg = get_sequencer_config(funcs, sequencer)
    vector = cfg["rotation_matrix_a11"] + cfg["rotation_matrix_a12"] * 1j
    phase_incr = numpy.angle(vector, deg=True)
    if phase_incr == 0:
        return 0
    elif phase_incr >= 0:
        return 360 - phase_incr
    else:
        return -1.0 * phase_incr


# -----------------------------------------------------------------------------
def set_sequencer_channel_map(funcs: FuncRefs, sequencer: int, output: int, enable: bool) -> None:
    """
    Set enable of the indexed sequencer's path to output.
    If an invalid sequencer index is given or the channel map is not valid, an
    error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    output : int
        Output index.
    enable : bool
        Sequencer path to output enable

    Returns
    ----------

    Raises
    ----------
    """

    check_sequencer_index(sequencer)
    channel_map_bin = funcs._get_sequencer_channel_map(sequencer)
    channel_map = list(
        struct.unpack("I" * int(len(channel_map_bin) / 4), channel_map_bin)
    )

    if output not in channel_map and enable:
        channel_map.append(output)
    elif output in channel_map and not enable:
        channel_map.remove(output)

    funcs._set_sequencer_channel_map(
        sequencer,
        struct.pack("I" * len(channel_map), *channel_map)
    )


# -----------------------------------------------------------------------------
def get_sequencer_channel_map(funcs: FuncRefs, sequencer: int, output: int) -> bool:
    """
    Get enable of the indexed sequencer's path to output.
    If an invalid sequencer index is given or the channel map is not valid, an
    error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    output : int
        Output index.

    Returns
    ----------
    bool
        Sequencer path to output enable.

    Raises
    ----------
    """

    check_sequencer_index(sequencer)
    channel_map_bin = funcs._get_sequencer_channel_map(sequencer)
    channel_map = list(
        struct.unpack("I" * int(len(channel_map_bin) / 4), channel_map_bin)
    )

    return output in channel_map


# ----------------------------------------------------------------------------
def arm_sequencer(funcs: FuncRefs, scpi_cmd_prefix: str) -> None:
    """
    Prepare the indexed sequencer to start by putting it in the armed state.
    If no sequencer index is given, all sequencers are armed. Any sequencer
    that was already running is stopped and rearmed. If an invalid sequencer
    index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : Optional[int]
        Sequencer index.

    Returns
    ----------

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # The SCPI command prefix is set by the native instrument layer so that
    # it can select to arm a specific sequencer (e.g. "SLOT1:SEQuencer0") or
    # all sequencers (e.g. "SLOT:SEQuencer")
    # The actual SCPI call is wrapped in a function to make use of the
    # scpi_error_check method.
    @scpi_error_check
    def arm_sequencer_func(instrument: Any):
        funcs._write("{}:ARM".format(scpi_cmd_prefix))
    arm_sequencer_func(funcs.instrument)


# ----------------------------------------------------------------------------
def start_sequencer(funcs: FuncRefs, scpi_cmd_prefix: str) -> None:
    """
    Start the indexed sequencer, thereby putting it in the running state.
    If an invalid sequencer index is given or the indexed sequencer was not
    yet armed, an error is set in system error. If no sequencer index is
    given, all armed sequencers are started and any sequencer not in the armed
    state is ignored. However, if no sequencer index is given and no
    sequencers are armed, and error is set in system error.

    Parameters
    ----------
    sequencer : Optional[int]
        Sequencer index.

    Returns
    ----------

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # The SCPI command prefix is set by the native instrument layer so that
    # it can select to start a specific sequencer (e.g. "SLOT1:SEQuencer0") or
    # all sequencers (e.g. "SLOT:SEQuencer")
    # The actual SCPI call is wrapped in a function to make use of the
    # scpi_error_check method.
    @scpi_error_check
    def start_sequencer_func(instrument: Any):
        funcs._write("{}:START".format(scpi_cmd_prefix))
    start_sequencer_func(funcs.instrument)


# ----------------------------------------------------------------------------
def stop_sequencer(funcs: FuncRefs, scpi_cmd_prefix: str) -> None:
    """
    Stop the indexed sequencer, thereby putting it in the stopped state. If
    an invalid sequencer index is given, an error is set in system error. If
    no sequencer index is given, all sequencers are stopped.

    Parameters
    ----------
    sequencer : Optional[int]
        Sequencer index.

    Returns
    ----------

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # The SCPI command prefix is set by the native instrument layer so that
    # it can select to stop a specific sequencer (e.g. "SLOT1:SEQuencer0") or
    # all sequencers (e.g. "SLOT:SEQuencer")
    # The actual SCPI call is wrapped in a function to make use of the
    # scpi_error_check method.
    @scpi_error_check
    def stop_sequencer_func(instrument: Any):
        funcs._write("{}:STOP".format(scpi_cmd_prefix))
    stop_sequencer_func(funcs.instrument)


# ----------------------------------------------------------------------------
def get_sequencer_state(
    funcs: FuncRefs,
    sequencer: int,
    timeout: int = 0,
    timeout_poll_res:
    float = 0.02
) -> SequencerState:
    """
    Get the sequencer state. If an invalid sequencer index is given, an error
    is set in system error. If the timeout is set to zero, the function
    returns the state immediately. If a positive non-zero timeout is set, the
    function blocks until the sequencer completes. If the sequencer hasn't
    stopped before the timeout expires, a TimeoutError is thrown.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    timeout : int
        Timeout in minutes.
    timeout_poll_res : float
        Timeout polling resolution in seconds.

    Returns
    ----------
    SequencerState
        Tuple containing sequencer status and corresponding flags.

    Raises
    ----------
    TimeoutError
        Timeout
    """

    # Format status string
    check_sequencer_index(sequencer)
    state = funcs._get_sequencer_state(sequencer)
    state_elem_list = re.sub(" |-", "_", state).split(";")
    if state_elem_list[-1] != "":
        state_flag_list = state_elem_list[-1].split(",")[:-1]
    else:
        state_flag_list = []

    state_tuple = SequencerState(
        SequencerStatus[state_elem_list[0]],
        [SequencerStatusFlags[flag] for flag in state_flag_list],
    )

    elapsed_time = 0.0
    timeout = timeout * 60.0
    while ((state_tuple.status == SequencerStatus.RUNNING or
            state_tuple.status == SequencerStatus.Q1_STOPPED) and
            elapsed_time < timeout):
        time.sleep(timeout_poll_res)

        state_tuple = get_sequencer_state(funcs, sequencer)
        elapsed_time += timeout_poll_res

        if elapsed_time >= timeout:
            raise TimeoutError(
                "Sequencer {} did not stop in timeout period of {} minutes.".format(sequencer, int(timeout / 60))
            )

    return state_tuple


# ----------------------------------------------------------------------------
def _add_awg_waveform(
    funcs: FuncRefs,
    sequencer: int,
    name: str,
    waveform: List[float],
    index: Optional[int] = None,
) -> None:
    """
    Add new waveform to AWG waveform list of indexed sequencer's AWG path. If
    an invalid sequencer index is given or if the waveform causes the waveform
    memory limit to be exceeded or if the waveform samples are out-of-range,
    an error is set in the system error. The waveform names 'all' and 'ALL'
    are reserved and adding waveforms with those names will also result in an
    error being set in system error. The optional index argument is used to
    specify an index for the waveform in the waveform list which is used by
    the sequencer Q1ASM program to refer to the waveform. If no index is
    given, the next available waveform index is selected (starting from 0).
    If an invalid waveform index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Waveform name.
    waveform : list
        List of floats in the range of 1.0 to -1.0 representing the waveform.
    index : Optional[int]
        Waveform index of the waveform in the waveform list.

    Returns
    ----------

    Raises
    ----------
    """

    funcs._add_awg_waveform(sequencer, name, len(waveform), False)
    funcs._set_awg_waveform_data(sequencer, name, waveform)
    if index is not None:
        funcs._set_awg_waveform_index(sequencer, name, index)


# ----------------------------------------------------------------------------
# Note: decorator uses instrument argument
@scpi_error_check
def _get_awg_waveforms(instrument: Any, funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all waveforms in waveform list of indexed sequencer's AWG path. If an
    invalid sequencer index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with waveforms.

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # SCPI call
    num_waveforms = struct.unpack("I", funcs._get_awg_waveforms(sequencer))[0]
    if num_waveforms == 0:
        funcs._flush_line_end()

    waveform_dict = {}
    for wave_it in range(0, num_waveforms):
        # Get name and index
        name = str(funcs._read_bin("", False), "utf-8")
        index = struct.unpack("I", funcs._read_bin("", False))[0]

        # Get data
        data = funcs._read_bin("", wave_it >= (num_waveforms - 1))
        data = struct.unpack("f" * int(len(data) / 4), data)

        # Add to dictionary
        waveform_dict[name] = {"index": index, "data": list(data)}

    return waveform_dict


# ----------------------------------------------------------------------------
def _add_acq_weight(
    funcs: FuncRefs,
    sequencer: int,
    name: str,
    weight: List[float],
    index: Optional[int] = None,
) -> None:
    """
    Add new weight to acquisition weight list of indexed sequencer's
    acquisition path. If an invalid sequencer index is given or if the weight
    causes the weight memory limit to be exceeded or if the weight samples are
    out-of-range, an error is set in the system error. The weight names 'all'
    and 'ALL' are reserved and adding weights with those names will also
    result in an error being set in system error. The optional index argument
    is used to specify an index for the weight in the weight list which is
    used by the sequencer Q1ASM program to refer to the weight. If no index
    is given, the next available weight index is selected (starting from 0).
    If an invalid weight index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Weight name.
    weight : list
        List of floats in the range of 1.0 to -1.0 representing the weight.
    index : Optional[int]
        Weight index of the weight in the weight list.

    Returns
    ----------

    Raises
    ----------
    """

    funcs._add_acq_weight(sequencer, name, len(weight), False)
    funcs._set_acq_weight_data(sequencer, name, weight)
    if index is not None:
        funcs._set_acq_weight_index(sequencer, name, index)


# ----------------------------------------------------------------------------
# Note: decorator uses instrument argument
@scpi_error_check
def _get_acq_weights(instrument: Any, funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all weights in weight list of indexed sequencer's acquisition path.
    If an invalid sequencer index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with weights.

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # SCPI call
    num_weights = struct.unpack("I", funcs._get_acq_weights(sequencer))[0]
    if num_weights == 0:
        funcs._flush_line_end()

    weight_dict = {}
    for weight_it in range(0, num_weights):
        # Get name and index
        name = str(funcs._read_bin("", False), "utf-8")
        index = struct.unpack("I", funcs._read_bin("", False))[0]

        # Get data
        data = funcs._read_bin("", weight_it >= (num_weights - 1))
        data = struct.unpack("f" * int(len(data) / 4), data)

        # Add to dictionary
        weight_dict[name] = {"index": index, "data": list(data)}

    return weight_dict


# ----------------------------------------------------------------------------
def _add_acq_acquisition(
    funcs: FuncRefs,
    sequencer: int,
    name: str,
    num_bins: int,
    index: Optional[int] = None,
) -> None:
    """
    Add new acquisition to acquisition list of indexed sequencer's acquisition
    path. If an invalid sequencer index is given or if the required
    acquisition memory cannot be allocated, an error is set in system error.
    The acquisition names 'all' and 'ALL' are reserved and adding those will
    also result in an error being set in system error. If no index is given,
    the next available weight index is selected (starting from 0). If an
    invalid weight index is given, an error is set in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Acquisition name.
    num_bins : int
        Number of bins in acquisition. Maximum is 2^24.
    index : Optional[int]
        Waveform index of the acquisition in the acquisition list.

    Returns
    ----------

    Raises
    ----------
    """

    funcs._add_acq_acquisition(sequencer, name, num_bins)
    if index is not None:
        funcs._set_acq_acquisition_index(sequencer, name, index)


# ----------------------------------------------------------------------------
def _get_acq_data_and_convert(
    funcs: FuncRefs,
    init_read_func: Callable[[Optional[int], Optional[str]], bytes],
    flush_line_end: bool
) -> Dict:
    """
    Get acquisition data and convert it to a dictionary.

    Parameters
    ----------
    init_read_func : Callable[[Optional[int], Optional[str]], bytes]
        Function that performs the initial binary read.
    flush_line_end : bool
        Indication to flush final characters after final read.

    Returns
    ----------
    dict
        Dictionary with data of single acquisition.

    Raises
    ----------
    """

    acquisition_dict = {
        "scope": {
            "path0": {"data": [], "out-of-range": False, "avg_cnt": 0},
            "path1": {"data": [], "out-of-range": False, "avg_cnt": 0},
        },
        "bins": {
            "integration": {"path0": [], "path1": []},
            "threshold": [],
            "avg_cnt": [],
        },
    }

    sample_width = 12
    max_sample_value = 2 ** (sample_width - 1) - 1
    max_sample_value_sqrd = max_sample_value ** 2

    # Retrieve scope data
    scope_data = init_read_func()
    acquisition_dict["scope"]["path0"]["data"] = list(struct.unpack("i" * int(len(scope_data) / 4), scope_data))
    acquisition_dict["scope"]["path0"]["out-of-range"] = struct.unpack("?", funcs._read_bin("", False))[0]
    acquisition_dict["scope"]["path0"]["avg_cnt"] = struct.unpack("I", funcs._read_bin("", False))[0]
    scope_data = funcs._read_bin("", False)
    acquisition_dict["scope"]["path1"]["data"] = list(struct.unpack("i" * int(len(scope_data) / 4), scope_data))
    acquisition_dict["scope"]["path1"]["out-of-range"] = struct.unpack("?", funcs._read_bin("", False))[0]
    acquisition_dict["scope"]["path1"]["avg_cnt"] = struct.unpack("I", funcs._read_bin("", False))[0]

    # Normalize scope data
    avg_cnt = acquisition_dict["scope"]["path0"]["avg_cnt"]
    acquisition_dict["scope"]["path0"]["data"] = [
        val / max_sample_value if avg_cnt == 0 else val / max_sample_value / avg_cnt
        for val in acquisition_dict["scope"]["path0"]["data"]
    ]
    avg_cnt = acquisition_dict["scope"]["path1"]["avg_cnt"]
    acquisition_dict["scope"]["path1"]["data"] = [
        val / max_sample_value if avg_cnt == 0 else val / max_sample_value / avg_cnt
        for val in acquisition_dict["scope"]["path1"]["data"]
    ]

    # Retrieve bin data
    bins = funcs._read_bin("", flush_line_end)
    bin_format = "QqqLL"
    num_bins = int(len(bins) / struct.calcsize("=" + bin_format))
    bins = struct.unpack("=" + bin_format * num_bins, bins)
    for bin_idx in range(0, num_bins):
        valid = bins[bin_idx * len(bin_format)]
        if bool(valid):
            bin_path0 = bins[bin_idx * len(bin_format) + 1]
            bin_path1 = bins[bin_idx * len(bin_format) + 2]
            thres = bins[bin_idx * len(bin_format) + 3]
            avg_cnt = bins[bin_idx * len(bin_format) + 4]

            # Normalize
            bin_path0 /= max_sample_value_sqrd
            bin_path1 /= max_sample_value_sqrd
            thres = float(thres)
            if avg_cnt != 0:
                bin_path0 /= avg_cnt
                bin_path1 /= avg_cnt
                thres /= avg_cnt
        else:
            bin_path0 = float("NaN")
            bin_path1 = float("NaN")
            thres = float("NaN")
            avg_cnt = float("NaN")

        acquisition_dict["bins"]["integration"]["path0"].append(bin_path0)
        acquisition_dict["bins"]["integration"]["path1"].append(bin_path1)
        acquisition_dict["bins"]["threshold"].append(thres)
        acquisition_dict["bins"]["avg_cnt"].append(avg_cnt)

    return acquisition_dict


# ----------------------------------------------------------------------------
# Note: decorator uses instrument argument
@scpi_error_check
def get_acq_acquisition_data(
    instrument: Any,
    funcs: FuncRefs,
    sequencer: int,
    name: str
) -> Dict:
    """
    Get acquisition data of acquisition in acquisition list of indexed
    sequencer's acquisition path. The acquisition scope and bin data is
    normalized to a range of -1.0 to 1.0 taking both the bit widths of the
    processing path and average count into considaration. For the binned
    integration results, the integration length is not handled during
    normalization and therefore these values have to be divided by their
    respective integration lenghts. If an invalid sequencer index is given or
    if a non-existing acquisition name is given, an error is set in system
    error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Acquisition name.

    Returns
    ----------
    dict
        Dictionary with data of single acquisition.

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # SCPI call
    check_sequencer_index(sequencer)
    return _get_acq_data_and_convert(
        funcs,
        partial(funcs._get_acq_acquisition_data, sequencer, name),
        True,
    )


# ----------------------------------------------------------------------------
# Note: decorator uses instrument argument
@scpi_error_check
def _get_acq_acquisitions(instrument: Any, funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all acquisitions in acquisition list of indexed sequencer's
    acquisition path. If an invalid sequencer index is given, an error is set
    in system error.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with acquisitions.

    Raises
    ----------
    RuntimeError
        An error is reported in system error and debug <= 1.
        All errors are read from system error and listed in the exception.
    """

    # SCPI call
    num_acq = struct.unpack("I", funcs._get_acq_acquisitions(sequencer))[0]
    if num_acq == 0:
        funcs._flush_line_end()

    acquisition_dict = {}
    for acq_it in range(0, num_acq):
        # Get name and index
        name = str(funcs._read_bin("", False), "utf-8")
        index = struct.unpack("I", funcs._read_bin("", False))[0]

        # Get data
        acq = _get_acq_data_and_convert(
            funcs,
            partial(funcs._read_bin, "", False),
            acq_it >= (num_acq - 1)
        )

        # Add to dictionary
        acquisition_dict[name] = {"index": index, "acquisition": acq}

    return acquisition_dict


# ----------------------------------------------------------------------------
def add_waveforms(funcs: FuncRefs, sequencer: int, waveforms: Dict) -> None:
    """
    Add all waveforms in JSON compatible dictionary to the AWG waveform list
    of indexed sequencer. The dictionary must be structured as follows:

    - name: waveform name.

        - data: waveform samples in a range of 1.0 to -1.0.
        - index: optional waveform index used by the sequencer Q1ASM program
                 to refer to the waveform.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    waveforms : dict
        JSON compatible dictionary with one or more waveforms and weigths.

    Returns
    ----------

    Raises
    ----------
    KeyError
        Missing waveform data of waveform in dictionary.
    """

    check_sequencer_index(sequencer)
    for name in waveforms:
        if "data" in waveforms[name]:
            if "index" in waveforms[name]:
                _add_awg_waveform(
                    funcs,
                    sequencer,
                    name,
                    waveforms[name]["data"],
                    waveforms[name]["index"],
                )
            else:
                _add_awg_waveform(
                    funcs,
                    sequencer,
                    name,
                    waveforms[name]["data"]
                )
        else:
            raise KeyError(
                "Missing data key for {} in AWG waveform dictionary".format(name)
            )


# ----------------------------------------------------------------------------
def delete_waveform(
    funcs: FuncRefs,
    sequencer: int,
    name: str = "",
    all: bool = False
) -> None:
    """
    Delete a waveform specified by name in the AWG waveform list of indexed
    sequencer or delete all waveforms if `all` is True.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Waveform name
    all : bool
        All waveforms

    Returns
    ----------

    Raises
    ----------
    """

    check_sequencer_index(sequencer)
    funcs._delete_awg_waveform(sequencer, "all" if all else name)


# ----------------------------------------------------------------------------
def get_waveforms(funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all waveforms and weigths in the AWG waveform list of indexed
    sequencer. The returned dictionary is structured as follows:

    - name: waveform name.

        - data: waveform samples in a range of 1.0 to -1.0.
        - index: waveform index used by the sequencer Q1ASM program to refer
                 to the waveform.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with waveforms.

    Raises
    ----------
    """

    check_sequencer_index(sequencer)
    return _get_awg_waveforms(funcs.instrument, funcs, sequencer)


# ----------------------------------------------------------------------------
def add_weights(funcs: FuncRefs, sequencer: int, weights: Dict) -> None:
    """
    Add all weights in JSON compatible dictionary to the aquisition weight
    list of indexed sequencer. The dictionary must be structured as follows:

    - name : weight name.

        - data: weight samples in a range of 1.0 to -1.0.
        - index: optional waveweightform index used by the sequencer Q1ASM
                 program to refer to the weight.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    weights : dict
        JSON compatible dictionary with one or more weigths.

    Returns
    ----------

    Raises
    ----------
    KeyError
        Missing weight data of weight in dictionary.
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    for name in weights:
        if "data" in weights[name]:
            if "index" in weights[name]:
                _add_acq_weight(
                    funcs,
                    sequencer,
                    name,
                    weights[name]["data"],
                    weights[name]["index"],
                )
            else:
                _add_acq_weight(
                    funcs,
                    sequencer,
                    name,
                    weights[name]["data"]
                )
        else:
            raise KeyError(
                "Missing data key for {} in acquisiton weight dictionary".format(name)
            )


# ----------------------------------------------------------------------------
def delete_weight(
    funcs: FuncRefs,
    sequencer: int,
    name: str = "",
    all: bool = False
) -> None:
    """
    Delete a weight specified by name in the acquisition weight list of
    indexed sequencer or delete all weights if `all` is True.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Weight name
    all : bool
        All weights

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    funcs._delete_acq_weight(sequencer, "all" if all else name)


# ----------------------------------------------------------------------------
def get_weights(funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all weigths in the acquisition weight lists of indexed sequencer.
    The returned dictionary is structured as follows:

    -name : weight name.

        - data: weight samples in a range of 1.0 to -1.0.
        - index: weight index used by the sequencer Q1ASM program to refer
                 to the weight.

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with weights.

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    return _get_acq_weights(funcs.instrument, funcs, sequencer)


# ----------------------------------------------------------------------------
def get_acquisition_state(
    funcs: FuncRefs,
    sequencer: int,
    timeout: int = 0,
    timeout_poll_res: float = 0.02,
    check_seq_state: bool = True,
) -> bool:
    """
    Return acquisition binning completion state of the indexed sequencer. If
    an invalid sequencer is given, an error is set in system error. If the
    timeout is set to zero, the function returns the state immediately. If a
    positive non-zero timeout is set, the function blocks until the acquisition
    binning completes. If the acquisition hasn't completed before the timeout
    expires, a TimeoutError is thrown. Note that when sequencer state checking
    is enabled, the sequencer state is checked using get_sequencer_state with
    the selected timeout period first and then the acquisition state is checked
    with the same timeout period. This means that the total timeout period is
    two times the set timeout period.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    timeout : int
        Timeout in minutes.
    timeout_poll_res : float
        Timeout polling resolution in seconds.
    check_seq_state : bool
        Check if sequencer is done before checking acquisition state.

    Returns
    ----------
    bool
        Indicates the acquisition binning completion state (False = uncompleted,
        True = completed).

    Raises
    ----------
    TimeoutError
        Timeout
    NotImplementedError
        Functionality not available on this module.
    """

    # Check if sequencer has stopped
    check_qrm_type(funcs.is_qrm_type())
    if check_seq_state:
        seq_state = get_sequencer_state(
            funcs,
            sequencer,
            timeout,
            timeout_poll_res
        )
        if seq_state.status != SequencerStatus.STOPPED:
            return False
    else:
        seq_state = get_sequencer_state(funcs, sequencer)

    # Get acquisition status
    acq_state = SequencerStatusFlags.ACQ_BINNING_DONE in seq_state.flags
    elapsed_time = 0.0
    timeout = timeout * 60.0
    while acq_state is False and elapsed_time < timeout:
        time.sleep(timeout_poll_res)

        seq_state = get_sequencer_state(funcs, sequencer)
        acq_state = SequencerStatusFlags.ACQ_BINNING_DONE in seq_state.flags
        elapsed_time += timeout_poll_res

        if elapsed_time >= timeout:
            raise TimeoutError(
                "Acquisitions on sequencer {} did not complete in timeout period of {} minutes.".format(sequencer, int(timeout / 60))
            )

    return acq_state


# ----------------------------------------------------------------------------
def add_acquisitions(funcs: FuncRefs, sequencer: int, acquisitions: Dict) -> None:
    """
    Add all waveforms and weights in JSON compatible dictionary to AWG
    waveform and aquisition weight lists of indexed sequencer. The dictionary
    must be structured as follows:

    - name: acquisition name.
        - num_bins: number of bins in acquisition.
        - index: optional acquisition index used by the sequencer Q1ASM
                 program to refer to the acquition.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    acquisitions : dict
        JSON compatible dictionary with one or more acquisitions.

    Returns
    ----------

    Raises
    ----------
    KeyError
        Missing dictionary key in acquisitions.
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    for name in acquisitions:
        if "num_bins" in acquisitions[name]:
            if "index" in acquisitions[name]:
                _add_acq_acquisition(
                    funcs,
                    sequencer,
                    name,
                    acquisitions[name]["num_bins"],
                    acquisitions[name]["index"],
                )
            else:
                _add_acq_acquisition(
                    funcs,
                    sequencer,
                    name,
                    acquisitions[name]["num_bins"]
                )
        else:
            raise KeyError(
                "Missing num_bins key for {} in acquisition dictionary".format(name)
            )


# ----------------------------------------------------------------------------
def delete_acquisition(
    funcs: FuncRefs,
    sequencer: int,
    name: str = "",
    all: bool = False
) -> None:
    """
    Delete an acquisition specified by name in the acquisition list of indexed
    sequencer or delete all acquisitions if `all` is True.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Weight name
    all : bool
        All weights

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    funcs._delete_acq_acquisition(sequencer, "all" if all else name)


# ----------------------------------------------------------------------------
def store_scope_acquisition(funcs: FuncRefs, sequencer: int, name: str) -> None:
    """
    After an acquisition has completed, store the scope acquisition results
    in the acquisition specified by name of the indexed sequencers. If an
    invalid sequencer index is given an error is set in system error. To get
    access to the acquisition results, the sequencer will be stopped when
    calling this function.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    name : str
        Acquisition name.

    Returns
    ----------

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    funcs._set_acq_acquisition_data(sequencer, name)


# ----------------------------------------------------------------------------
def get_acquisitions(funcs: FuncRefs, sequencer: int) -> Dict:
    """
    Get all acquisitions in acquisition lists of indexed sequencer. The
    acquisition scope and bin data is normalized to a range of -1.0 to 1.0
    taking both the bit widths of the processing path and average count into
    considaration. For the binned integration results, the integration length
    is not handled during normalization and therefore these values have to be
    divided by their respective integration lenghts. The returned dictionary
    is structured as follows:

    - name: acquisition name

        - index: acquisition index used by the sequencer Q1ASM program to
                 refer to the acquisition.
        - acquisition: acquisition dictionary

            - scope: Scope data

                - path0: input path 0

                    - data: acquisition samples in a range of 1.0 to -1.0.
                    - out-of-range: out-of-range indication for the entire
                                    acquisition (False = in-range, True =
                                    out-of-range).
                    - avg_cnt: number of averages.

                - path1: input path 1

                    - data: acquisition samples in a range of 1.0 to -1.0.
                    - out-of-range: out-of-range indication for the entire
                                    acquisition (False = in-range, True =
                                    out-of-range).
                    - avg_cnt: number of averages.

            - bins: bin data

                - integration: integration data

                    - path_0: input path 0 integration result bin list
                    - path_1: input path 1 integration result bin list

                - threshold: threshold result bin list
                - valid: list of valid indications per bin
                - avg_cnt: list of number of averages per bin

    Parameters
    ----------
    sequencer : int
        Sequencer index.

    Returns
    ----------
    dict
        Dictionary with acquisitions.

    Raises
    ----------
    NotImplementedError
        Functionality not available on this module.
    """

    check_qrm_type(funcs.is_qrm_type())
    check_sequencer_index(sequencer)
    return _get_acq_acquisitions(funcs.instrument, funcs, sequencer)


# --------------------------------------------------------------------------
_validate_qcm_sequence = fastjsonschema.compile(QCM_SEQUENCE_JSON_SCHEMA)
_validate_qrm_sequence = fastjsonschema.compile(QRM_SEQUENCE_JSON_SCHEMA)
_validat_wave = fastjsonschema.compile(WAVE_JSON_SCHEMA)
_validate_acq = fastjsonschema.compile(ACQ_JSON_SCHEMA)


def set_sequence(
    funcs: FuncRefs,
    sequencer: int,
    sequence: Union[str, Dict[str, Any]],
    validation_enable: bool = True,
) -> None:
    """
    Set sequencer program, AWG waveforms, acquisition weights and acquisitions
    from a JSON file or from a dictionary directly. The JSON file or
    dictionary need to apply the schema specified by
    `QCM_SEQUENCE_JSON_SCHEMA`, `QRM_SEQUENCE_JSON_SCHEMA`, `WAVE_JSON_SCHEMA`
    and `ACQ_JSON_SCHEMA`.

    Parameters
    ----------
    sequencer : int
        Sequencer index.
    sequence : Union[str, Dict[str, Any]]
        Path to sequence file or dictionary.
    validation_enable : bool
        Enable JSON schema validation on sequence.

    Returns
    ----------

    Raises
    ----------
    JsonSchemaValueException
        Invalid JSON object.
    """

    # Set dictionary
    if isinstance(sequence, dict):
        sequence_dict = sequence
    else:
        with open(sequence, "r") as file:
            sequence_dict = json.load(file)

    # Validate dictionary
    if validation_enable:
        if funcs.is_qrm_type():
            _validate_qrm_sequence(sequence_dict)
        else:
            _validate_qcm_sequence(sequence_dict)
        for name in sequence_dict["waveforms"]:
            _validat_wave(sequence_dict["waveforms"][name])
        if funcs.is_qrm_type():
            for name in sequence_dict["weights"]:
                _validat_wave(sequence_dict["weights"][name])
            for name in sequence_dict["acquisitions"]:
                _validate_acq(sequence_dict["acquisitions"][name])

    # Set sequence
    set_sequencer_program(funcs, sequencer, sequence_dict["program"])
    delete_waveform(funcs, sequencer, all=True)
    add_waveforms(funcs, sequencer, sequence_dict["waveforms"])
    if funcs.is_qrm_type():
        delete_weight(funcs, sequencer, all=True)
        add_weights(funcs, sequencer, sequence_dict["weights"])
        delete_acquisition(funcs, sequencer, all=True)
        add_acquisitions(funcs, sequencer, sequence_dict["acquisitions"])

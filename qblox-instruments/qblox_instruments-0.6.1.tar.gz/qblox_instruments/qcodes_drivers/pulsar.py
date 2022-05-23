# --------------------------------------------------------------------------
# Description    : Pulsar QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# --------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from typing import Any, Callable, List, Optional, Union
from qcodes import Instrument, InstrumentChannel, Parameter
from qblox_instruments import PulsarType
from qblox_instruments.native import Pulsar as PulsarNative
from qblox_instruments.qcodes_drivers.qcm_qrm import add_qcodes_params, invalidate_qcodes_parameter_cache, get_item


# -- class -------------------------------------------------------------------

class Pulsar(PulsarNative, Instrument):
    """
    This class connects `QCoDeS <https://qcodes.github.io/Qcodes/>`_ to the
    Pulsar native interface.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        identifier: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[int] = None,
        dummy_type: Optional[PulsarType] = None,
    ):
        """
        Creates Pulsar QCoDeS class and adds all relevant instrument
        parameters. These instrument parameters call the associated methods
        provided by the native interface.

        Parameters
        ----------
        name : str
            Instrument name.
        identifier : Optional[str]
            Instrument identifier. See :func:`~qblox_instruments.resolve()`.
            If None, the instrument is identified by name.
        port : Optional[int]
            Override for the TCP port through which we should connect.
        debug : Optional[int]
            Debug level (0 | None = normal, 1 = no version check, >1 = no
            version or error checking).
        dummy_type : Optional[PulsarType]
            Configure as dummy module of specified type.

        Returns
        ----------

        Raises
        ----------
        """

        # Initialize parent classes.
        if identifier is None:
            identifier = name
        super().__init__(identifier, port, debug, dummy_type)
        Instrument.__init__(self, name)

        # Add QCoDeS parameters
        add_qcodes_params(self, num_seq=6)

    # ------------------------------------------------------------------------
    @property
    def sequencers(self) -> List:
        """
        Get list of sequencers submodules.

        Parameters
        ----------

        Returns
        ----------
        list
            List of sequencer submodules.

        Raises
        ----------
        """

        return list(self.submodules.values())

    # ------------------------------------------------------------------------
    def reset(self) -> None:
        """
        Resets device, invalidates QCoDeS parameter cache and clears all
        status and event registers (see
        `SCPI <https://www.ivifoundation.org/docs/scpi-99.pdf>`_).

        Parameters
        ----------

        Returns
        ----------

        Raises
        ----------
        """

        invalidate_qcodes_parameter_cache(self)
        self._reset()

    # ------------------------------------------------------------------------
    def __getitem__(
        self,
        key: str
    ) -> Union[InstrumentChannel, Parameter, Callable[..., Any]]:
        """
        Get sequencer or parameter using string based lookup.

        Parameters
        ----------
        key : str
            Sequencer, parameter or function to retrieve.

        Returns
        ----------
        Union[InstrumentChannel, Parameter, Callable[..., Any]]
            Sequencer, parameter or function.

        Raises
        ----------
        KeyError
            Sequencer, parameter or function does not exist.
        """

        return get_item(self, key)

    # ------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Returns simplified representation of class giving just the class,
        name and connection.

        Parameters
        ----------

        Returns
        ----------
        str
            String representation of class.

        Raises
        ----------
        """

        loc_str = ""
        if hasattr(self._transport, "_socket"):
            address, port = self._transport._socket.getpeername()
            loc_str = f" at {address}:{port}"
        return f"<{type(self).__name__}: {self.name}" + loc_str + ">"

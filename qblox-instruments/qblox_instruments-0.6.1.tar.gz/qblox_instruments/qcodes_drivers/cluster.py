# --------------------------------------------------------------------------
# Description    : Cluster QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# --------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from typing import Any, Callable, Dict, List, Optional, Union
from qcodes import validators as vals
from qcodes import Instrument, InstrumentChannel, Parameter
from qblox_instruments.native import Cluster as ClusterNative
from qblox_instruments.qcodes_drivers.qcm_qrm import QcmQrm, get_item


# -- class -------------------------------------------------------------------

class Cluster(ClusterNative, Instrument):
    """
    This class connects `QCoDeS <https://qcodes.github.io/Qcodes/>`_ to the
    Cluster native interface.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        identifier: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[int] = None,
        dummy_cfg: Optional[Dict] = None,
    ):
        """
        Creates Cluster QCoDeS class and adds all relevant instrument
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
        dummy_cfg : Optional[Dict]
            Configure as dummy using this configuration. For each slot that
            needs to be occupied by a module add the slot index as key and
            specify the type of module in the slot using the type
            :class:`~qblox_instruments.ClusterType`.

        Returns
        ----------

        Raises
        ----------
        """

        # Initialize parent classes.
        if identifier is None:
            identifier = name
        super().__init__(identifier, port, debug, dummy_cfg)
        Instrument.__init__(self, name)

        # Set number of slots
        self._num_slots = 20

        # Add QCoDeS parameters
        self.add_parameter(
            "reference_source",
            label="Reference source.",
            docstring="Sets/gets reference source ('internal' = internal "
                      "10 MHz, 'external' = external 10 MHz).",
            unit="",
            vals=vals.Bool(),
            val_mapping={"internal": True, "external": False},
            set_parser=bool,
            get_parser=bool,
            set_cmd=self._set_reference_source,
            get_cmd=self._get_reference_source,
        )

        # Add QCM/QRM modules
        for slot_idx in range(1, self._num_slots + 1):
            module = QcmQrm(self, "module{}".format(slot_idx), slot_idx)
            self.add_submodule("module{}".format(slot_idx), module)

    # ------------------------------------------------------------------------
    @property
    def modules(self) -> List:
        """
        Get list of modules.

        Parameters
        ----------

        Returns
        ----------
        list
            List of modules.

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

        # Invalidate instrument parameters
        for param in self.parameters.values():
            param.cache.invalidate()

        # Invalidate module parameters
        for module in self.submodules.values():
            module._invalidate_qcodes_parameter_cache()

        # Reset
        self._reset()

    # ------------------------------------------------------------------------
    def __getitem__(
        self,
        key: str
    ) -> Union[InstrumentChannel, Parameter, Callable[..., Any]]:
        """
        Get module or parameter using string based lookup.

        Parameters
        ----------
        key : str
            Module, parameter or function to retrieve.

        Returns
        ----------
        Union[InstrumentChannel, Parameter, Callable[..., Any]]
            Module, parameter or function.

        Raises
        ----------
        KeyError
            Module, parameter or function does not exist.
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

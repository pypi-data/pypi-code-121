# ----------------------------------------------------------------------------
# Description    : SPI Rack QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

from time import time
from typing import Union, Optional

from qcodes.instrument.base import Instrument

from qblox_instruments.native import SpiRack as SpiRackNative
from qblox_instruments.qcodes_drivers.spi_rack_modules import SpiModuleBase, DummySpiModule
from qblox_instruments.qcodes_drivers.spi_rack_modules import S4gModule, D5aModule


class SpiRack(SpiRackNative, Instrument):
    """
    SPI rack driver class based on
    `QCoDeS <https://qcodes.github.io/Qcodes/>`_.

    Example usage:

    .. highlight:: python
    .. code-block:: python

        from qblox_instruments import SpiRack
        from qblox_instruments.qcodes_drivers.spi_rack_modules import S4gModule

        spi = SpiRack("my_spi_rack", "COM4")   # connects to an SPI rack on COM port 4
        spi.add_spi_module(3, "D5a", "alice")  # adds an D5a module with address 3 named "alice"
        spi.add_spi_module(2, "S4g", "bob")    # adds an S4g module with address 2 named "bob"
        spi.add_spi_module(6, S4gModule)       # adds an S4g module with address 6 with the default name module6

        spi.bob.dac0.current(10e-3)            # sets the current of output 1 of the S4g module named "bob" to 10 mA
        spi.alice.dac6.voltage(-2)             # sets the voltage of output 7 of the D5a module named "alice" to -2 V
    """

    def __init__(
        self,
        name: str,
        address: str,
        baud_rate: int = 9600,
        timeout: float = 1,
        is_dummy: bool = False,
    ):
        """
        Instantiates the driver object.

        Parameters
        ----------
        name : str
            Instrument name.
        address : str
            COM port used by SPI rack controller unit (e.g. "COM4")
        baud_rate : int
            Baud rate
        timeout : float
            Data receive timeout in seconds
        is_dummy : bool
            If true, the SPI rack driver is operating in "dummy" mode for
            testing purposes.

        Returns
        ----------
        """
        t0 = time()
        super().__init__(address, baud_rate, timeout, is_dummy)
        Instrument.__init__(self, name)

        # If drivers are created for different modules they should be added
        # here
        self._MODULES_MAP = {
            "S4g": S4gModule,
            "D5a": D5aModule,
            "dummy": DummySpiModule,
        }

        self._add_qcodes_params()

        self.connect_message(begin_time=t0)

    def _add_qcodes_params(self) -> None:
        """
        Function to add the QCoDeS parameters to the instrument.
        """
        self.add_parameter(
            "temperature",
            unit="C",
            set_cmd=False,
            get_cmd=self.spi_rack.get_temperature,
            docstring="Returns the temperature in the C1b module. Reads the "
            "temperature from the internal C1b temperature sensor. Accuracy "
            "is +- 0.5 degrees in 0-70 degree range.",
        )
        self.add_parameter(
            "battery_voltages",
            unit="V",
            set_cmd=False,
            get_cmd=self.spi_rack.get_battery,
            docstring="Calculates the battery voltages from the ADC channel "
            "values. Returns: [VbatPlus, VbatMin]",
        )

    def add_spi_module(
        self,
        address: int,
        module_type: Union[SpiModuleBase, str],
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Add a module to the driver.

        Parameters
        ----------
        address : int
            Address that the module is set to (set internally on the module
            itself with a jumper).
        module_type : Union[str, :class:`~qblox_instruments.qcodes_drivers.spi_rack_modules.spi_module_base.SpiModuleBase`]
             Either a str that is defined in _MODULES_MAP, or a reference to
             a class derived from
             :class:`~qblox_instruments.qcodes_drivers.spi_rack_modules.spi_module_base.SpiModuleBase`.
        name: Optional[str]
            Optional name of the module. If no name is given or is None, a
            default name of "module{address}" is used.

        Returns
        ----------

        Raises
        ----------
        ValueError
            module_type is not a string or a subclass of
            :class:`~qblox_instruments.qcodes_drivers.spi_rack_modules.spi_module_base.SpiModuleBase`
        """

        name, module_obj = SpiRackNative.add_spi_module(
            self,
            address,
            module_type,
            name,
            **kwargs
        )
        self.add_submodule(name, module_obj)

    def close(self) -> None:
        """
        Closes connection to hardware and closes the Instrument.
        """
        SpiRackNative.close(self)
        Instrument.close(self)

    def connect_message(
        self,
        idn_param: str = "IDN",
        begin_time: Optional[float] = None
    ) -> None:
        """
        Print a standard message on initial connection to an instrument.
        Overridden from superclass to accommodate IEEE488.2 for IDN.

        Parameters
        ----------
        idn_param: str
            Name of parameter that returns ID dict. Default ``IDN``.
        begin_time: Optional[float]
            ``time.time()`` when init started. Default is ``self._t0``, set
            at start of ``Instrument.__init__``.
        """
        # start with an empty dict, just in case an instrument doesn't
        # heed our request to return all 4 fields.
        idn = {
            "manufacturer": None,
            "model": None,
            "serial": None,
            "firmware": None
        }
        idn.update(self.get(idn_param))
        t = time() - (begin_time or self._t0)

        con_msg = (
            "Connected to: {manufacturer} {model} " +
            "(serial:{serial}, firmware:{firmware}) " +
            "in {t:.2f}s"
        ).format(t=t, **idn)
        print(con_msg)
        self.log.info(f"Connected to instrument: {idn}")

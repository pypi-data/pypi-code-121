# ----------------------------------------------------------------------------
# Description    : SPI Rack native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

from typing import Dict, List, Optional, Tuple, Union

from spirack.spi_rack import SPI_rack as SpiApi
from qblox_instruments import get_build_info
from qblox_instruments.native.spi_rack_modules import SpiModuleBase, DummySpiModule
from qblox_instruments.native.spi_rack_modules import S4gModule, D5aModule


class QbloxSpiApi(SpiApi):
    def write_data(self, module, chip, SPI_mode, SPI_speed, data):
        self.unlock()
        return super().write_data(module, chip, SPI_mode, SPI_speed, data)

    def read_data(self, module, chip, SPI_mode, SPI_speed, data):
        self.unlock()
        return super().read_data(module, chip, SPI_mode, SPI_speed, data)

    def write_bulk_data(self, module, chip, SPI_mode, SPI_speed, data):
        self.unlock()
        return super().write_bulk_data(module, chip, SPI_mode, SPI_speed, data)

    def read_bulk_data(self, module, chip, SPI_mode, SPI_speed, data):
        self.unlock()
        return super().read_bulk_data(module, chip, SPI_mode, SPI_speed, data)


class DummySpiApi:
    """
    A dummy API that can be used to test the SPI rack driver.
    """

    TEMPERATURE = 25.0
    BATTERY_LVLS = [6.0, -6.0]
    FIRMWARE_VERSION = "v1.0"

    def __init__(self, address: int, baud_rate: int, timeout: float = 1.0):
        """
        Instantiates the dummy API object.

        Parameters
        ----------
        address : int
            Mock value for the address on which the SPI Rack is connected.
            This value is assigned to a member variable, but is not
            actually used.
        address : int
            Mock value for the baud_rate for the serial connection. This
            value is assigned to a member variable, but is not actually
            used.
        timeout : float
            Mock value for the timeout for the serial connection. This value
            is assigned to a member variable, but is not actually used.
        """
        self.address = address
        self.baud_rate = baud_rate
        self.timeout = timeout

        self.locked = True

    def get_temperature(self) -> float:
        """
        Return a mock temperature.

        Returns
        ----------
        float
            returns `DummySpiApi.TEMPERATURE`
        """
        return self.TEMPERATURE

    def get_battery(self) -> List[float]:
        """
        Return a mock battery level list. In the actual API these are two
        values read from the battery ADCs. For the mock API simply constant
        values are returned. The expected values to be returned can also be
        gotten through `DummySpiApi.BATTERY_LVLS`.

        Returns
        ----------
        List[float]
            returns `DummySpiApi.BATTERY_LVLS`
        """
        return self.BATTERY_LVLS

    def get_firmware_version(self) -> str:
        """
        Returns a firmware version string. In the actual API this is returned
        by the microcontroller.

        Returns
        ----------
        str
            returns `DummySpiApi.FIRMWARE_VERSION`
        """
        return self.FIRMWARE_VERSION

    def close(self) -> None:
        """
        Not relevant for dummy api but added to remove errors
        """
        pass

    def unlock(self) -> None:
        """
        Unlocks the communication to the microcontroller. Since for the dummy
        implementation there is no communication to the microcontroller, this
        simply sets a self.locked to False.
        """
        self.locked = False


class SpiRack:
    """
    SPI rack native interface class. This class relies on the
    `spirack API <https://github.com/mtiggelman/SPI-rack/>`_.
    """

    # If drivers are created for different modules they should be added here
    _MODULES_MAP = {
        "S4g": S4gModule,
        "D5a": D5aModule,
        "dummy": DummySpiModule,
    }

    def __init__(
        self,
        address: str,
        baud_rate: int = 9600,
        timeout: float = 1,
        is_dummy: bool = False,
    ):
        """
        Instantiates the driver object.

        Parameters
        ----------
        address : str
            COM port used by SPI rack controller unit (e.g. "COM4")
        baud_rate : int
            Baud rate
        timeout :  float
            Data receive timeout in seconds
        is_dummy : bool
            If true, the SPI rack driver is operating in "dummy" mode for
            testing purposes.

        Returns
        ----------
        """

        api = DummySpiApi if is_dummy else QbloxSpiApi
        self.spi_rack = api(address, baud_rate, timeout=timeout)

        self.spi_rack.unlock()

        self._modules = {}

    def add_spi_module(
        self,
        address: int,
        module_type: Union[SpiModuleBase, str],
        name: Optional[str] = None,
        **kwargs,
    ) -> Tuple[str, SpiModuleBase]:
        """
        Add a module to the driver and return module object.

        Parameters
        ----------
        address : int
            Address that the module is set to (set internally on the module
            itself with a jumper).
        module_type : Union[str, :class:`~qblox_instruments.native.spi_rack_modules.SpiModuleBase`]
             Either a str that is defined in _MODULES_MAP, or a reference
             to a class derived from
             :class:`~qblox_instruments.native.spi_rack_modules.SpiModuleBase`.
        name: Optional[str]
            Optional name of the module. If no name is given or is None, a
            default name of "module{address}" is used.

        Returns
        ----------
        str
            Name
        SpiModuleBase
            SPI module object

        Raises
        ----------
        ValueError
            module_type is not a string or a subclass of
            :class:`~qblox_instruments.native.spi_rack_modules.SpiModuleBase`
        """
        if name is None:
            name = "module{}".format(address)

        if isinstance(module_type, str):
            module = self._MODULES_MAP[module_type]
            module_obj = module(self, name, address, **kwargs)
        elif issubclass(module_type, SpiModuleBase):
            module_obj = module_type(self, name, address, **kwargs)
        else:
            raise ValueError(f"{module_type} is not a valid SPI module.")

        self._modules[address] = module_obj
        return name, module_obj

    def get_idn(self) -> Dict:
        """
        Generates the IDN dict.

        Parameters
        ----------

        Returns
        ----------
        dict
            The QCoDeS style IDN dictionary. Currently only the firmware
            version is actually read from hardware.

        Raises
        ----------
        """
        return {
            "manufacturer": "Qblox",
            "model": "SPI Rack",
            "firmware": {
                "device": self.spi_rack.get_firmware_version(),
                "driver": get_build_info().to_idn_dict(),
            },
        }

    def close(self) -> None:
        """
        Closes connection to hardware and closes the Instrument.
        """
        self.spi_rack.close()

    def set_dacs_zero(self) -> None:
        """
        Calls the :meth:`set_dacs_zero` function on all the modules, which in
        turn should cause all output values to be set to 0.
        """
        for mod in self._modules.values():
            mod.set_dacs_zero()

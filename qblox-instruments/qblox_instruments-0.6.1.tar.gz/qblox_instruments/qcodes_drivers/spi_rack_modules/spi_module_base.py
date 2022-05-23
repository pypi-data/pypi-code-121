# ----------------------------------------------------------------------------
# Description    : SPI Module Base Class
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

from qcodes.instrument.channel import InstrumentChannel
from qcodes.instrument.parameter import ManualParameter
from qblox_instruments.native.spi_rack_modules import SpiModuleBase as SpiModuleBaseNative


class SpiModuleBase(SpiModuleBaseNative, InstrumentChannel):
    """
    Defines an abstract base class for SPI modules. All module drivers
    should inherit from this class.

    This class defines no actual functionality but rather serves to provide
    a common interface shared among all modules.

    Parameters
    ----------
    parent
        Reference to the :class:`~qblox_instruments.SpiRack` parent object.
        This is handled by the
        :func:`~qblox_instruments.SpiRack.add_spi_module` function.
    name : str
        Name given to the InstrumentChannel.
    address : int
        Module number set on the hardware (set internally on the module
        itself with a jumper).

    Returns
    ----------

    Raises
    ----------
    """

    def __init__(self, parent, name: str, address: int, **kwargs):
        super().__init__(parent, name, address)
        InstrumentChannel.__init__(self, parent, name)


class DummySpiModule(SpiModuleBase):
    """
    A dummy implementation of module driver, used for mock implementations.
    """

    def __init__(self, parent, name: str, address: int):
        super().__init__(parent, name, address)

        self.add_parameter(
            "output",
            unit="A",
            parameter_class=ManualParameter,
            docstring="This is a simple manual parameter that can be used "
            "during testing. The user is able to get and set values to/from "
            "it but no actual functionality is associated with it.",
        )

    def set_dacs_zero(self) -> None:
        self.output(0)

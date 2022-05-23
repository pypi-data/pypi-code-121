# ----------------------------------------------------------------------------
# Description    : SPI Module Base Class
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod


class SpiModuleBase(metaclass=ABCMeta):
    """
    Abstract SPI module base class.
    """

    def __init__(self, parent, name: str, address: int, **kwargs):
        """
        Defines an abstract base class for SPI modules. All module drivers
        should inherit from this class.

        This class defines no actual functionality but rather serves to
        provide a common interface shared among all modules.

        Parameters
        ----------
        parent
            Reference to the :class:`~qblox_instruments.native.SpiRack` parent
            object. This is handled by the
            :func:`~qblox_instruments.native.SpiRack.add_spi_module` function.
        name : str
            Name given to the module.
        address : int
            Module number set on the hardware (set internally on the module
            itself with a jumper).

        Returns
        ----------

        Raises
        ----------
        """

        self._mod_parent = parent
        self._mod_name = name
        self._mod_address = address

    @abstractmethod
    def set_dacs_zero(self) -> None:
        """ "
        Base method for set_dacs_zero. Should be overridden by subclass.
        """

        raise NotImplementedError(
            f"{type(self)} has no implementation of set_dacs_zero()"
        )


class DummySpiModule(SpiModuleBase):
    """
    A dummy implementation of module driver, used for mock implementations.
    """

    pass

from typing import Optional

from cosapp.drivers.driver import Driver


class OptionalDriver(Driver):
    """Abstract class to be inherited by driver turn off during heavy computation.

    For instance, `Driver` plotting some information are best turned off during
    optimization or Monte-Carlo.
    """

    __inhibited = False

    @classmethod
    def set_inhibited(cls, inhibited: bool) -> None:
        """Set the inhibition status for all `OptionalDriver` classes.

        Parameters
        ----------
        inhibited : bool
            The new inhibition status
        """
        cls.__inhibited = inhibited

    def __init__(self, 
        name: str, 
        owner: Optional["cosapp.systems.System"] = None, 
        force: Optional[bool] = None, 
        **kwargs
    ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str, optional
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belong; defaults to `None`.
        force: bool, optional
            If True, `run_once` method is not inhibited whatever the class variable status is.
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)
        self._active = force

    def is_active(self) -> bool:
        """Is this Module execution activated?

        Returns
        -------
        bool
            Activation status
        """
        return bool(not self.__inhibited or self._active)

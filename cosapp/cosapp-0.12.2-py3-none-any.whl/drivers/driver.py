"""
Classes driving simulation on CoSApp :py:class:`~cosapp.systems.system.System`.
"""
from __future__ import annotations
import logging
import time
from typing import Optional, TypeVar

from cosapp.patterns.visitor import Visitor
from cosapp.core.module import Module
from cosapp.recorders.recorder import BaseRecorder
from cosapp.utils.options_dictionary import OptionsDictionary
from cosapp.utils.naming import NameChecker, CommonPorts
from cosapp.utils.helpers import check_arg

logger = logging.getLogger(__name__)

AnyDriver = TypeVar("AnyDriver", bound="Driver")
Recorder = TypeVar("Recorder", bound=BaseRecorder)


class Driver(Module):
    """Abstract base class for all systems drivers.

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which this driver belongs; default None
    **kwargs : Any
        Keyword arguments used to set driver options

    Attributes
    ----------
    name : str
        Name of the driver
    parent : Driver, optional
        Top driver containing this driver; default None.
    owner : System
        :py:class:`~cosapp.systems.system.System` to which this driver belong.
    children : OrderedDict[str, Driver]
        Drivers belonging to this one.

    options : OptionsDictionary
      |  Options for the current driver:
      |  **verbose** : int, {0, 1}
      |      Verbosity level of the driver; default 0 (i.e. minimal information)

    solution :  List[Tuple[str, float]]
        List of (name, value) for the iteratives when a solution is reached
    """

    __slots__ = ('_owner', '_recorder', 'options', 'start_time', 'status', 'error_code')

    _name_check = NameChecker(
        pattern = r"^[A-Za-z][\w\s@-]*[\w]?$",
        message = "Driver name must start with a letter, and contain only alphanumerics + {'_', '@', ' ', '-'}",
        excluded = CommonPorts.names(),
    )

    def __init__(
        self,
        name: str,
        owner: Optional["cosapp.systems.System"] = None,
        **kwargs
    ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`.
        **kwargs: Dict[str, Any]
            Optional keywords arguments.
        """
        from cosapp.systems import System

        super().__init__(name)
        self._owner: Optional[System] = None
        self._recorder: Optional[BaseRecorder] = None
        self.owner = owner

        self.options = OptionsDictionary()  # type: OptionsDictionary
            # "Driver options dictionary"
        self.start_time = 0.0  # type: float
            # unit="s",
            # desc="Absolute time at which the Driver execution started.",
        self.status = ""  # type: str
            #desc="Status of the driver."
            # TODO Fred what are the status? Enum, any str?
        self.error_code = "0"  # type: str
            # desc="Error code during the execution."
            # TODO Fred what is the code? ESI?

        # TODO is tol_target really used in all cases? Is it not redundant with options parameters?
        # self.target_tol = None # desc='Targeted maximal relative tolerance for numerical solution.')
        # TODO is current_tol updated in all cases to a relevant value?
        # self.current_tol = np.nan # desc='Maximal current relative tolerance of the numerical solution.')

        self.options.declare(
            "verbose",
            default=0,
            dtype=int,
            lower=0,
            upper=1,
            desc="Verbosity level of the driver",
        )
        for key in self.options:
            try:
                self.options[key] = kwargs.pop(key)
            except KeyError:
                continue

    def accept(self, visitor: Visitor) -> None:
        """Specifies course of action when visited by `visitor`"""
        visitor.visit_driver(self)

    def __repr__(self) -> str:
        context = "alone" if self.owner is None else f"on System {self.owner.name!r}"
        return f"{self.name} ({context}) - {self.__class__.__name__}"

    @property
    def owner(self):
        """System: System owning the driver and its children."""
        return self._owner

    @owner.setter
    def owner(self, system: Optional["cosapp.systems.System"]) -> None:
        self._set_owner(system)

    def _set_owner(self, system: Optional["cosapp.systems.System"]) -> bool:
        """Owner setter as a protected method, to be used by derived classes.
        This prevents from calling base class `owner.setter`, which can be tricky.

        Returns
        -------
        changed [bool]:
            `True` if owner has changed, `False` otherwise.
        """
        from cosapp.systems import System
        if system is not None:
            check_arg(system, 'owner', System)
        
        changed = system is not self._owner
        self._owner: Optional[System] = system
        if self._recorder is not None:
            self._recorder.watched_object = system
        for child in self.children.values():
            child.owner = system

        return changed

    def check_owner_attr(self, item: str) -> None:
        if item not in self.owner:
            raise AttributeError(f"{item!r} not found in System {self.owner.name!r}")

    @property
    def recorder(self) -> Optional[BaseRecorder]:
        """BaseRecorder or None : Recorder attached to this `Driver`."""
        return self._recorder

    def is_standalone(self) -> bool:
        """Is this Driver able to solve a system?

        Returns
        -------
        bool
            Ability to solve a system or not.
        """
        for driver in self.children.values():
            if driver.is_standalone():
                return True

        return False

    def _set_children_active_status(self, active_status : bool) -> None:
        self._active = active_status
        for child in self.children.values():
            child._set_children_active_status(active_status)

    def setup_run(self) -> None:
        """Set execution order and start the recorder."""
        if self.owner is None:
            raise AttributeError(f"Driver {self.name!r} has no owner system.")

    def _precompute(self) -> None:
        """Set execution order and start the recorder."""
        self.start_time = time.time()

        if self.owner.parent is None and self.parent is None:
            logger.info(" " + "-" * 60)
            logger.info(f" # Starting driver {self.name!r} on {self.owner.name!r}")

        if self._recorder is not None:
            self._recorder.start()

    def _postcompute(self) -> None:
        """Actions performed after the `Module.compute` call."""
        if self._recorder is not None:
            self._recorder.exit()  # TODO Fred Better in clean_run ?

        if self.owner.parent is None and self.parent is None:
            logger.info(
                " # Ending driver {!r} on {!r} in {} seconds\n".format(
                    self.name, self.owner.name, round(time.time() - self.start_time, 3)
                )
            )

    def add_child(self, child: AnyDriver, execution_index: Optional[int] = None) -> AnyDriver:
        """Add a child `Driver` to the current `Driver`.

        When adding a child `Driver`, it is possible to specified its position in the execution
        order.

        Parameters
        ----------
        child: Driver
            `Driver` to add to the current `Driver`
        execution_index: int, optional
            Index of the execution order list at which the `Module` should be inserted;
            default latest.

        Returns
        -------
        `child`

        Notes
        -----
        The added child will have its owner set to that of current driver.
        """
        check_arg(child, 'child', Driver)
        
        driver = super().add_child(child, execution_index)
        driver.owner = self.owner

        return driver

    def add_driver(self, child: AnyDriver, execution_index: Optional[int] = None) -> AnyDriver:
        """Alias for :py:meth:`~cosapp.drivers.driver.Driver.add_child`."""
        return self.add_child(child, execution_index)

    def add_recorder(self, recorder: Recorder) -> Recorder:
        check_arg(recorder, 'recorder', BaseRecorder)

        self._recorder = recorder
        self._recorder.watched_object = self.owner
        self._recorder._owner = self

        return self.recorder

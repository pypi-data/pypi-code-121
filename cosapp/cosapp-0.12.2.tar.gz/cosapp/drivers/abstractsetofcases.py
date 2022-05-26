import abc
from typing import Any, Dict, Iterable, Optional, Union

from cosapp.drivers.driver import Driver


# TODO
# [ ] Quid for vector variables
class AbstractSetOfCases(Driver):
    """
    This driver builds a set of cases from a list

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = ('cases')

    def __init__(
        self,
        name: str,
        owner: Optional["cosapp.systems.System"] = None,
        **kwargs
    ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str, optional
            Name of the `Module`
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)
        # TODO Fred - is this not too much oriented for MonteCarlo or DoE? What about a mission for which input
        # variables may not be the same on all points.
        self.cases = None  # type: Optional[Iterable[Any]]
            # desc="List of cases to be carried out."

    def _precase(self, case_idx: int, case: Any):
        """Hook to be called before running each case.
        
        Parameters
        ----------
        case_idx : int
            Index of the case
        case : Any
            Parameters for this case
        """
        self.status = ""
        self.error_code = "0"

    @abc.abstractmethod
    def _build_cases(self) -> None:
        """Generator of cases."""
        pass

    def _postcase(self, case_idx: int, case: Any):
        """Hook to be called before running each case.
        
        Parameters
        ----------
        case_idx : int
            Index of the case
        case : Any
            Parameters for this case
        """
        if self._recorder is not None:
            self._recorder.record_state(case_idx, self.status, self.error_code)

    def setup_run(self):
        """Actions performed prior to the `Module.compute` call."""
        super().setup_run()
        self._build_cases()

    def run_children(self) -> None:
        """Runs all driver children.
        """
        for child in self.children.values():
            child.run_once()
            if len(child.status) > 0:
                self.status = child.status
            if child.error_code != "0":
                self.error_code = child.error_code

    def compute(self) -> None:
        """Contains the customized `Module` calculation, to execute after children.
        """
        for case_idx, case in enumerate(self.cases):
            if len(case) > 0:
                self._precase(case_idx, case)
                self.run_children()
                self._postcase(case_idx, case)

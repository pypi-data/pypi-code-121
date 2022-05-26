import abc
import json
import numpy
import logging
import re
from copy import copy
from numbers import Number
from typing import (
    AnyStr, Dict, List,
    Callable, Optional,
    Sequence, Tuple, Union,
)

from cosapp.core.numerics.basics import MathematicalProblem, SolverResults
from cosapp.drivers.driver import Driver
from cosapp.drivers.runonce import RunOnce
from cosapp.utils.options_dictionary import OptionsDictionary

logger = logging.getLogger(__name__)


class AbstractSolver(Driver):
    """
    Solve a `System`

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = ('force_init', '_raw_problem', 'problem', 'initial_values', 'solution')

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
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belong; defaults to `None`.
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)

        self.force_init = False  # type: bool
            # desc="Force the initial values to be used."

        self.problem: MathematicalProblem = None
        self.initial_values = numpy.empty(0, dtype=float)
        self.solution: Dict[str, float] = {}
        self.reset_problem()

    def _set_owner(self, system: Optional["cosapp.systems.System"]) -> bool:
        defined = self.owner is not None
        changed = super()._set_owner(system)
        if changed:
            self.reset_problem()
            if defined:
                logger.warning(
                    f"System owner of Driver {self.name!r} has changed. Mathematical problem has been cleared."
                )
        return changed

    @property
    def raw_problem(self) -> MathematicalProblem:
        """MathematicalProblem: raw problem defined at solver level"""
        return self._raw_problem

    def reset_problem(self) -> None:
        """Reset mathematical problem"""
        self._raw_problem = MathematicalProblem(self.name, self.owner)

    def _filter_options(self, kwargs, aliases: Dict[str, str] = dict()):
        """
        Translate option names into self.options using an alias dictionary, to handle cases where
        a common option name, such as 'tol', is passed to a specific solver/function with a different name.
        
        For example, in scipy.optimize.root(), the convergence criterion may be referred to as 'ftol', 'gtol'...
        depending on the invoked algorithm (Levenberg-Marquardt, Powell, Broyden's good, etc.).
        """
        keys = list(kwargs.keys())  # make a copy of keys only

        for key in keys:
            value = kwargs.pop(key)
            try:
                key = aliases[key]
            except KeyError:
                pass
            if key in self.options:
                self.options[key] = value
            else:
                raise KeyError(f"Unknown solver option {key!r}")

    @property
    def _default_driver_name(self) -> str:
        """str : Name for the default driver."""
        return "runner"

    def _get_solver_limits(self) -> Dict[str, numpy.ndarray]:
        """Returns the step limitations for all iteratives.

        There are 4 types of limits defined:
        - lower_bound: lower bound of the iteratives
        - upper_bound: upper bound of the iteratives
        - abs_step: maximal absolute step of the iteratives
        - rel_step: maximal relative step of the iteratives

        Returns
        -------
        Dict[str, numpy.ndarray]
            Dictionary with the limits for all iteratives.
        """
        mapping = {
            "lower_bound": "lower_bound",
            "upper_bound": "upper_bound",
            "abs_step": "max_abs_step",
            "rel_step": "max_rel_step",
        }
        options = dict.fromkeys(mapping, [])

        for unknown in self.problem.unknowns.values():
            for name, attr_name in mapping.items():
                const = getattr(unknown, attr_name)
                array = numpy.full_like(unknown.value, const, dtype=type(const))
                options[name] = numpy.concatenate((options[name], array.flatten()))

        return options

    def compute_before(self):
        """Contains the customized `Module` calculation, to execute before children.
        """
        # Set initial_values to current solution
        # k = 0
        # for value in self.solution.values():
        #     n = numpy.size(value)
        #     self.initial_values[k : k + n] = numpy.reshape(value, -1)
        #     k += n
        logger.debug(f"Set unknowns initial values: {self.initial_values}")
        self.set_iteratives(self.initial_values)

    def setup_run(self) -> None:
        """Set up the mathematical problem."""
        super().setup_run()
        self.problem = MathematicalProblem(self.name, self.owner)
        self.initial_values = numpy.empty(0, dtype=float)

    def run_once(self) -> None:
        """Run solver once, assuming driver has already been initialized.
        """
        with self.log_context(" - run_once"):
            if self.is_active():
                self._precompute()

                logger.debug(f"Call {self.name}.compute_before()")
                self.compute_before()

                # Sub-drivers are executed at each iteration in `compute`,
                # so the child loop before `self.compute()` is omitted.
                logger.debug(f"Call {self.name}.compute()")
                self._compute_calls += 1
                self.compute()

                self._postcompute()
                self.computed.emit()
            
            else:
                logger.debug(f"Skip {self.name} execution - Inactive")

    def _precompute(self) -> None:
        # TODO we should check that all variables are of numerical types
        super()._precompute()

    @abc.abstractmethod
    def set_iteratives(self, x: Sequence[float]) -> None:
        pass

    @abc.abstractmethod
    def resolution_method(self,
        fresidues: Callable[[Sequence[float], Union[float, str], bool], numpy.ndarray],
        x0: Sequence[float],
        args: Tuple[Union[float, str]] = (),
        options: Optional[OptionsDictionary] = None,
    ) -> SolverResults:
        """Function call to cancel the residues.

        Parameters
        ----------
        fresidues : Callable[[Sequence[float], Union[float, str]], numpy.ndarray]
            Residues function taking two parameters (evaluation vector, time/ref) and returning the residues
        x0 : Sequence[float]
            The initial values vector to converge to the solution
        args : Tuple[Union[float, str], bool], optional
            A tuple of additional argument for fresidues starting with the time/ref parameter and the need to update
            residues reference
        options : OptionsDictionary, optional
            Options for the numerical resolution method

        Returns
        -------
        SolverResults
            Solution container
        """
        pass

    # def _postcompute(self) -> None:
    #     # Set initial_values to current solution
    #     k = 0
    #     for value in self.solution.values():
    #         n = numpy.size(value)
    #         self.initial_values[k : k + n] = numpy.reshape(value, -1)
    #         k += n
    #     super()._postcompute()

    def save_solution(self, file: Optional[str] = None) -> Dict[str, Union[Number, List[Number]]]:
        """Save the latest solver solution.

        If `file` is specified, the solution will be saved in it in JSON format.

        Parameters
        ----------
        file : str, optional
            Filename to save the answer in; default None (i.e. data will not be saved)

        Returns
        -------
        Dict[str, Union[Number, List[Number]]]
            Dictionary of the latest solution
        """
        latest_answer = dict()

        for k, v in self.solution.items():
            if isinstance(v, numpy.ndarray):
                v = v.tolist()
            latest_answer[k] = copy(v)

        if file:
            with open(file, "w") as outfile:
                json.dump(latest_answer, outfile)

        return latest_answer

    def load_solution(self,
        solution: Union[Dict[str, Union[Number, numpy.ndarray]], AnyStr],
        case: Optional[str] = None,
    ):
        """Load the provided solution to initialize the solver.

        The solution can be provided directly as a dictionary or from a filename to be read.

        Parameters
        ----------
        solution : Dict[str, Union[Number, numpy.ndarray]] or str
            Dictionary of the latest solution to load or the filename in JSON format to read from.
        case : str, optional
            Case to initialize with the solution; default None (i.e. will be guessed from variable name)
        """
        # TODO Fred is it better to set the initial values or to override the previous solution?
        #   In case the solution does not cover all offdesign unknowns, the later should be better.
        from cosapp.systems import System

        if isinstance(solution, str):
            with open(solution, "r") as f:
                data = json.load(f)
        elif isinstance(solution, dict):
            data = solution
        else:
            raise TypeError(
                f"Solution expected as dict or json file name; got {type(solution).__qualname__!r}."
            )

        def extract_varname(driver, key: str):
            matches = re.findall(f"{driver.name}\[(.*)\]", key)
            if matches:  # Off-design variable
                return matches[0]
            else:
                return key

        with System.set_master(repr(self.owner)) as is_master:
            if is_master:
                self.owner.open_loops()

            try:
                if case is None:
                    for name, value in data.items():
                        for child in filter(
                            lambda d: isinstance(d, RunOnce), self.children.values()
                        ):
                            varname = extract_varname(child, name)
                            if varname != name:  # Off-design variable
                                try:
                                    child.set_init({varname: numpy.asarray(value)})
                                except:
                                    continue
                                else:
                                    break
                            elif varname in child.design.unknowns:  # We may have a design variable
                                child.set_init({varname: numpy.asarray(value)})
                                break
                else:
                    child = self.children[case]
                    if not isinstance(child, RunOnce):
                        raise TypeError(
                            "Only drivers derived from RunOnce can be initialized"
                            f"; got { type(child).__qualname__!r} for driver {case!r}."
                        )
                    for name, value in data.items():
                        varname = extract_varname(child, name)
                        try:
                            child.set_init({varname: numpy.asarray(value)})
                        except:
                            continue

            finally:  # Ensure to clean the system
                if is_master:
                    self.owner.close_loops()

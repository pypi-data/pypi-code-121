import copy
import numpy
import pandas
from io import StringIO
from numbers import Number
from typing import (
    Any, Callable, Dict, List, Optional,
    Sequence, Tuple, Union, Iterable,
    TypeVar,
)

from cosapp.core.numerics.basics import MathematicalProblem, SolverResults
from cosapp.core.numerics.enum import NonLinearMethods
from cosapp.core.numerics.root import root
from cosapp.drivers.driver import Driver
from cosapp.drivers.abstractsolver import AbstractSolver
from cosapp.drivers.driver import Driver
from cosapp.drivers.runsinglecase import RunSingleCase
from cosapp.drivers.utils import DesignProblemHandler
from cosapp.utils.helpers import check_arg
from cosapp.utils.logging import LogFormat, LogLevel

import logging
logger = logging.getLogger(__name__)

AnyDriver = TypeVar("AnyDriver", bound=Driver)


class NonLinearSolver(AbstractSolver):
    """Solve mathematical problem with algebraic variables.

    Attributes
    ----------
    compute_jacobian : bool
        Should the Jacobian matrix be computed? ; default True
    jac_lup : ndarray, optional
        LU decomposition of latest Jacobian matrix (if available, None otherwise)
    jac : ndarray, optional
        Latest Jacobian matrix computed (if available, None otherwise)
    """

    __slots__ = (
        '__method', '__option_aliases', '__trace', '__results',
        '__design_unknowns', 'compute_jacobian', 'jac_lup', 'jac',
    )

    def __init__(self, 
        name: str, 
        owner: Optional["cosapp.systems.System"] = None, 
        method: Union[NonLinearMethods, str] = NonLinearMethods.NR, 
        **kwargs
    ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str, optional
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belong; defaults to `None`.
        method : Union[NonLinearMethods, str]
            Resolution method to use
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)

        if isinstance(method, str):
            method = NonLinearMethods[method]
        else:
            check_arg(method, 'method', NonLinearMethods)
        self.__method = method
        self.__option_aliases = dict()
        self.__set_method(method, **kwargs)
        self.__trace: List[Dict[str, Any]] = list()
        self.__results: SolverResults = None

        self.compute_jacobian = True  # type: bool
            # desc='Should the Jacobian matrix be computed?'

        self.jac_lup = (None, None)  # type: Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]
            # desc='LU decomposition of latest Jacobian matrix (if available).'
        self.jac = None  # type: Optional[numpy.ndarray]
            # desc='Latest computed Jacobian matrix (if available).'

        self.add_child(RunSingleCase(self._default_driver_name))

    def reset_problem(self) -> None:
        """Reset mathematical problem"""
        super().reset_problem()
        self.__design_unknowns = dict()

    @property
    def method(self) -> NonLinearMethods:
        """NonLinearMethods : Selected solver algorithm."""
        return self.__method

    @property
    def results(self) -> SolverResults:
        """SolverResults: structure containing solver results,
        together with additional detail.
        """
        return self.__results

    def add_child(self, child: AnyDriver, execution_index: Optional[int] = None) -> AnyDriver:
        """Add a child `Driver` to the current `Driver`.

        When adding a child `Driver`, it is possible to specified its position in the execution order.

        Child `Port`, `inwards` and `outwards` can also be pulled at the parent level by providing either
        the name of the port/inward/outward or a list of them or the name mapping of the child element
        (dictionary keys) to the parent element (dictionary values).
        If the argument is not a dictionary, the name in the parent system will be the same as in the child.

        Parameters
        ----------
        child: Module
            `Module` to add to the current `Module`
        execution_index: int, optional
            Index of the execution order list at which the `Module` should be inserted;
            default is latest.

        Notes
        -----
        The added child will have its owner set to match the one of the current driver.
        """
        default_driver = self._default_driver_name
        if len(self.children) == 1 and default_driver in self.children:
            self.pop_child(default_driver)
        self.compute_jacobian = True
        return super().add_child(child, execution_index)

    def is_standalone(self) -> bool:
        """Is this Driver able to solve a system?

        Returns
        -------
        bool
            Ability to solve a system or not.
        """
        return True

    def resolution_method(self,
        fresidues: Callable[[Sequence[float], Union[float, str], bool], numpy.ndarray],
        x0: Sequence[float],
        args: Tuple[Union[float, str]] = (),
        options: Optional[Dict[str, Any]] = None
    ) -> SolverResults:

        if self.method == NonLinearMethods.NR:
            self.options.update(self._get_solver_limits())

        common_keys = set(self.options).intersection(options)
        this_options = dict((key, options[key]) for key in common_keys)

        if self.method == NonLinearMethods.NR:
            this_options['compute_jacobian'] = self.compute_jacobian
            this_options['jac_lup'] = self.jac_lup
            this_options['jac'] = self.jac

        results = root(fresidues, x0, args=args, method=self.method, options=this_options)

        if results.jac_lup[0] is not None:
            self.jac_lup = results.jac_lup
            self.jac = results.jac
            self.compute_jacobian = False

        return results

    def setup_run(self) -> None:
        super().setup_run()
        self._init_problem()

    def _print_solution(self) -> None:  # TODO better returning a string
        """Print the solution in the log."""
        if self.options['verbose']:
            # TODO move it in MathematicalProblem
            logger.info(f"Parameters [{len(self.solution)}]: ")
            for k, v in self.solution.items():
                logger.info(f"   # {k}: {v}")

            for name, residue in self.problem.residues.items():
                value = numpy.asarray(residue.value)
                if value.ndim > 0:
                    spacing = " " * len(name)
                    msg = f"Residues [{len(self.problem.residues)}]: \n   # ({name}"
                    msg += f"\n   #  {spacing}".join(f", {v:.5g}" for v in value)
                    msg += ")\n"
                else:
                    logger.info(f"   # ({name}, {value:.5g})")

            tol = numpy.max(numpy.abs(self.problem.residues_vector))
            try:
                option = self.__option_aliases['tol']  # should never fail, in principle
                target = self.options[option]
            except:
                target = 0
            logger.debug(f" # Current tolerance {tol} for target {target}")

    def _init_problem(self):
        """Initialize mathematical problem"""
        logger.debug(
            "\n".join([
                "*" * 40,
                "*", 
                "* Assemble mathematical problem",
                "*",
                "*" * 40,
            ])
        )
        self.problem = MathematicalProblem(self.name, self.owner)
        handler = DesignProblemHandler(self.owner)
        handler.design.extend(self._raw_problem, equations=False)
        handler.offdesign.extend(self._raw_problem, unknowns=False)
        handler.problems = handler.export_problems()  # resolve aliasing
        self.__design_unknowns = handler.design.unknowns
        self.problem.extend(handler.design)
        # handler.offdesign.extend(self.owner.get_unsolved_problem(), copy=True)
        self.initial_values = numpy.append(self.initial_values, self.get_init())
        # Set of unknown names to detect design/offdesign conflicts
        design_unknowns = set(handler.design.unknowns)

        for child in self.children.values():
            if isinstance(child, RunSingleCase):
                local = child.processed_problems
                design_unknowns |= set(local.design.unknowns)
                common = design_unknowns.intersection(local.offdesign.unknowns)
                if common:
                    kind = "unknown"
                    if len(common) > 1:
                        names = ", ".join(repr(v) for v in sorted(common))
                        names = f"({names}) are"
                        kind += "s"
                    else:
                        names = f"{common.pop()!r} is"
                    raise ValueError(
                        f"{names} defined as design and off-design {kind} in {child.name!r}"
                    )
                self.__design_unknowns.update(local.design.unknowns)
                # Enforce solver-level off-design problem to child case
                case_problem = child.add_offdesign_problem(handler.offdesign)
                self.problem.extend(case_problem, copy=False)
                self.initial_values = numpy.append(self.initial_values, child.get_init(self.force_init))

            else:
                logger.warning(
                    f"Including Driver {child.name!r} without iteratives in Driver {self.name!r} is not numerically advised."
                )

        logger.debug(
            "\n".join([
                "Mathematical problem:",
                f"{'<empty>' if self.problem.shape == (0, 0) else self.problem}",
            ])
        )

    def get_init(self) -> numpy.ndarray:
        """Get the System iteratives initial values for this driver.

        Returns
        -------
        numpy.ndarray
            The list of iteratives initial values.
            The values should be in the same order as the unknowns in the `get_problem`.
        """
        full_init = numpy.empty(0)

        for unknown in self.__design_unknowns.values():
            data = copy.deepcopy(unknown.value)
            full_init = numpy.append(full_init, data)

        return full_init

    def _fresidues(self, x: Sequence[float]) -> numpy.ndarray:
        """
        Method used by the solver to take free variables values as input and values of residues as
        output (after running the System).

        Parameters
        ----------
        x : Sequence[float]
            The list of values to set to the free variables of the `System`
        update_residues_ref : bool
            Request residues to update their reference

        Returns
        -------
        numpy.ndarray
            The list of residues of the `System`
        """
        x = numpy.asarray(x)
        logger.debug(f"Call fresidues with x = {x!r}")
        self.set_iteratives(x)

        # Run all points
        for child in self.children.values():
            logger.debug(f"Call {child.name}.run_once()")
            child.run_once()

        residues = self.problem.residues_vector
        logger.debug(f"Residues: {residues!r}")
        return residues

    def set_iteratives(self, x: Sequence[float]) -> None:
        x = numpy.asarray(x)
        counter = 0
        for name, unknown in self.problem.unknowns.items():
            if unknown.mask is None:
                unknown.set_default_value(x[counter])
                counter += 1
            else:
                n = numpy.count_nonzero(unknown.mask)
                unknown.set_default_value(x[counter : counter + n])
                counter += n
            # Set all design variables at once
            if name in self.__design_unknowns:
                # Set the variable to the new x
                if not numpy.array_equal(unknown.value, unknown.default_value):
                    unknown.set_to_default()

    def compute(self) -> None:
        """Run the resolution method to find free vars values that zero out residues
        """
        # Reset status
        self.status = ''
        self.error_code = '0'

        try:
            self.problem.validate()
        except ArithmeticError:
            self.status = 'ERROR'
            self.error_code = '9'
            raise

        if len(self.initial_values) > 0:
            self.solution = {}

            # compute first order
            results = self.resolution_method(
                self._fresidues,
                self.initial_values,
                options=self.options,
            )

            self.__results = results
            self.__trace = getattr(results, "trace", list())

            if results.success:
                self.status = ''
                self.error_code = '0'
                logger.info(f"solver : {self.name}{results.message}")
            
            else:
                self.status = 'ERROR'
                self.error_code = '9'

                error_msg = f"The solver failed: {results.message}"

                error_desc = getattr(results, 'jac_errors', {})
                if error_desc:
                    if len(error_desc['unknowns']) > 0:
                        indices = error_desc['unknowns']
                        unknown_names = [self.problem.unknowns_names[i] for i in indices]
                        error_msg += (
                            f" \nThe {len(indices)} following parameter(s)"
                            f" have no influence: {unknown_names} \n{indices}"
                        )
                    if len(error_desc['residues']) > 0:
                        indices = error_desc['residues']
                        equation_names = [self.problem.residues_names[i] for i in indices]
                        error_msg += (
                            f" \nThe {len(indices)} following residue(s)"
                            f" are not influenced: {equation_names}"
                        )

                if self.parent is not None:
                    raise ArithmeticError(error_msg)
                else:
                    logger.error(error_msg)

            self.solution = dict(
                (key, unknown.default_value)
                for key, unknown in self.problem.unknowns.items()
            )
            self._print_solution()

        else:
            logger.debug('No parameters/residues to solve. Fallback to children execution.')
            self.owner.run_children_drivers()

        if self._recorder is not None:
            for child in self.children.values():
                child.run_once()
                self._recorder.record_state(child.name, self.status, self.error_code)

    def log_debug_message(self,
        handler: "HandlerWithContextFilters",
        record: logging.LogRecord,
        format: LogFormat = LogFormat.RAW
    ) -> bool:
        """Callback method on the driver to log more detailed information.
        
        This method will be called by the log handler when :py:meth:`~cosapp.utils.logging.LoggerContext.log_context`
        is active if the logging level is lower or equals to VERBOSE_LEVEL. It allows
        the object to send additional log message to help debugging a simulation.

        Parameters
        ----------
        handler : HandlerWithContextFilters
            Log handler on which additional message should be published.
        record : logging.LogRecord
            Log record
        format : LogFormat
            Format of the message

        Returns
        -------
        bool
            Should the provided record be logged?
        """
        message = record.getMessage()
        activate = getattr(record, "activate", None)
        emit_record = super().log_debug_message(handler, record, format)

        if message.endswith("call_setup_run") or message.endswith("call_clean_run"):
            emit_record = False

        elif activate == True:
            self.options["history"] = True
            emit_record = False

        elif activate == False:
            self.options["history"] = False
            emit_record = False

            message = ""
            for i, info in enumerate(self.__trace):
                if i == 0:
                    unknowns_trace = info["x"]
                    residues_trace = info["residues"]
                else:
                    unknowns_trace = numpy.vstack((unknowns_trace, info["x"]))
                    residues_trace = numpy.vstack((residues_trace, info["residues"]))

                if "jac" in info:
                    message += f"Iteration {i}\n"
                    container = StringIO()
                    numpy.savetxt(container, info["jac"], delimiter=",")
                    jacobian = container.getvalue()
                    unknowns = ", ".join(self.problem.unknowns_names)
                    message += f"New Jacobian matrix:\n,{unknowns}\n"
                    for residue, line in zip(self.problem.residues_names, jacobian.splitlines()):
                        message += f"{residue}, {line}\n"

            if len(self.__trace) > 0:
                if len(self.__trace) == 1:
                    size = self.problem.shape[0]
                    unknowns_trace = unknowns_trace.reshape((1, size))
                    residues_trace = residues_trace.reshape((1, size))
                unknowns_df = pandas.DataFrame(unknowns_trace, columns=self.problem.unknowns_names)
                container = StringIO()
                unknowns_df.to_csv(container, line_terminator="\n")
                message += f"Unknowns\n{container.getvalue()}\n"
                residues_df = pandas.DataFrame(residues_trace, columns=self.problem.residues_names)
                container = StringIO()
                residues_df.to_csv(container, line_terminator="\n")
                message += f"Residues\n{container.getvalue()}\n"

            handler.log(
                LogLevel.FULL_DEBUG,
                message,
                name=logger.name,
            )

        return emit_record

    def __set_method(self, method, **options):
        check_arg(method, 'method', NonLinearMethods)

        self.__method = method
        self.__option_aliases = dict()

        if self.__method == NonLinearMethods.NR:
            self.options.declare('tol', 'auto', dtype=(float, str), allow_none=True,
                desc='Absolute tolerance (in max-norm) for the residual.')
            self.options.declare('max_iter', 500, dtype=int,
                desc='The maximum number of iterations.')
            # Note: use a power of 2 for `eps`, to guaranty machine-precision accurate gradients in linear problems
            self.options.declare('eps', 2**(-16), dtype=float, allow_none=True, lower=2**(-30),
                desc='Relative step length for the forward-difference approximation of the Jacobian.')
            self.options.declare('factor', 1.0, dtype=Number, allow_none=True, lower=1e-3, upper=1.0,
                desc='A parameter determining the initial step bound factor * norm(diag * x). Should be in interval [0.001, 1].')
            self.options.declare('partial_jac', True, dtype=bool, allow_none=False,
                desc='Defines if partial Jacobian updates can be computed before a complete Jacobian matrix update.')
            self.options.declare('partial_jac_tries', 10, dtype=int, allow_none=False, lower=1, upper=10,
                desc='Defines how many partial Jacobian updates can be tried before a complete Jacobian matrix update.')
            self.options.declare('jac_update_tol', 0.01, dtype=float, allow_none=False, lower=0, upper=1,
                desc='Tolerance level for partial Jacobian matrix update, based on nonlinearity estimation.')
            self.options.declare('recorder', None, allow_none=True,
                desc='A recorder to store solver intermediate results.')
            self.options.declare('lower_bound', None, dtype=numpy.ndarray, allow_none=True,
                desc='Min values for parameters iterated by solver.')
            self.options.declare('upper_bound', None, dtype=numpy.ndarray, allow_none=True,
                desc='Max values for parameters iterated by solver.')
            self.options.declare('abs_step', None, dtype=numpy.ndarray, allow_none=True,
                desc='Max absolute step for parameters iterated by solver.')
            self.options.declare('rel_step', None, dtype=numpy.ndarray, allow_none=True,
                desc='Max relative step for parameters iterated by solver.')
            self.options.declare('history', False, dtype=bool, allow_none=False,
                desc='Request saving the resolution trace.')
            self.options.declare('tol_update_period', 4, dtype=int, lower=1, allow_none=False,
                desc="Tolerance update period, in iteration number, when tol='auto'.")
            self.options.declare('tol_to_noise_ratio', 16, dtype=Number, lower=1.0, allow_none=False,
                desc="Tolerance-to-noise ratio, when tol='auto'.")

        elif self.__method == NonLinearMethods.POWELL:
            self.__option_aliases = {
                'tol': 'xtol',
                'max_eval': 'maxfev',
            }
            self.options.declare('xtol', 1.0e-7, dtype=float,
                desc="The calculation will terminate if the relative error between two consecutive iterations is at most tol.")
            self.options.declare('maxfev', 0, dtype=int,
                desc='The maximum number of calls to the function. If zero, assumes 100 * (N + 1),'
                    ' where N is the number of elements in x0.')
            self.options.declare('eps', None, dtype=float, allow_none=True,
                desc='A suitable step length for the forward-difference approximation of the Jacobian (for fprime=None).'
                    ' If eps is less than machine precision u, it is assumed that the relative errors in the'
                    ' functions are of the order of u.')
            self.options.declare('factor', 0.1, dtype=float, lower=0.1, upper=100.,
                desc='A parameter determining the initial step bound factor * norm(diag * x). Should be in the interval [0.1, 100].')

        elif self.__method == NonLinearMethods.BROYDEN_GOOD:
            self.__option_aliases = {
                'tol': 'fatol',
                'num_iter': 'nit',
                'max_iter': 'maxiter',
                'min_rel_step': 'xtol',
                'min_abs_step': 'xatol',
            }
            self.options.declare('nit', 100, dtype=int,
                desc='Number of iterations to perform. If omitted (default), iterate unit tolerance is met.')
            self.options.declare('maxiter', 200, dtype=int,
                desc='Maximum number of iterations to make. If more are needed to meet convergence, NoConvergence is raised.')
            self.options.declare('disp', False, dtype=bool,
                desc='Print status to stdout on every iteration.')
            self.options.declare('fatol', 6e-6, dtype=float,
                desc='Absolute tolerance (in max-norm) for the residual. If omitted, default is 6e-6.')
            self.options.declare('line_search', 'armijo', dtype=str, allow_none=True,
                desc='Which type of a line search to use to determine the step '
                    'size in the direction given by the Jacobian approximation. Defaults to ‘armijo’.')
            self.options.declare('jac_options', {'reduction_method': 'svd'},
                dtype=dict, allow_none=True,
                desc='Options for the respective Jacobian approximation. restart, simple or svd')

        self._filter_options(options, self.__option_aliases)

    def extend(self, problem: MathematicalProblem, *args, **kwargs) -> MathematicalProblem:
        """Extend solver inner problem.
        
        Parameters
        ----------
        - problem [MathematicalProblem]:
            Source mathematical problem.
        - *args, **kwargs:
            Additional arguments forwarded to `MathematicalProblem.extend`.

        Returns
        -------
        - MathematicalProblem:
            The extended problem.
        """
        return self._raw_problem.extend(problem, *args, **kwargs)

    def add_unknown(self,
        name: Union[str, Iterable[Union[dict, str]]],
        *args, **kwargs,
    ) -> MathematicalProblem:
        """Add design unknown(s).

        More details in `MathematicalProblem.add_unknown`.

        Parameters
        ----------
        - name [str or Iterable of dictionary or str]:
            Name of the variable or collection of variables to be added.
        - *args, **kwargs:
            Additional arguments forwarded to `MathematicalProblem.add_unknown`.

        Returns
        -------
        - MathematicalProblem:
            The updated problem.
        """
        return self._raw_problem.add_unknown(name, *args, **kwargs)

    def add_equation(self,
        equation: Union[str, Iterable[Union[dict, str]]],
        *args, **kwargs,
    ) -> MathematicalProblem:
        """Add off-design equation(s).

        More details in `MathematicalProblem.add_equation`.

        Parameters
        ----------
        - equation [str or Iterable of str of the kind 'lhs == rhs']:
            Equation or collection of equations to be added.
        - *args, **kwargs:
            Additional arguments forwarded to `MathematicalProblem.add_equation`.

        Returns
        -------
        - MathematicalProblem:
            The updated problem.
        """
        return self._raw_problem.add_equation(equation, *args, **kwargs)

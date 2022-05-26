"""
`Driver`s for `System` optimization calculation.
"""
import numpy
import scipy.optimize
import warnings
import copy
from numbers import Number
from typing import (
    Union, Iterable, Callable, Optional,
    Any, Sequence, Dict, List, Set, Tuple,
)
from collections.abc import Collection

from cosapp.core.eval_str import EvalString
from cosapp.core.numerics.basics import MathematicalProblem, SolverResults
from cosapp.core.numerics.boundary import Unknown
from cosapp.drivers.abstractsolver import AbstractSolver
from cosapp.drivers.optionaldriver import OptionalDriver
from cosapp.drivers.utils import UnknownAnalyzer, ConstraintParser
from cosapp.recorders.recorder import BaseRecorder
from cosapp.utils.options_dictionary import OptionsDictionary
from cosapp.utils.helpers import check_arg

import logging
logger = logging.getLogger(__name__)


# TODO
# [ ] Pull unknowns from Systems
class Optimizer(AbstractSolver):
    """Driver running an optimization problem on its `System` owner.

    In general, the optimization problems are of the form::

        minimize f(x) subject to

        g_i(x) >= 0,  i = 1,...,m
        h_j(x)  = 0,  j = 1,...,p

    where ``x`` is a vector of one or more variables. ``g_i(x)`` are the inequality constraints.
    ``h_j(x)`` are the equality constrains.

    Optionally, the lower and upper bounds for each element in x can also be specified.

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options

    Attributes
    ----------
    name : str
        Name of the driver
    parent : Driver, optional
        Top driver containing this driver; default None.
    owner : System
        :py:class:`~cosapp.systems.system.System` to which this driver belong.
    children : OrderedDict[Driver]
        Drivers belonging to this one.

    options : OptionsDictionary
      |  Options for the current driver
      |  **verbose** : int, {0, 1}
      |    Verbosity level of the driver; default 0 (i.e. minimal information)
      |  **eps** : float, [1.5e-8, 1.]
      |    Step size used for numerical approximation of the Jacobian; default 1.5e-8
      |  **ftol** : float, [1.5e-8, 1.]
      |    Iteration termination criteria (f^k - f^{k+1})/max{\|f^k\|,\|f^{k+1}\|,1} <= ftol;
      |    default 1e-6
      |  **max_iter** : int, [1, [
      |    Maximum number of iterations; default 100

    solution :  # TODO

    Notes
    -----
    This optimizer is a wrapper around ``scipy.optimize.minimize`` function. For more details please
    refer to:
    https://docs.scipy.org/doc/scipy-1.0.0/reference/generated/scipy.optimize.minimize.html

    """
    __slots__ = ('_constraints', '_raw_constraints', '_initial_state', '_objective')

    def __init__(self,
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

        # TODO we need to move this in an enhanced MathematicalProblem
        self._raw_constraints: Set[str] = set()  # Human-readable constraints
        self._constraints: List[Dict] = list()   # Non-negativity constraints
        self._initial_state: Dict[str, Any] = dict()
        self._objective: EvalString = None

        self.options.declare(
            name = 'method',
            default = None,
            values = self.available_methods(),
            desc = (
                "Type of solver."
                " If not given, chosen to be one of 'BFGS', 'L-BFGS-B', 'SLSQP',"
                " depending if the problem has constraints or bounds."
            ),
            allow_none = True,
        )
        self.options.declare(
            'eps', 2**(-26), dtype=float, lower=2**(-26), upper=1.,
            desc="Step size used for numerical approximation of the Jacobian.",
        )
        self.options.declare(
            'ftol', 1.5e-8, dtype=float, lower=1e-15, upper=1.,
            desc="Iterations stop when (f^k - f^{k+1}) / max(|f^k|, |f^{k+1}|, 1) <= ftol.",
        )
        self.options.declare(
            'maxiter', 100, dtype=int, lower=1,
            desc='Maximum number of iterations.',
        )
        self.options.declare(
            'monitor', False, dtype=bool, allow_none=False,
            desc="Defines if intermediate system state should be recorded.",
        )
        self._filter_options(kwargs, aliases={'tol': 'ftol', 'max_iter': 'maxiter'})

    def set_minimum(self, expression: str) -> None:
        """Set the scalar objective function to be minimized.

        Parameters
        ----------
        expression : str
            The objective expression to be minimized.
        """
        self.__check_owner("objective")
        check_arg(expression, "expression", str, lambda s: "==" not in s)

        self._objective = objective = EvalString(expression, self.owner)
        if objective.constant:
            warnings.warn(f"Objective is constant {objective.eval()}")

    def set_maximum(self, expression: str) -> None:
        """Set the scalar objective function to be maximized.

        Parameters
        ----------
        expression : str
            The objective expression to be maximized.
        """
        self.set_minimum(f"-({expression})")

    def set_objective(self, expression: str) -> None:
        """Set the scalar quantity to be minimized.
        Same as `set_minimum`.

        Note:
        -----
        This method is deprecated, and should be replaced by either
        `set_minimum` or `set_maximum`, depending on the objective.

        Parameters
        ----------
        expression : str
            The objective expression to be minimized.
        """
        warnings.warn(
            "method `set_objective` is deprecated; use `set_minimum` or `set_maximum` instead."
        )
        self.set_minimum(expression)

    @staticmethod
    def available_methods() -> List[str]:
        """Returns all possible values of option `method`.
        For more information, please refer to the online documentation
        of `scipy.optimize.minimize`.
        """
        return [
            'Nelder-Mead', 'Powell', 'CG', 'BFGS', 'Newton-CG',
            'L-BFGS-B', 'TNC', 'COBYLA', 'SLSQP', 'dogleg',
            'trust-constr', 'trust-ncg', 'trust-exact', 'trust-krylov',
        ]

    @property
    def objective(self):
        try:
            return self._objective.eval()
        except:
            return None

    @property
    def objective_expr(self) -> str:
        return str(self._objective) if self._objective else None

    def add_unknown(self,
            name: Union[str, Iterable[Union[dict, str, Unknown]]],
            max_abs_step: Number = numpy.inf,
            max_rel_step: Number = numpy.inf,
            lower_bound: Number = -numpy.inf,
            upper_bound: Number = numpy.inf
    ) -> "MathematicalProblem":
        """Add unknown variables.

        You can set variable one by one or provide a list of dictionary to set multiple variable at once. The
        dictionary key are the arguments of this method.

        Parameters
        ----------
        name : str or Iterable of dictionary or str
            Name of the variable or list of variable to add
        max_rel_step : float, optional
            Maximal relative step by which the variable can be modified by the numerical solver; default numpy.inf
        max_abs_step : float, optional
            Maximal absolute step by which the variable can be modified by the numerical solver; default numpy.inf
        lower_bound : float, optional
            Lower bound on which the solver solution is saturated; default -numpy.inf
        upper_bound : float, optional
            Upper bound on which the solver solution is saturated; default numpy.inf

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_owner("variables")
        self._raw_problem.add_unknown(name, max_abs_step, max_rel_step, lower_bound, upper_bound)

    def add_constraints(self, expression: Union[str, List[str]]) -> None:
        """Add constraints to the optimization problem.

        Parameters
        ----------
        - expression [str or List[str]]:
            Human-readable equality or inequality constraints, such as
            'x >= y**2', '0 < alpha < 1', 'a == b', or a list thereof.
        
        Note
        ----
        Expressions are parsed into non-negative constraints in the
        optimization problem. Strict inequalities are not enforced,
        and treated as non-strict inequalities.
        For instance, `x < y` translates into: `y - x >= 0`.
        """
        self.__check_owner("constraints")
        check_arg(expression, 'expression', (str, Collection))

        if isinstance(expression, str):
            expression = [expression] 
        
        self._raw_constraints.update(expression)
        constraints = ConstraintParser.parse(expression)

        for constraint in constraints:
            # Test that expression can be evaluated
            try:
                evalstr = EvalString(constraint.expression, self.owner)
            except:
                raise
            data = dict(
                type = 'ineq' if constraint.is_inequality else 'eq',
                expr = evalstr,
            )
            self._constraints.append(data)

    @property
    def constraints(self) -> Set[str]:
        """Set[str]: representation of optimization constraints."""
        return self._raw_constraints.copy()

    def __check_owner(self, kind: str) -> None:
        if self.owner is None:
            raise AttributeError(f"Owner system is required to define optimization {kind}.")

    def setup_run(self):
        """Method called once before starting any simulation."""
        super().setup_run()
        
        # Resolve unknown aliasing and connected unknowns
        analyzer = UnknownAnalyzer(self.owner)
        self.problem = analyzer.filter_problem(self._raw_problem)

    def _fun_wrapper(self, expression: EvalString) -> Callable[[numpy.ndarray], float]:
        """Wrapper around objective and constraint expression to propagate the x values in the
            `System` owner.

        Parameters
        ----------
        expression : EvalString
            The expression to be evaluated.

        Returns
        -------
        Callable[[numpy.ndarray], float]
            Callable function usable by scipy.optimize.minimize
        """

        def wrapper(x: numpy.ndarray, *args) -> float:
            """Wrapper around objective and constraint function to propagate the x values in the
            `System` owner.

            Parameters
            ----------
            x : 1D-scalar numpy.ndarray
                Points at which the function needs to be evaluated
            args : Tuple
                Any additional fixed parameters needed to completely specify the function

            Returns
            -------
            Float
                Value of the function for x
            """
            # Propagate x value in the System owner, if it has changed
            counter = 0
            need_update = False
            for unknown in self.problem.unknowns.values():
                if unknown.mask is None:
                    unknown.set_default_value(x[counter])
                    counter += 1
                else:
                    n = numpy.count_nonzero(unknown.mask)
                    unknown.set_default_value(x[counter:counter + n])
                    counter += n

                # Set the variable to the new x
                if not numpy.array_equal(unknown.value, unknown.default_value):
                    unknown.set_to_default()
                    need_update = True

            if need_update:
                for child in self.exec_order:
                    self.children[child].run_once()

            return expression.eval()

        return wrapper

    def _fresidues(self, x: numpy.ndarray) -> float:
        """
        Method used by the solver to take free variables values as input and values of the objective function (after
        running the System).

        Parameters
        ----------
        x : numpy.ndarray
            The list of values to set to the free variables of the `System`

        Returns
        -------
        float
            Objective function value
        """
        x = numpy.asarray(x)
        logger.debug(f"Call fresidues with x = {x!r}")
        self.set_iteratives(x)

        if len(self.children) > 0:
            for subdriver in self.children.values():
                subdriver.run_once()
        else:
            self.owner.run_children_drivers()

        objective = self._objective.eval()
        logger.debug(f"Objective: {objective!r}")
        return objective

    def set_iteratives(self, x: Sequence[float]) -> None:
        x = numpy.asarray(x)
        counter = 0
        for unknown in self.problem.unknowns.values():
            if unknown.mask is None:
                unknown.set_default_value(x[counter])
                counter += 1
            else:
                n = numpy.count_nonzero(unknown.mask)
                unknown.set_default_value(x[counter : counter + n])
                counter += n
            # Set variable to new x
            if not numpy.array_equal(unknown.value, unknown.default_value):
                unknown.set_to_default()

    def resolution_method(self,
        fresidues: Callable[[Sequence[float]], float],
        x0: numpy.ndarray,
        args: Tuple[Union[float, str], bool] = (),
        options: Optional[OptionsDictionary] = None,
        bounds = None,
        constraints = None,
    ) -> SolverResults:
        """Function call to cancel the residues.

        Parameters
        ----------
        fresidues : Callable[[Sequence[float], Union[float, str]], float]
            Residues function taking two parameters (evaluation vector, time/ref) and returning the residues
        x0 : numpy.ndarray
            The initial values vector to converge to the solution
        args : Tuple[Union[float, str], bool], optional
            A tuple of additional argument for fresidues starting with the time/ref parameter
        options : OptionsDictionary, optional
            Options for the numerical resolution method

        Returns
        -------
        SolverResults
            Solution container
        """
        sub_options = {
            # Specify both `ftol` and `gtol`, as name varies among scipy solvers
            'ftol': options['ftol'],
            'gtol': options['ftol'],  # `ftol` is not understood by unconstrained solvers
            'eps': options['eps'],
            'maxiter': options['maxiter'],
            'disp': bool(options['verbose']),
        }

        def callback(*args, **kwargs) -> bool:
            self._record_data()
            return False

        with warnings.catch_warnings():
            # Ignore warnings about `gtol` or `ftol` potentially emitted by scipy solver
            warnings.filterwarnings("ignore", message="Unknown solver options: [fg]tol")
            output = scipy.optimize.minimize(
                fresidues, x0,
                args=args,
                tol=options['ftol'],
                method=options['method'],
                bounds=bounds,
                constraints=constraints,
                options=sub_options,
                callback=callback,
            )
        if output.fun < self.objective:
            # Solver solution does not correspond to
            # last system execution; rerun to synch.
            self._fresidues(output.x)
            self._record_data()
        return output

    def _precompute(self):
        """List unknowns and gather initial values."""
        super()._precompute()
        OptionalDriver.set_inhibited(True)

        init = numpy.empty(0)

        for name, unknown in self.problem.unknowns.items():
            if not self.force_init and name in self.solution:
                # We ran successfully at least once and are environmental friendly
                data = self.solution[name]

            else:  # User wants the init or first simulation or crash
                try:
                    boundary = self._initial_state[name]
                except KeyError:
                    data = copy.deepcopy(unknown.value)
                else:
                    umask = unknown.mask if unknown.mask is not None else numpy.empty(0)
                    bmask = boundary.mask if boundary.mask is not None else numpy.empty(0)
                    if not numpy.array_equal(umask, bmask):
                        raise ValueError(
                            f"Unknown and initial conditions on {unknown.name!r} are not masked equally"
                        )
                    data = copy.deepcopy(boundary.default_value)
                    # self._initial_state[name] = boundary

            init = numpy.append(init, data)

        self.initial_values = init

    def compute(self) -> None:
        """Execute the optimization."""
        self.status = ''
        self.error_code = '0'

        # Check that objective is set
        if self._objective is None:
            self.status = 'ERROR'
            self.error_code = '9'
            raise ArithmeticError(
                "Optimization objective was not specified."
            )

        # Gather and simplify the bounds
        limits = self._get_solver_limits()
        unique_lower = numpy.unique(limits['lower_bound'])
        unique_upper = numpy.unique(limits['upper_bound'])
        def get_bounds(lower, upper) -> tuple:
            return (
                None if lower == -numpy.inf else lower,
                None if upper ==  numpy.inf else upper
            )
        if unique_lower.size == 1 and unique_upper.size == 1:
            bounds = get_bounds(unique_lower[0], unique_upper[0])
            if bounds == (None, None):
                bounds = None
        else:
            bounds = tuple()

        if bounds is not None:
            bounds = [
                get_bounds(lower, upper)
                for lower, upper in zip(limits['lower_bound'], limits['upper_bound'])
            ]

        # Create nonlinear constraints
        # TODO The following is really ugly. Constraints should be merged
        # from children through MathematicalProblem extension.
        def format_constraint(constraint):
            return {
                'type': constraint['type'],
                'fun': self._fun_wrapper(constraint['expr'])
            }
        constraints = tuple(map(format_constraint, self._constraints))

        if len(self.initial_values) > 0:
            monitored = self.options['monitor']
            BaseRecorder.paused = not monitored
            if monitored:
                self._fresidues(self.initial_values)
                self._record_data()

            results = self.resolution_method(
                self._fresidues,
                self.initial_values,
                args = (),
                bounds = bounds,
                constraints = constraints,
                options = self.options,
            )

            if not results.success:
                self.status = 'ERROR'
                self.error_code = '9'
                self.solution = {}
                logger.error(f"The solver failed: {results.message}")
            else:
                self.solution = dict(
                    (key, unknown.default_value)
                    for key, unknown in self.problem.unknowns.items()
                )
                self._print_solution()

            if not monitored:
                BaseRecorder.paused = False
                self._record_data()

        else:
            logger.warning('No design variable has been specified for the optimization.')

    def _record_data(self) -> None:
        """Record data into recorder, if any."""
        if self._recorder is not None:
            self._recorder.record_state(self.name)

    def _postcompute(self) -> None:
        """Undo pull inputs and reset iteratives sets."""
        OptionalDriver.set_inhibited(False)
        super()._postcompute()

    def _print_solution(self) -> None:  # TODO better returning a string
        """Print the solution in the log."""
        if self.options['verbose']:
            logger.info(f"Objective function: {self._objective.eval():.5g}")
            logger.info(f"Parameters [{len(self.solution)}]: ")
            for name, value in self.solution.items():
                logger.info(f"   # {name}: {value}")
            constraints = self._constraints
            if constraints:
                logger.info(f"Constraints [{len(constraints)}]: ")
                for constraint in constraints:
                    expr = constraint['expr']
                    logger.info(f"   # {expr}: {expr.eval()}")

    def _repr_markdown_(self) -> str:
        """Mardown representation of optimization problem."""
        itemize = lambda item: f"* {item}"

        def section(header: str, collection: Union[str, List[str]]) -> List[str]:
            content = []
            if isinstance(collection, str):
                collection = [collection]
            if collection:
                content.append(f"#### {header.title()}:\n")
                content.extend(map(itemize, collection))
                content.append("")
            return content

        lines = []

        def add_section(header, collection) -> None:
            nonlocal lines
            lines.extend(section(header, collection))
        
        add_section("Objective", f"Minimize {self._objective}")
        add_section("Unknowns", self._raw_problem.unknowns)
        add_section("Constraints", self._raw_constraints)

        return "\n".join(lines)

import logging
from collections import OrderedDict
from numbers import Number
from typing import (
    Any, Dict, Iterable, Optional,
    Sequence, Union, Tuple, List,
    Set, Callable, NamedTuple,
)

import numpy

from cosapp.core.variableref import VariableReference
from cosapp.core.numerics.boundary import Unknown, TimeUnknown, TimeDerivative
from cosapp.core.numerics.residues import Residue, DeferredResidue
from cosapp.utils.naming import natural_varname

logger = logging.getLogger(__name__)


class SolverResults:
    """Storage class for solver solution

    Attributes
    ----------
    x : Sequence[float]
        Solution vector
    success : bool
        Whether or not the solver exited successfully.
    message : str
        Description of the cause of the termination.
    fun : ndarray
        Values of objective function.
    jac_lup : (ndarray[float], ndarray[int]), optional
        LU decomposition of Jacobian given as tuple (LU, perm); (None, None) if not available.
    jac : ndarray, optional
        Values of function Jacobian; None if not available.
    jac_errors : dict, optional
        Dictionary with singular Jacobian matrix error indexes
    jac_calls : int
        Number of calls to the Jacobian matrix calculation
    fres_calls : int
        Number of calls to the residues function
    trace : List[Dict[str, Any]]
        Resolution history (if requested) with the evolution of x, residues and jacobian
    """

    def __init__(self):
        self.x = list()  # type: Sequence[float]
        self.success = False  # type: bool
        self.message = ''  # type: str
        self.fun = numpy.array([], dtype=float)  # type: numpy.ndarray
        self.tol = numpy.nan
        self.jac_lup = (None, None)  # type: Optional[(numpy.ndarray, numpy.ndarray)]
        self.jac = None  # type: Optional[numpy.ndarray]
        self.jac_errors = dict()
        self.jac_calls = 0  # type: int
        self.fres_calls = 0  # type: int
        self.trace = list()  # type: List[Dict[str, Any]]


class WeakDeferredResidue(NamedTuple):
    deferred: DeferredResidue
    weak: bool = False

    @property
    def target(self) -> str:
        """str: targetted quantity"""
        return self.deferred.target

    @property
    def variables(self) -> Set[str]:
        """Set[str]: names of variables involved in residue"""
        return self.deferred.variables

    def target_value(self) -> Any:
        """Evaluates and returns current value of target"""
        return self.deferred.target_value()

    def equation(self) -> str:
        """Returns target equation with updated lhs value"""
        return self.deferred.equation()

    def make_residue(self, reference=None) -> Residue:
        """Generates the residue corresponding to equation 'target == value(target)'"""
        return self.deferred.make_residue(reference)


class MathematicalProblem:
    """Container object for unknowns and equations.

    Parameters
    ----------
    name : str
        Name of the mathematical problem
    context : cosapp.systems.System
        Context in which the mathematical problem will be evaluated.
    """

    def __init__(self, name: str, context: 'Optional[cosapp.systems.System]') -> None:
        # TODO add point label to associate set of equations with Single Case
        self._name = name  # type: str
        self._context = context  # type: Optional[cosapp.systems.System]
        self._unknowns = OrderedDict()  # type: Dict[str, Unknown]
        self._residues = OrderedDict()  # type: Dict[str, Residue]
        self._transients = OrderedDict()  # type: Dict[str, TimeUnknown]
        self._rates = OrderedDict()  # type: Dict[str, TimeDerivative]
        self._targets = OrderedDict()  # type: Dict[str, WeakDeferredResidue]

    def __str__(self) -> str:
        msg = ""
        if len(self.unknowns) > 0:
            msg += "Unknowns\n"
            for name in self.unknowns:
                msg += f"  {name}\n"
        if len(self.residues) > 0:
            msg += "Equations\n"
            for residue in self.residues.values():
                msg += f"  {residue!s}\n"
        return msg

    def __repr__(self) -> str:
        msg = ""
        if len(self.unknowns) > 0:
            msg += "Unknowns\n"
            for unknown in self.unknowns.values():
                msg += f"  {unknown!r}\n"
        if len(self.residues) > 0:
            msg += "Equations\n"
            for residue in self.residues.values():
                msg += f"  {residue!s}\n"
        return msg

    @property
    def name(self) -> str:
        """str : Mathematical system name."""
        return self._name

    @property
    def context(self) -> 'Optional[cosapp.systems.System]':
        """cosapp.systems.System or None : Context in which the mathematical system is evaluated."""
        return self._context

    @context.setter
    def context(self, context: 'Optional[cosapp.systems.System]'):
        if self._context is None:
            self._context = context
        elif context is not self._context:
            raise ValueError(f"Context is already set to {self._context.name!r}.")

    @property
    def residues(self) -> Dict[str, Residue]:
        """Dict[str, Residue] : Residue equations."""
        return self._residues

    @property
    def residues_names(self) -> Tuple[str]:
        """Tuple[str] : Names of residues, flattened to have the same size as `residues_vector`."""
        names = []
        for name, residue in self.residues.items():
            n_values = numpy.size(residue.value)
            if n_values > 1:
                names.extend(f"{name}[{i}]" for i in range(n_values))
            else:
                names.append(name)
        return tuple(names)

    @property
    def residues_vector(self) -> numpy.ndarray:
        """numpy.ndarray : Vector of residues."""
        values = tuple(
            residue.value for residue in self.residues.values()
        )
        return numpy.hstack(values) if values else numpy.empty(0)

    @property
    def n_unknowns(self) -> int:
        """int: Number of unknowns."""
        return sum(
            numpy.size(unknown.value) 
            for unknown in self.unknowns.values()
        )

    @property
    def n_equations(self) -> int:
        """int: Number of equations (including deferred equations)."""
        n_equations = sum(
            numpy.size(residue.value)
            for residue in self.residues.values()
        )
        n_equations += sum(
            numpy.size(deferred.target_value())
            for deferred in self.deferred_residues.values()
        )
        return n_equations

    @property
    def shape(self) -> Tuple[int, int]:
        """(int, int) : Number of unknowns and equations."""
        return (self.n_unknowns, self.n_equations)

    @property
    def unknowns(self) -> Dict[str, Unknown]:
        """Dict[str, Unknown] : Unknown numerical features defined for this system."""
        return self._unknowns

    @property
    def unknowns_names(self) -> Tuple[str]:
        """Tuple[str] : Names of unknowns flatten to have the same size as `residues_vector`."""
        names = []
        for name, unknown in self.unknowns.items():
            n_values = numpy.size(unknown.value)
            if n_values > 1:
                names.extend([f"{name}[{i}]" for i in numpy.arange(n_values)[unknown.mask]])
            else:
                names.append(name)
        return tuple(names)

    def add_unknown(self,
        name: Union[str, Iterable[Union[dict, str, Unknown]]],
        max_abs_step: Number = numpy.inf,
        max_rel_step: Number = numpy.inf,
        lower_bound: Number = -numpy.inf,
        upper_bound: Number = numpy.inf,
        mask: Optional[numpy.ndarray] = None,
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
        mask : numpy.ndarray or None
            Mask of unknown values in the vector variable

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_context("unknowns")
        context = self.context

        def add_unknown(
            name: str,
            max_abs_step: Number = numpy.inf,
            max_rel_step: Number = numpy.inf,
            lower_bound: Number = -numpy.inf,
            upper_bound: Number = numpy.inf,
            mask: Optional[numpy.ndarray] = None,
        ):
            """Set numerical limitations on variables.

            Parameters
            ----------
            context: cosapp.systems.System
                Object in which the unknown is defined
            name : str
                Name of the variable
            max_rel_step : float, optional
                Maximal relative step by which the variable can be modified by the numerical solver; default numpy.inf
            max_abs_step : float, optional
                Maximal absolute step by which the variable can be modified by the numerical solver; default numpy.inf
            lower_bound : float, optional
                Lower bound on which the solver solution is saturated; default -numpy.inf
            upper_bound : float, optional
                Upper bound on which the solver solution is saturated; default numpy.inf
            mask : numpy.ndarray or None
                Mask of unknown values in the vector variable
            """
            # TODO we have a problem here if a vector variable is defined as unknown partially multiple times
            #   Example a = [1, 2, 3] with Unknown1 = a[0] & Unknown2 = a[2]

            unknown = Unknown(context, name, max_abs_step, max_rel_step, lower_bound, upper_bound, mask)
            if unknown.name in self._unknowns:
                logger.info(
                    f"Variable {name!r} is already declared as unknown in {self.name!r}."
                )
            else:
                self._unknowns[unknown.name] = unknown

        params = (max_abs_step, max_rel_step, lower_bound, upper_bound, mask)

        if isinstance(name, str):
            add_unknown(name, *params)
        else:
            for unknown in name:
                if isinstance(unknown, Unknown):
                    current_to_context = context.get_path_to_child(unknown.context)
                    new_name = f"{current_to_context}.{name}" if current_to_context else unknown.name
                    if new_name in self._unknowns:
                        logger.warning(
                            "Unknown {!r} already exists in mathematical system {!r}. "
                            "It will be overwritten.".format(new_name, self.name)
                        )
                    self._unknowns[new_name] = unknown
                elif isinstance(unknown, str):
                    add_unknown(unknown, *params)
                else:
                    add_unknown(**unknown)

        return self

    def add_equation(self,
        equation: Union[str, Iterable[Union[dict, str, Tuple[str, str]]]],
        name: Optional[str] = None,
        reference: Union[Number, numpy.ndarray, str] = 1,
    ) -> "MathematicalProblem":
        """Add residue equation.

        You can add residue equation one by one or provide a list of dictionary to add multiple equation at once. The
        dictionary key are the arguments of this method.

        Parameters
        ----------
        equation : str or Iterable of str of the kind 'lhs == rhs'
            Equation or list of equations to add
        name : str, optional
            Name of the equation; default None => 'lhs == rhs'
        reference : Number, numpy.ndarray or "norm", optional
            Reference value(s) used to normalize the equation; default is 1.
            If value is "norm", actual reference value is estimated from order of magnitude.

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_context("equations")
        context = self.context

        def add_residue(equation, name=None, reference=1):
            """Add residue from equation."""
            residue = Residue(context, equation, name, reference)
            self._residues[residue.name] = residue

        if isinstance(equation, str):
            add_residue(equation, name, reference)
        else:
            for eq in equation:
                if isinstance(eq, str):
                    add_residue(eq)
                elif isinstance(eq, dict):
                    add_residue(**eq)
                else:
                    add_residue(*eq)

        return self

    def add_target(self,
        expression: Union[str, Iterable[str]],
        reference: Union[Number, numpy.ndarray, str] = 1,
        weak = False,
    ) -> "MathematicalProblem":
        """Add deferred equation.

        Parameters
        ----------
        expression: str
            Targetted expression
        reference : Number, numpy.ndarray or "norm", optional
            Reference value(s) used to normalize the (deferred) equation; default is 1.
            If value is "norm", actual reference value is estimated from order of magnitude.
        weak: bool, optional
            If True, the target is disregarded if the corresponding variable is connected; default is `False`.

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_context("targets")
        context = self.context

        def register(name, reference=1):
            deferred = DeferredResidue(context, name, reference)
            if len(deferred.variables) > 1:
                raise NotImplementedError(
                    f"Targets are only supported for single variables; got {deferred.variables}"
                )
            key = self.target_key(deferred.target)
            self._targets[key] = WeakDeferredResidue(deferred, weak)

        if isinstance(expression, str):
            register(expression, reference)
        else:
            for target in expression:
                register(target)

        return self

    def get_target_equations(self) -> List[str]:
        return [deferred.equation() for deferred in self._targets.values()]

    def get_target_residues(self) -> Dict[str, Residue]:
        return dict(
            (key, deferred.make_residue())
            for key, deferred in self._targets.items()
        )

    @staticmethod
    def target_key(target: str) -> str:
        """Returns dict key to be used for targetted quantity `target`"""
        return f"Target[{target}]"

    @property
    def deferred_residues(self) -> Dict[str, WeakDeferredResidue]:
        """Dict[str, WeakDeferredResidue]: Dict of deferred residues defined for this system."""
        return self._targets

    @property
    def transients(self) -> Dict[str, TimeUnknown]:
        """Dict[str, TimeUnknown] : Unknown time-dependent numerical features defined for this system."""
        return self._transients

    def add_transient(self,
        name: str,
        der: Any,
        max_time_step: Union[Number, str] = numpy.inf,
        max_abs_step: Union[Number, str] = numpy.inf,
        pulled_from: Optional[VariableReference] = None,
    ) -> "MathematicalProblem":
        """Add a time-dependent unknown.

        Parameters
        ----------
        name : str
            Name of the new time-dependent (transient) variable
        der : Any
            Name of the variable or evaluable expression defining the time derivative of transient variable
        max_time_step : Number or evaluable expression (str), optional
            Maximal time step for the time integration of the transient variable; numpy.inf by default.
        max_abs_step : Number or evaluable expression compatible with transient variable, optional
            Maximum variable step admissible over one time step; numpy.inf by default.
        pulled_from : VariableReference, optional
            Original time unknown before pulling; None by default.

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_context("transient unknowns")

        if name in self._transients:
            raise ArithmeticError(f"Variable {name!r} is already defined as a time-dependent unknown of {self.name!r}.")

        self._transients[name] = TimeUnknown(self.context, name, der, max_time_step, max_abs_step, pulled_from=pulled_from)
        return self

    @property
    def rates(self) -> Dict[str, TimeDerivative]:
        """Dict[str, TimeDerivative] : Time derivatives computed during system evolution."""
        return self._rates

    def add_rate(self, name: str, source: Any, initial_value: Any = None) -> "MathematicalProblem":
        """Add a time derivative.

        Parameters
        ----------
        name : str
            Name of the new time-dependent (transient) variable
        source : Any
            Name of the variable or evaluable expression whose time derivative will be computed

        Returns
        -------
        MathematicalProblem
            The modified MathematicalSystem
        """
        self.__check_context("rates")

        if name in self._rates:
            raise ArithmeticError(f"Variable {name!r} is already defined as a time-dependent unknown of {self.name!r}.")

        self._rates[name] = TimeDerivative(self.context, name, source, initial_value)
        return self

    def __check_context(self, name: str):
        if self.context is None:
            raise AttributeError(f"Owner System is required to define {name}.")

    @staticmethod
    def naming_functions(system1, system2) -> Tuple[Callable[[str], str], Callable[[str], str]]:
        """Returns name mapping functions for variables and residues,
        based on contexts `system1` and `system2`.
        Each function maps a str to a str.

        Returns
        -------
        var_name, res_name: tuple of Callable[[str], str]
            Variable and residue name functions.
        """
        if system1 is not system2:
            path = system1.get_path_to_child(system2)
            var_name = lambda name: f"{path}.{name}"
            res_name = lambda name: var_name(name if name.endswith(')') else f"({name})")
        else:
            var_name = res_name = lambda name: name
        return var_name, res_name

    def extend(self,
        other: "MathematicalProblem",
        copy = True,
        unknowns = True,
        equations = True,
        overwrite = False,
    ) -> "MathematicalProblem":
        """Extend the current mathematical system with the other one.

        Parameters
        ----------
        - other [MathematicalProblem]:
            The other mathematical system to add
        - copy [bool, optional]:
            Should the objects be copied; default is `True`.
        - unknowns [bool, optional]:
            If `False`, unknowns are discarded; default is `True`.
        - equations [bool, optional]:
            If `False`, equations are discarded; default is `True`.
        - overwrite [bool, optional]:
            If `False` (default), common unknowns/equations raise `ValueError`.
            If `True`, attributes are silently overwritten.

        Returns
        -------
        MathematicalProblem
            The resulting mathematical system
        """
        if other is self and not copy:
            return self  # quick return

        var_name, residue_name = self.naming_functions(self.context, other.context)

        get = (lambda obj: obj.copy()) if copy else (lambda obj: obj)

        def transfer(self_dict, other_dict, get_fullname):
            for name, elem in other_dict.items():
                fullname = get_fullname(name)
                if not overwrite and fullname in self_dict:
                    raise ValueError(f"{fullname!r} already exists in {self.name!r}.")
                self_dict[fullname] = get(elem)

        if unknowns:
            transfer(self._unknowns, other.unknowns, var_name)
            transfer(self._transients, other.transients, var_name)
            transfer(self._rates, other.rates, var_name)

        if equations:
            transfer(self._residues, other.residues, residue_name)

            connectors = list(self.context.incoming_connectors())
            name2variable = other.context.name2variable

            for deferred in other._targets.values():
                targetted = list(deferred.variables)[0]
                name = deferred.target.replace(targetted, var_name(targetted))  # default
                ref = name2variable[targetted]
                port = ref.mapping
                for connector in connectors:
                    # Check if targetted var is a pulled output
                    if port is connector.source and port.is_output and ref.key in connector.source_variables():
                        alias = natural_varname(
                            f"{connector.sink.name}.{connector.sink_variable(ref.key)}"
                        )
                        original = name
                        if deferred.target == targetted:
                            name = alias
                        else:
                            # target is an expression involving `targetted`
                            name = name.replace(var_name(targetted), alias)
                        logger.info(
                            f"Target on {original!r} will be based on {name!r} in the context of {self.context.full_name()!r}"
                        )
                        break
                self.add_target(name, weak=deferred.weak)

        return self

    def clear(self) -> None:
        """Clear all mathematical elements in this problem."""
        self._unknowns.clear()
        self._residues.clear()
        self._transients.clear()
        self._rates.clear()
        self._targets.clear()

    def copy(self) -> 'MathematicalProblem':
        """Copy the `MathematicalSystem` object.

        Returns
        -------
        MathematicalProblem
            The duplicated mathematical problem.
        """
        new = MathematicalProblem(self.name, self.context)
        return new.extend(self, copy=True)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSONable representation of the mathematical problem.
        
        Returns
        -------
        Dict[str, Any]
            JSONable representation
        """
        return {
            "unknowns": dict((name, unknown.to_dict()) for name, unknown in self.unknowns.items()),
            "equations": dict((name, equation.to_dict()) for name, equation in self.residues.items()),
            "transients": dict((name, transient.to_dict()) for name, transient in self.transients.items()),
            "rates": dict((name, rate.to_dict()) for name, rate in self.rates.items())
        }

    def validate(self) -> None:
        """Verifies that there are as much unknowns as equations defined.

        Raises
        ------
        ArithmeticError
            If the mathematical system is not closed.
        """
        n_unknowns, n_equations = self.shape
        if n_unknowns != n_equations:
            msg = "Nonlinear problem {} error: Mismatch between numbers of params [{}] and residues [{}]".format(
                self.name, n_unknowns, n_equations
            )
            logger.error(msg)
            logger.error(f"Residues: {list(self.residues) + list(self.deferred_residues)}")
            logger.error(f"Variables: {list(self.unknowns)}")
            raise ArithmeticError(msg)

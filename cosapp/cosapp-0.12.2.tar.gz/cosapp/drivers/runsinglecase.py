import numpy
from typing import Any, Iterable, Dict, Optional, Union, List

from cosapp.core.eval_str import AssignString
from cosapp.core.numerics.basics import MathematicalProblem
from cosapp.core.numerics.boundary import Boundary
from cosapp.drivers.iterativecase import IterativeCase
from cosapp.drivers.utils import DesignProblemHandler
from cosapp.ports.enum import PortType
from cosapp.systems import System
from cosapp.utils.helpers import check_arg

import logging
logger = logging.getLogger(__name__)


class RunSingleCase(IterativeCase):
    """Set new boundary conditions and equations on the system.

    By default, it has a :py:class:`~cosapp.drivers.runonce.RunOnce` driver as child to run the system.

    Attributes
    ----------
    case_values : List[AssignString]
        List of requested variable assignments to set up the case
    initial_values : Dict[str, Tuple[Any, Optional[numpy.ndarray]]]
        List of variables to set with the values to set and associated indices selection

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = ('__case_values', '__raw_problem', '__processed', 'problem')

    def __init__(
        self,
        name: str,
        owner: Optional[System] = None,
        **kwargs
        ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str, optional
            Name of the `Module`
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
        **kwargs : Dict[str, Any]
            Optional keywords arguments formwarded to base class.
        """
        super().__init__(name, owner, **kwargs)
        self.__case_values = []  # type: List[AssignString]
            # desc="List of assignments 'lhs <- rhs' to perform in the present case.")
        self.problem = None # type: Optional[MathematicalProblem]
            # desc='Full mathematical problem to be solved on this case.'
        self.__raw_problem = DesignProblemHandler(owner)
        self.__processed = DesignProblemHandler(owner)
        self.owner = owner

    @property
    def design(self) -> MathematicalProblem:
        """MathematicalProblem: Design problem solved for case"""
        return self.__raw_problem.design

    @property
    def offdesign(self) -> MathematicalProblem:
        """MathematicalProblem: Local problem solved for case"""
        return self.__raw_problem.offdesign

    @property
    def processed_problems(self) -> DesignProblemHandler:
        """DesignProblemHandler: design/off-design problem handler"""
        return self.__processed

    def reset_problem(self) -> None:
        """Reset design and off-design problems defined on case."""
        self.__raw_problem = DesignProblemHandler(self.owner)
        self.__processed = DesignProblemHandler(self.owner)
        self.problem = None

    def merge_problems(self) -> None:
        self.problem = self.merged_problem()

    def merged_problem(self) -> MathematicalProblem:
        handler = self.__processed
        name = self.name
        try:
            return handler.merged_problem(name=name, offdesign_prefix=name)
        except ValueError as error:
            error.args = (f"{error.args[0]} in {name!r}",)
            raise

    def setup_run(self):
        """Method called once before starting any simulation."""
        super().setup_run()
        
        raw = self.__raw_problem
        # Force graph analysis by creating new problem handler
        self.__processed = DesignProblemHandler(self.owner)
        processed = self.__processed
        # Transfer problem copies from `raw` to `processed`
        processed.problems = raw.export_problems(prune=False)

        # Add owner off-design problem to `processed.offdesign`
        owner_problem = self.owner.get_unsolved_problem()
        processed.offdesign.extend(owner_problem)

        # Resolve unknown aliasing in `processed`
        processed.problems = processed.export_problems()
        self.merge_problems()

    def add_offdesign_problem(self, offdesign: MathematicalProblem) -> MathematicalProblem:
        """Add outer off-design problem to inner problem.

        Returns:
        ----------
        - `MathematicalProblem`
            The modified mathematical problem
        """
        # Unknowns & residues are duplicated to avoid side effects between points
        # Existing unknowns and equations are silently overwritten.
        if offdesign.shape != (0, 0):
            self.__processed.offdesign.extend(offdesign, copy=True, overwrite=True)
            self.merge_problems()
        return self.problem

    def _precompute(self) -> None:
        """Actions to carry out before the :py:meth:`~cosapp.drivers.runonce.RunOnce.compute` method call.

        It sets the boundary conditions and changes variable status.
        """
        super()._precompute()

        # Set boundary conditions
        for assignment in self.case_values:
            value, changed = assignment.exec()
            if changed:
                self.owner.set_dirty(PortType.IN)

        # Set offdesign variables
        design_unknowns = set(self.design.unknowns)
        problem = self.get_problem()
        for name, unknown in problem.unknowns.items():
            if name in design_unknowns:
                continue
            if not numpy.array_equal(unknown.value, unknown.default_value):
                unknown.set_to_default()

    def clean_run(self):
        """Method called once after any simulation."""
        self.problem = None

    def get_problem(self) -> MathematicalProblem:
        """Returns the full mathematical for the case.

        Returns
        -------
        MathematicalProblem
            The full mathematical problem to solve for the case
        """
        if self.problem is None:
            logger.warning("RunSingleCase.get_problem called with no prior call to RunSingleCase.setup_run.")
            return MathematicalProblem(self.name, self.owner)
        else:
            return self.problem

    def set_values(self, modifications: Dict[str, Any]) -> None:
        """Enter the set of variables defining the case, from a dictionary of the kind {'variable1': value1, ...}
        Note: will erase all previously defined values. Use 'add_values' to append new case values.

        The variable can be contextual `child1.port2.var`. The only rule is that it should belong to
        the owner `System` of this driver or any of its descendants.

        Parameters
        ----------
        modifications : Dict[str, Any]
            Dictionary of (variable name, value)

        Examples
        --------
        >>> driver.set_values({'myvar': 42, 'port.dummy': 'banana'})
        """
        self.clear_values()
        self.add_values(modifications)

    def add_values(self, modifications: Dict[str, Any]) -> None:
        """Add a set of variables to the list of case values, from a dictionary of the kind {'variable1': value1, ...}

        The variable can be contextual `child1.port2.var`. The only rule is that it should belong to
        the owner `System` of this driver or any of its descendants.

        Parameters
        ----------
        modifications : Dict[str, Any]
            Dictionary of (variable name, value)

        Examples
        --------
        >>> driver.add_values({'myvar': 42, 'port.dummy': 'banana'})
        """
        owner = self.owner
        if owner is None:
            raise AttributeError(
                f"Driver {self.name!r} must be attached to a System to set case values."
            )
        check_arg(modifications, 'modifications', dict)

        for variable, value in modifications.items():
            Boundary.parse(owner, variable)  # checks that variable is valid
            self.__case_values.append(AssignString(variable, value, owner))

    def add_value(self, variable: str, value: Any) -> None:
        """Add a single variable to list of case values.

        The variable can be contextual `child1.port2.var`. The only rule is that it should belong to
        the owner `System` of this driver or any of its descendants.

        Parameters
        ----------
        variable : str
            Name of the variable
        value : Any
            Value to be used.

        Examples
        --------
        >>> driver.add_value('myvar', 42)
        """
        self.add_values({variable: value})

    def clear_values(self):
        self.__case_values.clear()

    @property
    def case_values(self) -> List[AssignString]:
        return self.__case_values

    def extend(self, problem: MathematicalProblem) -> MathematicalProblem:
        """Extend local problem. Shortcut to `self.offdesign.extend(problem)`.
        
        Parameters
        ----------
        - problem: MathematicalProblem

        Returns
        -------
        MathematicalProblem
            The extended mathematical problem
        """
        return self.offdesign.extend(problem)

    def add_unknown(self,
        name: Union[str, Iterable[Union[dict, str]]],
        *args, **kwargs,
    ) -> MathematicalProblem:
        """Add local unknown(s).
        Shortcut to `self.offdesign.add_unknown(name, *args, **kwargs)`.

        More details in `MathematicalProblem.add_unknown`.

        Parameters
        ----------
        - name: str or Iterable of dictionary or str
            Name of the variable or list of variables to add
        - *args, **kwargs: Forwarded to `MathematicalProblem.add_unknown`

        Returns
        -------
        MathematicalProblem
            The modified mathematical problem
        """
        return self.offdesign.add_unknown(name, *args, **kwargs)

    def add_equation(self,
        equation: Union[str, Iterable[Union[dict, str]]],
        *args, **kwargs,
    ) -> MathematicalProblem:
        """Add local equation(s).
        Shortcut to `self.offdesign.add_equation(equation, *args, **kwargs)`.

        More details in `MathematicalProblem.add_equation`.

        Parameters
        ----------
        - equation: str or Iterable of str of the kind 'lhs == rhs'
            Equation or list of equations to add
        - *args, **kwargs: Forwarded to `MathematicalProblem.add_equation`

        Returns
        -------
        MathematicalProblem
            The modified mathematical problem
        """
        return self.offdesign.add_equation(equation, *args, **kwargs)

    def add_target(self,
        expression: Union[str, Iterable[str]],
        *args, **kwargs,
    ) -> MathematicalProblem:
        """Add deferred equation(s) on current point.
        Shortcut to `self.offdesign.add_target(expression, *args, **kwargs)`.

        More details in `MathematicalProblem.add_target`.

        Parameters
        ----------
        - expression: str
            Targetted expression
        - *args, **kwargs : Forwarded to `MathematicalProblem.add_target`

        Returns
        -------
        MathematicalProblem
            The modified mathematical problem
        """
        return self.offdesign.add_target(expression, *args, **kwargs)

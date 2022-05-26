import enum
from typing import Optional, Union, Dict, Tuple, List, Set, NamedTuple
from collections.abc import Collection

from cosapp.core.numerics.boundary import Unknown
from cosapp.core.numerics.basics import MathematicalProblem
from cosapp.core.eval_str import EvalString
from cosapp.utils.helpers import check_arg
from cosapp.utils.parsing import multi_split

import logging
logger = logging.getLogger(__name__)


class SystemAnalyzer:
    """Class containing data collected on a system,
    to be shared between different drivers.
    """
    __slots__ = ('__system', '__data')

    def __init__(self, system: Optional["cosapp.systems.System"] = None):
        self.__reset()
        self.system = system

    @property
    def data(self) -> Dict:
        return self.__data

    @property
    def system(self) -> "cosapp.systems.System":
        "System: system of interest"
        return self.__system

    @system.setter
    def system(self, system) -> None:
        if system is self.__system:
            return
        from cosapp.systems.system import System
        check_arg(system, 'system', (System, type(None)))
        self.__reset(system)

    def __reset(self, system=None) -> None:
        """Reset system and data, with no type check"""
        self.__system = system
        self.__data = dict()

    def clear_data(self) -> None:
        self.__data.clear()

    def check_system(self) -> None:
        if self.system is None:
            raise ValueError("object is not associated to any system")


class UnknownAnalyzer(SystemAnalyzer):
    """Class used to resolve unknown aliasing
    """
    def __init__(self, system: "cosapp.systems.System"):
        super().__init__(system)

    @property
    def input_mapping(self):
        return self.system.input_mapping

    def filter_problem(self, problem: MathematicalProblem, name=None) -> MathematicalProblem:
        self.check_system()
        context = self.system
        if problem.context is not context:
            raise ValueError(f"problem is not defined on system {context.name!r}")
        if not name:
            name = f"{problem.name}[filtered]"
        filtered = MathematicalProblem(name, problem.context)
        # Add equations
        filtered.extend(problem, unknowns=False)
        # Add unknowns
        input_mapping = self.input_mapping

        def get_free_unknown(unknown: Unknown, key: str) -> Union[Unknown, None]:
            """Checks if `unknown` is aliased by pulling.
            If so, returns alias unknown; else, returns original unknown.
            """
            try:
                alias = input_mapping[key]
            except KeyError:
                logger.warning(f"Skip connected unknown {key!r}")
                return None
            if alias.mapping is not unknown.port:
                if alias.context is not context:
                    alias_name = f"{alias.mapping.contextual_name}.{alias.key}"
                    contextual_name = f"{unknown.context.name}.{key}"
                    logger.warning(
                        f"Unknown {contextual_name!r} is aliased by {alias_name!r}"
                        f", defined outside the context of {context.name!r}"
                        f"; it is likely to be overwritten after the computation."
                    )
                else:
                    alias_name = f"{alias.mapping.name}.{alias.key}"
                    logger.info(f"Replace unknown {key!r} by {alias_name!r}")
                    unknown = unknown.transfer(alias.context, alias_name)
            return unknown
        
        for key, unknown in problem.unknowns.items():
            free_unknown = get_free_unknown(unknown, key)
            if free_unknown is None:
                continue
            aliased = (free_unknown is not unknown)
            if aliased:
                key = free_unknown.name
                filtered.unknowns[key] = free_unknown
            else:
                filtered.unknowns[key] = unknown.copy()

        return filtered


class DesignProblemHandler:
    """Class managing tied design and off-design problems,
    including unknown aliasing.
    """
    def __init__(self, system: "cosapp.systems.System"):
        self.__handler = UnknownAnalyzer(system)
        self.reset()

    @classmethod
    def make(cls, design: MathematicalProblem, offdesign: MathematicalProblem) -> "DesignProblemHandler":
        handler = cls(design.context)
        handler.problems = (design, offdesign)
        return handler

    @property
    def system(self) -> "cosapp.systems.System":
        return self.__handler.system

    @system.setter
    def system(self, system) -> None:
        self.__handler.system = system
        for name in ('design', 'offdesign'):
            problem = getattr(self, name)
            try:
                problem.context = system
            except ValueError:
                setattr(self, name, self.new_problem(name))

    @property
    def problems(self) -> Tuple[MathematicalProblem, MathematicalProblem]:
        """Tuple[MathematicalProblem, MathematicalProblem]: design and off-design problems as a tuple"""
        return self.design, self.offdesign

    @problems.setter
    def problems(self, problems) -> None:
        """Setter for (design, offdesign) tuple"""
        design, offdesign = problems
        if design is None:
            design = self.new_problem('design')
        if offdesign is None:
            offdesign = self.new_problem('offdesign')
        if design.context is not offdesign.context:
            raise ValueError("Design and off-design problems must be defined in the same context")
        self.design, self.offdesign = problems
        self.__handler.system = design.context

    def reset(self) -> None:
        """Reset handler"""
        self.design = self.new_problem('design')
        self.offdesign = self.new_problem('offdesign')

    def new_problem(self, name: str) -> MathematicalProblem:
        """Create new `MathematicalProblem` instance"""
        return MathematicalProblem(name, self.system)

    def export_problems(self, prune=True) -> Tuple[MathematicalProblem, MathematicalProblem]:
        """Export design and off-design problems.
        
        Parameters:
        -----------
        - prune, Optional[bool]:
            If `True` (default), resolve unknown aliasing first.
            If `False`, returned problems are copies of object attributes.

        Results:
        --------
        - (design, offdesign): Filtered design and off-design problems,
            as a tuple of `MathematicalProblem` objects.
        """
        if prune:
            handler = self.__handler
            design = handler.filter_problem(self.design, name='design')
            offdesign = handler.filter_problem(self.offdesign, name='offdesign')
        else:
            design = self.design.copy()
            offdesign = self.offdesign.copy()
        return design, offdesign

    def merged_problem(self, name="merged", offdesign_prefix="offdesign") -> MathematicalProblem:
        """Merge design and off-design problems into a single `MathematicalProblem` instance.
        """
        design, offdesign = self.export_problems()

        def check(attr, kind):
            design_attr = getattr(design, attr)
            offdesign_attr = getattr(offdesign, attr)
            common = set(design_attr).intersection(offdesign_attr)
            if common:
                if len(common) > 1:
                    names = ", ".join(repr(v) for v in sorted(common))
                    names = f"({names}) are"
                    kind += "s"
                else:
                    names = f"{common.pop()!r} is"
                raise ValueError(
                    f"{names} defined as design and off-design {kind}"
                )
        check('unknowns', kind='unknown')
        check('residues', kind='equation')
        
        merged = self.new_problem(name)
        no_rename = lambda name: name
        local_name = (lambda name: f"{offdesign_prefix}[{name}]") if offdesign_prefix else no_rename

        def add_problem(problem: MathematicalProblem, rename_unknowns=True) -> None:
            nonlocal merged
            rename = local_name if rename_unknowns else no_rename

            # Add unknowns
            for name in list(problem.unknowns.keys()):
                merged.unknowns[rename(name)] = problem.unknowns.pop(name)
            
            # Add residues
            for name in list(problem.residues.keys()):
                merged.residues[local_name(name)] = problem.residues.pop(name)

            for name, residue in problem.get_target_residues().items():
                merged.residues[local_name(name)] = residue

        add_problem(design, rename_unknowns=False)
        add_problem(offdesign, rename_unknowns=True)
        return merged

    def extend(self, other: "DesignProblemHandler", prune=True, copy=True, overwrite=False) -> "DesignProblemHandler":
        if prune or copy:
            design, offdesign = other.export_problems(prune)
        else:
            design, offdesign = other.problems
        # Extend inner problems; copy is unnecessary at this point,
        # as `design` and `offdesign` are consistent with argument `copy`.
        options = dict(copy=False, overwrite=overwrite)
        self.design.extend(design, **options)
        self.offdesign.extend(offdesign, **options)
        return self


@enum.unique
class ConstraintType(enum.Enum):
    """Enum covering constraint types"""
    GE = {
        'operator': ">=",
        'sort': (lambda lhs, rhs: (lhs, rhs)),
    }
    LE = {
        'operator': "<=",
        'sort': (lambda lhs, rhs: (rhs, lhs)),
    }
    EQ = {
        'operator': "==",
        'sort': (lambda lhs, rhs: (lhs, rhs)),
    }

    def expression(self, lhs: str, rhs: str) -> str:
        return "{} - ({})".format(*self.sort(lhs, rhs))

    def sort(self, lhs: str, rhs: str) -> Tuple[str, str]:
        return self.value['sort'](lhs, rhs)

    def __str__(self) -> str:
        return self.description

    @property
    def operator(self) -> str:
        return self.value['operator']

    @property
    def description(self) -> str:
        return f"Constraint of the kind `lhs {self.operator} rhs`"

    @property
    def is_inequality(self) -> bool:
        return self.operator != "=="


class Constraint(NamedTuple):
    """Named tuple representing a non-negative constraint
    of the kind `lhs <op> rhs`, where `<op>` is either
    `==` (equality) or `>=` (inequality constraint),
    depending on Boolean attribute `is_inequality`.

    Attributes:
    -----------
    - lhs [str]: left-hand side.
    - rhs [str]: right-hand side.
    - is_inequality [bool].

    Properties:
    -----------
    - expression [str]: non-negative constraint `lhs - rhs`.
    """
    lhs: str
    rhs: str
    is_inequality: bool = True

    @property
    def expression(self) -> str:
        return f"{self.lhs} - ({self.rhs})"

    def __str__(self) -> str:
        op = ">=" if self.is_inequality else "=="
        return f"{self.expression} {op} 0"


class ConstraintParser:

    @classmethod
    def parse(cls, expression: Union[str, List[str]]) -> Set[Constraint]:
        """Parse a string expression or a list thereof as a
        set of non-negative constraints to be used in solvers.

        Parameters:
        -----------
        - expression [str or List[str]]:
            Human-readable equality or inequality constraints,
            such as 'x >= y', '0 < alpha < 1', or a list thereof.
        
        Returns:
        --------
        - constraints [Set[Constraint]]:
            Set of `Constraint` named tuple objects.
        """
        check_arg(expression, 'expression', (str, Collection))
        ctypes = cls.types()
        not_in_sides = list(ctypes) + ["="]
        
        def side_ok(side: str) -> bool:
            return not any(nogo in side for nogo in not_in_sides) and side.strip()

        def parse_single(expression: str) -> Set[Constraint]:
            check_arg(expression, 'expression', str)
            constraints = set()

            for operator in "<>":
                expression = expression.replace(f"{operator}=", operator)

            expressions, operators = multi_split(expression, ctypes.keys())

            for lhs, rhs, operator in zip(expressions, expressions[1:], operators):
                ok = side_ok(lhs) and side_ok(rhs)
                ctype = ctypes[operator]
                constraint = Constraint(
                    *ctype.sort(lhs, rhs),
                    ctype.is_inequality,
                )
                if not ok:
                    raise ValueError(f"Invalid constraint {constraint.expression}")
                constraints.add(constraint)

            return constraints
        
        expressions = [expression] if isinstance(expression, str) else expression

        constraints = set()
        for expression in expressions:
            constraints |= parse_single(expression)

        return constraints

    @classmethod
    def types(cls) -> Dict[str, ConstraintType]:
        return {
            ">" : ConstraintType.GE,
            "<" : ConstraintType.LE,
            "<=": ConstraintType.LE,
            "==": ConstraintType.EQ,
            ">=": ConstraintType.GE,
        }

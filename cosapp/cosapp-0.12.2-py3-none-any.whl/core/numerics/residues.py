from abc import abstractmethod
from numbers import Number
from typing import Any, Dict, Optional, Tuple, Set, Union
from collections.abc import Collection

import numpy

from cosapp.core.eval_str import EvalString
from cosapp.utils.helpers import check_arg


class AbstractResidue:
    """Abstract class defining residue for solvers.

    Parameters
    ----------
    - context : cosapp.core.module.Module
        CoSApp Module in which this residue is defined
    - name : str
        Residue name
    """

    def __init__(
        self,
        context: "System",
        name: str,
    ):
        from cosapp.systems import System
        check_arg(context, "context", System)
        check_arg(name, "name", str)
        self._reference_value = 1.0
        self._value = None  # type: Union[Number, numpy.ndarray]
        self._context = context  # type: System
        self._name = name  # type: str
        super().__init__()

    def __str__(self) -> str:
        return f"{self._name} := {self._value}"

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self._name}): {self._value!s}"

    def _get_zeros_rhs(self, lhs: Union[str, Number, numpy.ndarray]) -> Union[str, Number, numpy.ndarray]:
        """Generate the default zeroed right-hand side of the residue equation.

        The default right-hand side is a zero value or vector. If the left
        hand side is defined by a string to be evaluated, the right hand
        side will be expressed as a string to evaluate.

        Attributes
        ----------
        lhs : str
            Left-hand side of the residue equation

        Returns
        -------
        Union[str, Number, numpy.ndarray]
            Default zeroed right-hand side
        """
        if isinstance(lhs, str):
            lhs_evaluated = EvalString(lhs, self.context).eval()
            return f"zeros({numpy.shape(lhs_evaluated)})"
        else:
            return numpy.zeros_like(numpy.asarray(lhs))

    @abstractmethod
    def update(self, **kwargs) -> Union[Number, numpy.ndarray]:
        """Update the value of the residue.

        Returns
        -------
        Number or numpy.ndarray
            The updated value
        """
        # TODO kwargs is bad
        pass

    @property
    def reference(self) -> Union[Number, numpy.ndarray]:
        """Number or numpy.ndarray: Reference value to normalize the residue with."""
        return self._reference_value

    @reference.setter
    def reference(self, value: Union[Number, numpy.ndarray]) -> None:
        """Set the reference value.

        Parameters
        ----------
        value : Union[Number, numpy.ndarray]
            User defined reference value; default None (guessed by the solver)
        """
        self._reference_value = value

    @property
    def context(self) -> "System":
        """System: CoSApp system usable in string evaluation."""
        return self._context

    @property
    def name(self) -> str:
        """str : Residue name"""
        return self._name

    @property
    def value(self) -> Union[Number, numpy.ndarray]:
        """Number or numpy.ndarray: residue's value."""
        return self._value

    @abstractmethod
    def copy(self) -> "AbstractResidue":
        """Copy the object.

        Returns
        -------
        AbstractResidue
            The duplicated object.
        """
        pass


class Residue(AbstractResidue):
    """Classical residue definition based on an equality equation

    Left-hand side == Right-hand side

    The right-hand side is assumed null if not specified.

    The residue can be defined by providing directly the numerical values
    of the left and right-hand sides. An alternative is to provide an string
    expression to be evaluated.

    Parameters
    ----------
    - context : cosapp.systems.System
        CoSApp System to which residue is linked
    - lhs : Number or numpy.ndarray or str
        Left-hand side of the equation.
    - rhs : Number or numpy.ndarray or str or None, optional
        Right-hand side of the equation; default None (i.e. equals zeros).
    - name : str or None, optional
        Residue name; default None (built from lhs and rhs)
    - reference: Number or numpy.ndarray or None
        Reference value to normalized the residue; default is unity
    """

    @staticmethod
    def residue_norm(
        left: Union[Number, Collection, numpy.ndarray],
        right: Union[Number, Collection, numpy.ndarray] = None,
    ) -> Union[Number, numpy.ndarray]:
        """Computes the order of magnitude of left- and right-hand sides to approximate the reference value.

        Parameters
        ----------
        - left : float or list of float or numpy.ndarray
            Left-hand side of the equation
        - right : float or list of float or numpy.ndarray or None (default)
            Right-hand side of the equation if not None

        Returns
        -------
        Number or numpy.ndarray
            An approximated reference value
        """
        a = numpy.abs(numpy.asarray(left, float))
        if right is not None:
            a += numpy.abs(right)
        return 10 ** numpy.floor(numpy.log10(numpy.where(a == 0, 1, a)))

    @staticmethod
    def evaluate_residue(
        lhs: Union[Number, Collection, numpy.ndarray],
        rhs: Union[Number, Collection, numpy.ndarray],
        reference: Union[Number, Collection, numpy.ndarray, str] = 1,
    ) -> Union[float, numpy.ndarray]:
        """Evaluate the normalized residue from left- and right-hand sides of an equation.

        The formula depends on the left- and right-hand side value of the equation:
            residues = (lhs - rhs) / reference

        Parameters
        ----------
        - lhs : Number or list of float or numpy.ndarray
            Left-hand side of the equation
        - rhs : Number or list of float or numpy.ndarray
            Right-hand side of the equation
        - reference : Number or list of float or numpy.ndarray or "norm"
            Reference value to normalize the equation with; default is unity

        Returns
        -------
        Number or numpy.ndarray
            Normalized residue
        """
        if isinstance(reference, str) and reference == "norm":  # type check avoids a warning for numpy arrays
            reference = Residue.residue_norm(lhs, rhs)
        return (numpy.asarray(lhs) - numpy.asarray(rhs)) / numpy.asarray(reference)

    def __init__(
        self,
        context: "System",
        equation: str,
        name: Optional[str] = None,
        reference: Union[Number, Collection, numpy.ndarray, str] = 1,
    ):
        """Initialization parameters:
        ----------
        - context : cosapp.systems.System
            CoSApp System to which this residue is linked
        - equation : str
            Equation of the kind 'hls == 'rhs', defining residue lhs - rhs.
        - name : str or None, optional
            Residue name; default None (built from equation)
        - reference : Number, numpy.ndarray or "norm", optional
            Reference value(s) used to normalize the equation; default is 1.
            If value is "norm", actual reference value is estimated from order of magnitude.
        """
        check_arg(equation, 'equation', str)
        check_arg(reference, 'reference', (Number, Collection, numpy.ndarray, str),
            lambda r: r == "norm" if isinstance(r, str) else numpy.all(numpy.asarray(r) > 0)
        )

        super().__init__(context, "temp")
        self.__lhs = None  # type: EvalString
        self.__rhs = None  # type: EvalString
        self.__equation = ""  # type: str
        self.__set_equation(equation)
        self._name = name or self.equation

        if isinstance(reference, str) and reference == "norm":  # type check avoids a warning for numpy arrays
            reference = Residue.residue_norm(self.__lhs.eval(), self.__rhs.eval())
        self.reference = reference
        self.update()

    @property
    def equation(self) -> str:
        """str: Equation defining the residue"""
        return self.__equation

    @staticmethod
    def split_equation(equation: str) -> Tuple[str, str]:
        """Parses and splits an equation of the kind 'lhs == rhs'.
        Returns string tuple (lhs, rhs).
        """
        eqsign = "=="
        check_arg(equation, 'equation', str,
            lambda s: s.count(eqsign) == 1 and s.replace(eqsign, '').count('=') == 0)
        lhs, rhs = equation.split(eqsign)
        lhs, rhs = lhs.strip(), rhs.strip()
        if len(lhs) == 0 or len(rhs) == 0:
            raise SyntaxError(f"Equation should be of the kind 'lhs == rhs'; got {equation!r}")
        return lhs, rhs

    def __set_equation(self, equation: str) -> None:
        """Checks that the two sides of an equation of the kind 'lhs == rhs' are compatible,
        and that residue (lhs - rhs) is not trivially constant.
        Left- and right-hand sides are finally stored as two evaluable expressions (EvalString).
        """
        lhs, rhs = Residue.split_equation(equation)
        context = self.context
        elhs = EvalString(lhs, context)
        erhs = EvalString(rhs, context)
        if elhs.constant and erhs.constant:
            raise RuntimeWarning(f"Equation {lhs} == {rhs} is trivially constant")
        try:
            elhs.eval() == erhs.eval()
        except:
            raise TypeError(f"Expressions {lhs!r} and {rhs!r} are not comparable")
        else:
            self.__lhs = elhs
            self.__rhs = erhs
            self.__equation = equation.strip()

    def __str__(self) -> str:
        name = self.__equation or self._name
        return f"{name} := {self._value}"

    def update(self) -> Union[Number, numpy.ndarray]:
        """Update the residue value

        Returns
        -------
        Number or numpy.ndarray
            The updated residues
        """
        self._value = Residue.evaluate_residue(
            self.__lhs.eval(), self.__rhs.eval(), self.reference
        )
        return self._value

    def copy(self) -> "Residue":
        """Copy the residue object.

        Returns
        -------
        Residue
            The duplicated residue
        """
        return Residue(
            self.context, self.__equation, self.name, reference=self.reference
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSONable representation of the equation.
        
        Returns
        -------
        Dict[str, Any]
            JSONable representation
        """
        ref = self.reference
        if isinstance(self.reference, numpy.ndarray):
            ref = self.reference.tolist()
        return {
            "context": self.context.contextual_name,
            "equation": self.__equation,
            "name": self.name,
            "reference": str(ref)
        }


class DeferredResidue:
    """Class representing a residue whose left-hand side evaluation is deferred.

    The right-hand side of the residue is a targetted quantity.
    Upon request, a Residue object is generated, with lhs = value(target).

    Parameters
    ----------
    - context : cosapp.systems.System
        CoSApp System to which residue is linked.
    - target : str
        Targetted quantity, and left-hand side of the equation.
    - reference: Number or numpy.ndarray or None
        Reference value to normalize the residue; default is unity.
    - variables: Set[str]
        Names of variables involved in the residue
    """
    def __init__(self, context: "System", target: str, reference=1.0):
        from cosapp.systems import System
        check_arg(context, "context", System)
        check_arg(target, "target", str)
        self.__context = context
        self.reference = reference
        self.target = target

    @property
    def context(self) -> "System":
        """System: evaluation context of residue"""
        return self.__context

    @property
    def target(self) -> str:
        """str: targetted quantity"""
        return str(self.__lhs)

    @target.setter
    def target(self, target: str) -> None:
        """Set targetted expression"""
        lhs = EvalString(target, self.context)
        if lhs.constant:
            raise ValueError(f"Targetted expression {lhs!r} appears to be constant")
        self.__lhs = lhs
        self.__vars = lhs.variables()

    @property
    def variables(self) -> Set[str]:
        """Set[str]: names of variables involved in residue"""
        return self.__vars

    def target_value(self) -> Any:
        """Evaluates and returns current value of target"""
        return self.__lhs.eval()

    def equation(self) -> str:
        """Returns target equation with updated lhs value"""
        return f"{self.target} == {self.target_value()!r}"

    def make_residue(self, reference=None) -> Residue:
        """Generates the residue corresponding to equation 'target == value(target)'"""
        if reference is None:
            reference = self.reference
        return Residue(self.context, self.equation(), reference=reference)

    def __repr__(self) -> str:
        clsname = self.__class__.__name__
        return f"{clsname}({self.context.name}, {self.target}, reference={self.reference})"

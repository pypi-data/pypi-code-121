"""Base class for recording data."""
import abc
import copy
import pandas
import warnings
from typing import Union, List, Optional, NamedTuple, Any

from cosapp.core.signal import Signal
from cosapp.core.eval_str import EvalString
from cosapp.utils.helpers import is_numerical, check_arg
from cosapp.utils.find_variables import SearchPattern, make_wishlist, find_variables


class SpecialColumns(NamedTuple):
    section: str
    status: str
    code: str
    reference: str


class BaseRecorder(abc.ABC):
    """Abstract base class for recorders.

    Matching pattern are case sensitive and support the following special patterns:

    ========  ================================
    Pattern   Meaning
    ========  ================================
    `*`       matches everything
    `?`       matches any single character
    `[seq]`   matches any character in seq
    `[!seq]`  matches any character not in seq
    ========  ================================

    Excluding pattern are shadowing includes one; e.g. if `includes='*port_in.*' and `excludes='*.Pt'`, for a port
    having variables named `Tt` and `Pt`, only `Tt` will be recorded.

    Parameters
    ----------
    includes : str or list of str, optional
        Variables matching these patterns will be included; default `'*'` (i.e. all variables).
    excludes : str or list of str or None, optional
        Variables matching these patterns will be excluded; default `None` (i.e. nothing is excluded).
    numerical_only : bool, optional
        Keep only numerical variables (i.e. number or numerical vector); default False.
    section : str, optional
        Current section name; default `''`.
    precision : int, optional
        Precision digits when writing floating point number; default 9 (i.e. 10 figures will be written).
    hold : bool, optional
        Append the new data or not; default `False`.
    raw_output : bool, optional
        Raw output; default `False`.

    Signals
    -------
    state_recorded : Signal(time_ref: Union[float, str], status: str, error_code: str)
        Signal emitted after `record_state` execution
    cleared : Signal()
        Signal emitted after `clear` execution
    """

    SPECIALS = SpecialColumns(
        section="Section", status="Status", code="Error code", reference="Reference"
    )

    paused = False  # type: bool

    def __init__(self,
        includes: SearchPattern = "*",
        excludes: Optional[SearchPattern] = None,
        # metadata: Optional[SearchPattern] = None,  # TODO?
        numerical_only = False,
        section = "",
        precision = 9,
        hold = False,
        raw_output = False,
    ):
        check_arg(raw_output, 'raw_output', bool)
        check_arg(numerical_only, 'numerical_only', bool)

        self.__includes = make_wishlist(includes, "includes")  # type: List[str]
        self.__excludes = make_wishlist(excludes, "excludes")  # type: List[str]
        self._numerical_only = numerical_only  # type: bool
        # self.__metadata = metadata  # type: List[str]
        self.__section = ""  # type: str
        self.section = section
        self.__hold = False  # type: bool
        self.hold = hold
        self.__precision = 9  # type: int
        self.precision = precision
        self._raw_output = raw_output  # type: bool
        self.__variables = None  # type: Optional[List[str]]
        self.__expressions = None  # type: Optional[List[str]]
        self._watch_object = None  # type: Optional[cosapp.core.module.Module]
        self._owner = None  # type: Optional[str]

        # Signal
        self.state_recorded = Signal(
            args=["time_ref", "status", "error_code"],
            name="cosapp.recorders.recorder.BaseRecorder.state_recorded",
        )
        self.cleared = Signal(name="cosapp.recorders.recorder.BaseRecorder.cleared")

    @classmethod
    def extend(cls, recorder, includes: SearchPattern=[], excludes: SearchPattern=[]) -> "BaseRecorder":
        """
        Factory returning a new recorder, with similar attributes as
        `recorder`, but extended `includes` and `excludes` fields.

        Parameters
        ----------
        includes : str, list of str, or None, optional
            Variables patterns extending `recorder` inclusion patterns; default `[]` (i.e. no change).
        excludes : str, list of str, or None, optional
            Variables patterns extending `recorder` exclusion patterns; default `[]` (i.e. no change).
        """
        new = cls(
            recorder.includes + make_wishlist(includes, "includes"),
            recorder.excludes + make_wishlist(excludes, "excludes"),
            recorder._numerical_only,
            recorder.section,
            recorder.precision,
            recorder.hold,
            recorder._raw_output,
        )
        new.watched_object = recorder.watched_object
        return new

    @property
    def watched_object(self) -> "Optional[cosapp.core.module.Module]":
        """Module : The object from which data are read."""
        return self._watch_object

    @watched_object.setter
    def watched_object(self, module: "cosapp.core.module.Module"):
        from cosapp.core.module import Module

        if not (module is None or isinstance(module, Module)):
            typename = type(module).__qualname__
            raise TypeError(
                f"Recorder must be attached to a System or a Driver; got {typename}."
            )
        is_new = module is not self._watch_object
        
        if self._watch_object is None or is_new:
            self.__variables = None
            self.__expressions = None
            self._watch_object = module

    @property
    @abc.abstractmethod
    def _raw_data(self) -> List[List[Any]]:
        """Returns a raw/unformated version of records.

        Returns
        -------
        List[List[Any]]
            Records of `watched_object` for variables given by method `field_names()`
        """
        pass

    @property
    def data(self) -> pandas.DataFrame:
        """
        pandas.DataFrame: DataFrame containing the results.
        Deprecated property; use `export_data()` instead.
        """
        warnings.warn(
            "Deprecated property; use export_data() instead",
            DeprecationWarning
        )
        return self.export_data()

    @abc.abstractmethod
    def export_data(self) -> pandas.DataFrame:
        """Export recorded results into a pandas.DataFrame object."""
        pass

    @property
    def includes(self) -> List[str]:
        """str or list of str : Variables matching these patterns will be included."""
        return self.__includes

    @property
    def excludes(self) -> List[str]:
        """str or list of str: Variables matching these patterns will be excluded."""
        return self.__excludes

    @property
    def section(self) -> str:
        """str : Current section name."""
        return self.__section

    @section.setter
    def section(self, section: str):
        check_arg(section, 'section', str)
        self.__section = section

    @property
    def hold(self) -> bool:
        """bool : Append the new data or not."""
        return self.__hold

    @hold.setter
    def hold(self, value: bool):
        check_arg(value, 'hold', bool)
        self.__hold = value

    @property
    def precision(self) -> int:
        """int : Precision digits when writing floating point number."""
        return self.__precision

    @precision.setter
    def precision(self, value: int):
        check_arg(value, 'precision', int, lambda n: n > 0)
        self.__precision = value

    def field_names(self) -> List[str]:
        """Returns list of requested variables and expressions.

        Returns
        -------
        List[str]
            Variable names matching the includes/excludes patterns of the user in the watched object.

        .. note::
            Inward and outward variables will appear without the prefix `inwards.` or `outwards.`.
        """
        if self.__variables is None and self.watched_object is not None:
            self.__update_varlist()
        return self.__variables or list()

    def __contains__(self, field: str) -> bool:
        return field in self.field_names()

    def __update_varlist(self) -> None:
        """Update the list of fields to be recorded"""
        includes = []
        evaluables = []
        context = self.watched_object
        for expression in set(self.__includes):
            try:
                EvalString(expression, context)
            except:
                includes.append(expression)
            else:
                if expression in context:
                    # Keep expression in search list,
                    # in case it matches an exclusion pattern
                    includes.append(expression)
                else:
                    evaluables.append(expression)
        
        if self._numerical_only:
            filter = lambda x: is_numerical(x)
        else:
            filter = lambda x: True
        
        variables = find_variables(
            context,
            includes,
            self.__excludes,
            advanced_filter=filter,
        )
        variables.extend(evaluables)
        self.__variables = variables = sorted(variables)
        self.__expressions = EvalString(", ".join(variables).join("[]"), context)

    def _get_units(self, varnames: Optional[List[str]] = None) -> List[str]:
        """Generate the list of units associated with the requested variables.

        Parameters
        ----------
        vars : list of str, optional
            List of the variables to get the units; if not provided, takes field_names

        Returns
        -------
        List[str]
            Variable units for the variables matching the includes/excludes patterns of the user.
        """
        if varnames is None:
            varnames = self.field_names()

        units = list()
        if self.watched_object is not None:
            name2variable = self.watched_object.name2variable
            for name in varnames:
                try:
                    ref = name2variable[name]
                    details = ref.mapping.get_details(ref.key)
                    unit = details.unit
                except:
                    unit = None
                units.append(unit or "-")

        return units

    def start(self):
        """Initialize recording support."""
        if self.watched_object is None:
            raise RuntimeError("A recorder should be watching a Driver.")

    def record_state(self, time_ref: Union[float, str], status="", error_code="0") -> None:
        """Record the watched object at the provided status.

        Parameters
        ----------
        time_ref : float or str
            Current simulation time (float) or point reference (str)
        status : str, optional
            Status of the simulation; default `''`.
        error_code : str, optional
            Error code; default `'0'`.
        """
        if self.paused:
            return

        line = [self.section, status, error_code, str(time_ref)] + self.formatted_data()
        self._record(line)
        self.state_recorded.emit(time_ref=time_ref, status=status, error_code=error_code)

    @abc.abstractmethod
    def formatted_data(self) -> List[Any]:
        """Returns collected data from watched object as a formatted list."""
        pass

    def collected_data(self) -> List[Any]:
        """Collects and returns recorded data from watched object as a list."""
        if self.__expressions is None:
            self.__update_varlist()
        return self.__expressions.eval()

    @abc.abstractmethod
    def _record(self, line: List[Any]) -> None:
        """
        Internally record data collected into list `line`.
        Required by `record_state` method.
        """
        pass

    def clear(self):
        """Clear all previously stored data."""
        self.cleared.emit()

    @abc.abstractmethod
    def exit(self):
        """Close recording session."""
        pass

    def restore(self, index: int):
        """Restore the watch object state from the recorded data.

        Parameters
        ----------
        index : int
            Index of the record as iloc in the Pandas DataFrame
        """
        check_arg(index, 'index', int)

        data = self._raw_data
        if index < 0 or index > len(data) - 1:
            raise IndexError(f"Index {index} does not exist in this Recorder")

        inputs = find_variables(
            self._watch_object, includes=["*"], excludes=[], outputs=False
        )

        recording = data[index][4:]

        for idx, var in [
            (idx, var)
            for idx, var in enumerate(self.field_names())
            if var in inputs
        ]:
            try:
                self._watch_object[var] = copy.deepcopy(recording[idx])
            except KeyError:
                pass

    def check(self) -> None:
        try:
            self.formatted_data()
        except Exception as ex:
            warnings.warn(
                f"Captured exception {ex!r} while trying to collect data in {self.watched_object}"
                "; recorder may fail.",
                RuntimeWarning
            )

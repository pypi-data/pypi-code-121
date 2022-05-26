import numpy
import pandas
from typing import List, Set, Union, Optional

from cosapp.drivers.abstractsetofcases import AbstractSetOfCases
from cosapp.drivers.optionaldriver import OptionalDriver
from cosapp.recorders.dataframe_recorder import DataFrameRecorder
from cosapp.utils.helpers import check_arg, is_number
from cosapp.utils.find_variables import find_variables


# TODO This does not support multipoints cases
class Influence(AbstractSetOfCases):
    """
    This driver evaluate the influence between inputs and outputs (floats only)
    In input :

    - the inwards (including in the ports)

    In output :

    - the inwards (including in the ports)
    - the connected ports
    - the outwards

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = (
        'input_vars', 'response_vars', 'influence_matrix', 'delta', 
        'influence_min_threshold', 'reference', 'found_input_vars', 'found_response_vars',
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
        name: str, optional
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belong; defaults to `None`.
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)

        self.input_vars = ["*"]  # type: List[str]
            # desc="Variable names varying between cases"        
        self.response_vars = ["*"]  # type: List[str]
            # desc="Variable names to monitor between cases"
        self.influence_matrix = None  # type: pandas.DataFrame
            # desc="Influence matrix d/d output(d/d input)"
        self.delta = 1e-3  # type: float
            # desc="Relative influence to apply for influence matrix computation"
        self.influence_min_threshold = 1e-5  # type: float
            # desc="Minimum value of influence to consider"

        self.reference = pandas.DataFrame()  # type: pandas.DataFrame
        self.found_input_vars = list()  # type: List[str]
        self.found_response_vars = list()  # type: List[str]

    def reset_input_vars(self):
        """Reset input_vars variable to its default value ['*']
        """
        self.input_vars = ["*"]

    def reset_response_vars(self):
        """Reset response_vars variable to its default value ['*']
        """
        self.response_vars = ["*"]

    def add_input_vars(self, names: Union[str, Set[str], List[str]]):
        """Add variable to be influenced.

        Parameters
        ----------
        names : Union[str, Set[str], List[str]]
            List of variables to be influenced
        """
        self._add_vars(names, is_input=True)

    def add_response_vars(self, names: Union[str, Set[str], List[str]]):
        """Add variable to be monitored.

        Parameters
        ----------
        names : Union[str, Set[str], List[str]]
            List of variables to be monitored
        """
        self._add_vars(names, is_input=False)

    def _add_vars(self, names: Union[str, Set[str], List[str]], is_input: bool = True):
        """Add variable to be influenced or monitored.

        Parameters
        ----------
        names : Union[str, Set[str], List[str]]
            List of variables to be influenced or monitored
        is_input : bool
            Defines if the variables is an input or not
        """
        check_arg(names, 'names', (str, set, list))

        if is_input and self.input_vars and self.input_vars[0] == "*":
            self.input_vars.pop(0)
        if not is_input and self.response_vars and self.response_vars[0] == "*":
            self.response_vars.pop(0)

        if isinstance(names, str):
            if is_input:
                self.input_vars.append(names)
            self.response_vars.append(names)
        else:
            for name in names:                
                if isinstance(name, str):
                    if is_input:
                        self.input_vars.append(name)
                    self.response_vars.append(name)
                else:
                    raise TypeError(
                        f"string expected; got {type(name).__qualname__}."
                    )

    def _build_cases(self) -> None:
        """Build the list of cases to run during execution
        """
        self.add_recorder(
            DataFrameRecorder(
                includes=self.input_vars + self.response_vars,
                raw_output=True,
                numerical_only=True,
            )
        )

        self.found_input_vars = find_variables(
            self.owner,
            includes=self.input_vars,
            excludes=[],
            advanced_filter=lambda x: is_number(x),
            outputs=False,
        )
        self.found_response_vars = find_variables(
            self.owner,
            includes=self.response_vars,
            excludes=[],
            advanced_filter=lambda x: is_number(x),
            inputs=False,
        )

        # TODO('Filter on variable types to avoid bugs with strings etc')
        # TODO('Support sequences')
        def f(ref, idx) -> numpy.array:
            case = ref.copy()
            case[idx] *= 1 + self.delta
            return case

        case_ref = [self.owner[var] for var in self.found_input_vars]
        self.cases = [case_ref]
        self.cases.extend(
            [f(case_ref, index) for index in range(len(self.found_input_vars))]
        )

    def _precase(self, case_idx, case):
        """Hook to be called before running each case."""
        # TODO Use MonteCarlo machinery
        for variable, value in zip(self.found_input_vars, case):
            self.owner[variable] = value

    def _precompute(self):
        """Set execution order, build cases and run reference case."""
        super()._precompute()
        self._run_reference()
        OptionalDriver.set_inhibited(True)

    def _run_reference(self):
        """Run the reference case (i.e. with no influence), store the result and clean the recorder."""
        case = self.cases[0]
        if case:
            self._precase(0, case)
            self.run_children()
            self._postcase(0, case)
        self.cases.pop(0)

        data = self.recorder.export_data()
        self.reference = data.iloc[
            :, len(DataFrameRecorder.SPECIALS) :
        ]  # Skip the information
        self.recorder.start()

    def _postcompute(self):
        """Calculate the influence matrix"""
        OptionalDriver.set_inhibited(False)
        super()._postcompute()

        data = self.recorder.export_data()
        results = data.iloc[
            :, len(DataFrameRecorder.SPECIALS) :
        ]  # Skip the information

        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            deltas = pandas.DataFrame(
                results.values / self.reference.values - 1.0,
                columns = self.reference.columns,
            )

        # TODO Improve coverage of no influence cases and absolute vs relative influence or mix of influences
        deltas[numpy.abs(deltas) == numpy.inf] = 0
        deltas[numpy.abs(results.values) < 1e-4] = 0

        inputs = deltas[self.found_input_vars]
        inputs_diag = inputs.values.diagonal().reshape((-1, 1))
        outputs = deltas[self.found_response_vars]

        inputs_diag = numpy.where(inputs_diag == 0., 1e-15, inputs_diag)

        # find inputs modified during the children drivers exec (connected port, variable iterated, etc.)
        coeff = numpy.where(abs(inputs_diag - self.delta) < 1e-10, 1. / inputs_diag, 0.)

        self.influence_matrix = pandas.DataFrame(
            outputs.values * coeff,
            columns = outputs.columns,
            index = inputs.columns,
        ).fillna(0)

    def show_influence_matrix(self,
        cleaned: bool = True,
        styling: bool = False,
        transpose: bool = False,
        sort_by: str = None,
    ):
        """Return the influence matrix with cleaning and styling options.

        Parameters
        ----------
        cleaned : bool, optional
            Defines if the returned influence matrix will be cleaned or not
        styling : bool, optional
            Defines if the returned influence matrix will be styled or not
        transpose : bool, optional
            Defines if the matrix will transposed or not before return
        sort_by: str, optional
            If given, will sort
        """
        matrix = self.influence_matrix

        if cleaned:
            matrix = matrix.where((abs(matrix) > self.influence_min_threshold), 0.0)
            matrix = matrix[(matrix.T != 0).any()]
            matrix = matrix.loc[:, (matrix != 0).any()]

        if sort_by:
            matrix = matrix.reindex(
                matrix[sort_by].abs().sort_values(ascending=False).index
            )

        if transpose:
            matrix = matrix.T

        if styling:
            matrix = matrix.style.bar(align="mid", color=["#d65f5f", "#5fba7d"])

        return matrix

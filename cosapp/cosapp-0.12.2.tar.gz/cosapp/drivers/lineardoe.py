import numpy
import itertools
from collections import OrderedDict
from typing import Any, Dict, Optional, Union

from cosapp.drivers.abstractsetofcases import AbstractSetOfCases
from cosapp.utils.helpers import check_arg


# TODO
# [ ] Quid for vector variables
class LinearDoE(AbstractSetOfCases):
    """
    This driver builds a set of linear Doe

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = ('input_vars',)

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
        self.input_vars = OrderedDict()

    def add_input_var(self,
        definition: Union[str, Dict[str, Any]],
        lower: Optional[float] = None,
        upper: Optional[float] = None,
        count: int = 2,
    ):
        check_arg(definition, 'definition', (str, dict))

        def add_unique_input_var(name: str, lower: float, upper: float, count: int = 2):
            self.check_owner_attr(name)
            self.input_vars[name] = {"lower": lower, "upper": upper, "count": count}

        if isinstance(definition, dict):
            for key, value in definition.items():
                if isinstance(value, dict):
                    try:
                        add_unique_input_var(key, **value)
                    except TypeError:
                        raise TypeError(
                            f"'lower' and 'upper' keys expected; got {value.keys()}."
                        )
                else:
                    raise TypeError(
                        f"dictionary expected; got {type(value).__name__}."
                    )
        else:
            add_unique_input_var(definition, lower=lower, upper=upper, count=count)

    def _build_cases(self):
        cases = list()
        for range_ in self.input_vars.values():
            cases.append(numpy.linspace(range_["lower"], range_["upper"], range_["count"]))
        self.cases = list(itertools.product(*cases))

    def _precase(self, case_idx, case):
        """Hook to be called before running each case."""
        super()._precase(case_idx, case)
        for variable, value in zip(self.input_vars, case):
            self.owner[variable] = value

"""Recorder in `pandas.DataFrame`."""
import copy
import pandas
from typing import Any, List, Optional

from cosapp.recorders.recorder import BaseRecorder, SearchPattern


class DataFrameRecorder(BaseRecorder):
    """Record data into a pandas.DataFrame.

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

    ..note::
        Do not mention `inwards` or `outwards` in `includes` or `excludes` list. Otherwise you may not record the wanted
        variables.
    """
    def __init__(
        self,
        includes: SearchPattern = "*",
        excludes: Optional[SearchPattern] = None,
        # metadata: Optional[SearchPattern] = None,
        numerical_only = False,
        section = "",
        precision = 9,
        hold = False,
        raw_output = True,
    ):
        super().__init__(
            includes, excludes, numerical_only, section, precision, hold, raw_output
        )
        # Temporary storage
        self.__buffer = list()  # type: List[List[Any]]

    def export_data(self) -> pandas.DataFrame:
        """Export recorded results into a pandas.DataFrame object."""
        # According to DataFrame documentation, it is more efficient to store in a list than create the DataFrame
        headers = [
            self.SPECIALS.section,
            self.SPECIALS.status,
            self.SPECIALS.code,
            self.SPECIALS.reference,
        ]
        varlist = self.field_names()
        if self._raw_output:
            headers.extend(varlist)
        else:
            # Add units in column headers
            headers.extend(
                map(
                    lambda v: f"{v[0]} [{v[1]}]",
                    zip(varlist, self._get_units(varlist)),
                )
            )
        return pandas.DataFrame(self.__buffer, columns=headers)

    @property
    def _raw_data(self) -> List[List[Any]]:
        """Return a raw/unformatted version of records

        Returns
        -------
        List[List[Any]]
            Records of `watched_object` for variables given by method `field_names()`
        """
        return self.__buffer

    def start(self):
        """Initialize recording support."""
        super().start()
        if not self.hold:
            self.__buffer.clear()

    def formatted_data(self) -> List[Any]:
        """Collect recorded data from watched object into a list."""
        line = []
        names = self.field_names()
        values = self.collected_data()
        for name, value in zip(names, values):
            try:
                line.append(copy.deepcopy(value))
            except copy.Error:
                context = self.watched_object
                if name in context:
                    varname = f"{context.name}.{name}"
                else:
                    varname = f"{context.name}[{name}]"
                raise TypeError(
                    f"Cannot record {varname}: DataFrameRecorder objects can only capture deep-copyable variables"
                )
        return line

    def _record(self, line: List[Any]) -> None:
        self.__buffer.append(line)

    def exit(self):
        """Close recording session."""
        pass

    def clear(self):
        """Clear all previously stored data."""
        self.__buffer.clear()
        super().clear()

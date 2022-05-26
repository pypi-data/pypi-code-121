"""Recorder to Delimited Separated Value format file."""
import os
import numpy
import pandas
from typing import Any, List, Optional
from collections.abc import Collection

from cosapp.recorders.recorder import BaseRecorder, SearchPattern
from cosapp.utils.helpers import is_numerical, check_arg


class DSVRecorder(BaseRecorder):
    """Record data into Delimiter Separated Value file.

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
    filepath : str
        Filepath to save data into.
    delimiter : `','`, `';'` or `'\t'`, optional
        Delimiter of data in the file; default `','`.
    use_buffer : bool, optional
        Should the data written after the simulation (`False`) or every time they are available (`True`);
        default `False`.
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
        filepath: str,
        includes: SearchPattern = "*",
        excludes: Optional[SearchPattern] = None,
        numerical_only = False,
        section = "",
        precision = 9,
        hold = False,
        delimiter = ",",
        raw_output = False,
        use_buffer = False,
    ):
        check_arg(filepath, "filepath", str)
        check_arg(delimiter, "delimiter", str)
        check_arg(use_buffer, "use_buffer", bool)

        supported_delimiters = (",", ";", "\t")
        if delimiter not in supported_delimiters:
            raise ValueError(
                f"Supported delimiters are {supported_delimiters}; got {delimiter!r}"
            )

        super().__init__(
            includes, excludes, numerical_only, section, precision, hold, raw_output
        )
        self.__filepath = filepath  # type: str
        self.__delimiter = delimiter  # type: str
        self.__buffer = [] if use_buffer else None  # type: List[List[Any]]

    @property
    def filepath(self) -> str:
        """str: path of the DSV file"""
        return self.__filepath

    @property
    def delimiter(self) -> str:
        """str: column delimiter used in DSV file"""
        return self.__delimiter

    def export_data(self) -> pandas.DataFrame:
        """Export recorded results into a pandas.DataFrame object."""
        if not os.path.exists(self.__filepath):
            return pandas.DataFrame()
        elif self.__buffer is not None:
            headers = self.get_headers()
            return pandas.DataFrame(self.__buffer, columns=headers)
        else:
            return pandas.read_csv(self.__filepath, delimiter=self.__delimiter, header=0)

    @property
    def _raw_data(self) -> List[List[Any]]:
        """Return a raw/unformatted version of records.

        Returns
        -------
        List[List[Any]]
            Records of `watched_object` for variables given by method `field_names()`
        """
        if not os.path.exists(self.__filepath):
            return list()

        if self.__buffer is not None:
            return self.__buffer

        with open(self.__filepath, "r") as fd:
            # The header line is skipped
            content = map(lambda line: line.split(self.__delimiter), fd.readlines()[1:])
        return content

    def start(self):
        """Initialize recording support."""
        super().start()
        if not self.hold:
            # Run system to ensure data are up-to-date
            # TODO could we use clean/dirty here?
            self.watched_object.run_once()
            if self.__buffer is not None:
                self.__buffer.clear()
            # Write header
            headers = self.get_headers()
            with open(self.__filepath, "w") as fd:
                fd.write(self.__delimiter.join(headers) + "\n")

    def get_headers(self) -> List[str]:
        """Returns the list of headers of DSV file."""
        headers = list(self.SPECIALS)

        def add_header(base, unit):
            if unit and not self._raw_output:
                headers.append(f"{base} [{unit}]")
            else:
                headers.append(base)

        names = self.field_names()
        units = [None] * len(names) if self._raw_output else self._get_units(names)
        system = self.watched_object

        for name, unit in zip(names, units):
            value = system[name]
            if isinstance(value, numpy.ndarray) and value.ndim > 0:
                for i in range(value.size):
                    entry = f"{name}[{i}]"
                    add_header(entry, unit)
            elif isinstance(value, Collection) and not isinstance(value, str):
                for i in range(len(value)):
                    entry = f"{name}[{i}]"
                    add_header(entry, unit)
            else:
                add_header(name, unit)
        
        return headers

    def formatted_data(self) -> List[Any]:
        """Format collected data from watched object into a list."""

        precision = self.precision
        def fmt(value, check=True):
            if check and not is_numerical(value):
                return str(value)
            return "{0:.{1}e}".format(value, precision)

        line = []
        for value in self.collected_data():
            if isinstance(value, numpy.ndarray):
                if numpy.issubdtype(value.dtype, numpy.number):
                    line.extend(fmt(v, check=False) for v in value.flat)
                else:
                    line.extend(str(v) for v in value.flat)
            elif isinstance(value, Collection) and not isinstance(value, str):
                line.extend(fmt(v) for v in value)
            else:
                line.append(fmt(value))

        return line

    def _record(self, line: List[Any]) -> None:
        if self.__buffer is None:
            with open(self.__filepath, "a") as fd:
                fd.write(self.__delimiter.join(line) + "\n")
        else:
            self.__buffer.append(line)

    def clear(self):
        """Clear all previously stored data."""
        if self.__buffer is not None:
            self.__buffer.clear()
        super().clear()

    def exit(self):
        """Close recording session."""
        if self.__buffer is not None:
            delimiter = self.__delimiter
            with open(self.__filepath, "a") as fd:
                for line in self.__buffer:
                    fd.write(delimiter.join(line) + "\n")

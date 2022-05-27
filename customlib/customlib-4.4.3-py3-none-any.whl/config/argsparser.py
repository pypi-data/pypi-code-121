# -*- coding: UTF-8 -*-

from typing import Sequence, Generator

from ..exceptions import BadParameterError


class ArgsParser(object):
    """`cmd-line` args parser."""

    def __init__(self):
        self.parameters = dict()

    def parse(self, args: Sequence[str]) -> dict:
        args: Generator = (arg for arg in args)
        for arg in args:
            if arg.startswith("--") is True:
                stripped = arg.strip("-")
                try:
                    section, option = stripped.split("-")
                except ValueError:
                    raise BadParameterError(f"Inconsistency in cmd-line parameters '{arg}'!")
                else:
                    try:
                        value = next(args)
                    except StopIteration:
                        raise BadParameterError(f"Missing value for parameter '{arg}'")
                    else:
                        if value.startswith("--") is False:
                            self._update(section, option, value)
                        else:
                            raise BadParameterError(f"Incorrect value '{value}' for parameter '{arg}'!")
            else:
                raise BadParameterError(f"Inconsistency in cmd-line parameters '{arg}'!")
        return self.parameters

    def _update(self, section: str, option: str, value: str):
        section = section.upper()
        if section not in self.parameters:
            self.parameters.update({section: {option: value}})
        else:
            section = self.parameters.get(section)
            section.update({option: value})

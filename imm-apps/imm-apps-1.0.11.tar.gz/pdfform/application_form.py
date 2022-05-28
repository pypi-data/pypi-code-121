from datetime import datetime
import time

from .form_controls import (
    Control,
    TextField,
    RadioButton,
    CheckBox,
    DropdownList,
    DateField,
    Skip,
    Pause,
    OutputInfo,
    Button,
)


class ApplicationForm(object):
    """Application PDF form"""

    def __init__(self, applicant, operations=None):
        self.applicant = applicant
        if operations is not None:
            self._operations = list(operations)
        else:
            self._operations = []

    def add_step(self, operation: Control):
        self._operations.append(operation)

    def add_text(self, data, pause=0):
        control = TextField(data, pause=pause)
        self.add_step(control)

    def add_radio(self, data):
        control = RadioButton(data)
        self.add_step(control)

    def add_checkbox(self, data):
        control = CheckBox(data)
        self.add_step(control)

    def add_dropdown(self, data, options, like: bool = False):
        control = DropdownList(data, options, like)
        self.add_step(control)

    def add_date(self, date, noday: bool = False, pause=0.2):
        self.add_step(DateField(date, noday, pause=pause))

    def add_skip(self, num):
        """Add {num} skips"""
        for _ in range(num):
            self.add_step(Skip())

    def add_pause(self, seconds):
        """Pause {seconds} seconds"""
        self.add_step(Pause(seconds))

    def add_button(self):
        """Click button"""
        self.add_step(Button())

    def add_info(self, info: str):
        """Output info for debugging script"""
        self.add_step(OutputInfo(info))

    def fill_form(self, start: int = 0, verbose: bool = False):
        """Perform the fill pdf form action"""
        step = 0
        for operation in self._operations[start:]:
            # if not isinstance(operation, OutputInfo):
            if verbose:
                operation.verbose = True
                print(step, end="\t")
                step += 1
            operation.fill()

import time
from abc import ABC, abstractmethod
from typing import Tuple
from datetime import date, timedelta
from utils.utils import best_match
from pywinauto.keyboard import send_keys


class Control(ABC):
    """Pdf form input control base class"""

    verbose: bool = False

    @abstractmethod
    def fill(self):
        """Fill this control"""


class Skip(Control):
    """Skip disabled control"""

    def fill(self):
        if self.verbose:
            print("Skip to next")
        send_keys("{TAB}")


class Button(Control):
    def fill(self):
        if self.verbose:
            print("Click button")
        send_keys("{ENTER}")


class Pause(Control):
    """Pause for a moment"""

    def __init__(self, seconds):
        self.seconds = seconds

    def fill(self):
        if self.verbose:
            print(f"Pause {self.seconds} seconds")
        time.sleep(self.seconds)


class TextField(Control):
    """Text field"""

    def __init__(self, data, pause=0):
        """data: text to fill"""
        self.data = data
        self.pause = pause

    def fill(self):
        if self.verbose:
            print(f"Fill text field with {self.data}")
        self.data = self.data or ""
        send_keys(self.data.replace(" ", "{SPACE}"), pause=self.pause)
        send_keys("{TAB}")


class RadioButton(Control):
    """Radio button"""

    def __init__(self, data):
        """data: False for No, True for yes"""
        self.data = data

    def fill(self):
        if self.data:
            key = "{VK_RIGHT}"
        else:
            key = "{VK_SPACE}"
        if self.verbose:
            print(f"Fill radio button with {self.data}, press {key} key")
        send_keys(key)
        send_keys("{TAB}")


class CheckBox(Control):
    """Check box"""

    def __init__(self, data):
        self.data = data

    def fill(self):
        if self.verbose:
            print(f"Fill check box with {self.data}")
        if self.data:
            send_keys("{VK_SPACE}")
            send_keys("{TAB}")
        else:
            send_keys("{TAB}")


class OutputInfo(Control):
    """Output log info"""

    def __init__(self, info):
        self.info = info

    def fill(self):
        if self.verbose:
            print(f"------- {self.info} -------")


class DropdownList(Control):
    """Dropdown list"""

    def __init__(self, data, options, like: bool = False):
        self.data = data
        self.options = options
        self.like = like

    def key_presses(self) -> Tuple[str, int]:
        s_char = self.data[0].lower()
        count = 0
        matched_one = best_match(self.data, self.options)
        for elem in self.options:
            if elem[0].lower() == s_char:
                count += 1
                if elem.lower() == matched_one.lower():
                    break
        return (s_char, count)

    def fill(self):
        key, num = self.key_presses()
        if self.verbose:
            print(f"Select dropdown list with {self.data}, press {key} {num} time(s)")
        for _ in range(num):
            send_keys(key)
        send_keys("{TAB}")


class DateField(Control):
    """Date field"""

    def __init__(self, the_date, noday: bool = False, pause=0.2):
        self.date = the_date or date.today() + timedelta(days=1)
        self.noday = noday
        self.pause = pause

    def fill(self):

        if self.noday:
            self.date = (
                self.date.strftime("%Y-%m") if type(self.date) == date else self.date
            )
            year, month = self.date.split("-")
            if self.verbose:
                print(f"Fill date {year}-{month}")
            send_keys(year, pause=self.pause)
            send_keys(month, pause=self.pause)
        else:
            self.date = (
                self.date.strftime("%Y-%m-%d") if type(self.date) == date else self.date
            )
            year, month, day = self.date.split("-")
            if self.verbose:
                print(f"Fill date {year}-{month}-{day}")
            send_keys(year, pause=self.pause)
            send_keys(month, pause=self.pause)
            send_keys(day, pause=self.pause)
        send_keys("{TAB}")

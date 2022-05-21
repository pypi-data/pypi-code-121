from enum import Enum
from typing import Any


class FormControlType(Enum):
    FormControlTypeInput = "input"
    FormControlTypeSelect = "select"
    FormControlTypeRadio = "radio"
    FormControlTypeTextArea = "textarea"
    FormControlTypeJson = "json"

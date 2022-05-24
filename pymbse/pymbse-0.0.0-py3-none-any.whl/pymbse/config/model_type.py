from enum import Enum


class ModelType(str, Enum):
    NOTEBOOK = "NOTEBOOK"
    SCRIPT = "SCRIPT"
    NOTEBOOK_SCRIPT = "NOTEBOOK_SCRIPT"

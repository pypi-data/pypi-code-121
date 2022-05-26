from enum import Enum


class ExperimentType(str, Enum):
    AUTOML = "automl"
    MLLAB = "mllab"
    PREDEFINEDAI = "predefinedai"

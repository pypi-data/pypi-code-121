from enum import Enum


class Frameworks(str,Enum):
    SKLEARN = "SKLEARN"
    KERAS = "KERAS"
    H2O = "H2O"
    LIGHTGBM = "LIGHTGBM"
    XGBOOST = "XGBOOST"
    CATBOOST = "CATBOOST"
    PYTORCH = "PYTORCH"

    @staticmethod
    def has_value(item):
        return item in [v.value for v in Frameworks.__members__.values()]

def is_framework_supported(framework):
    if not Frameworks.has_value(framework):
        return False
    return True

from .SpatialMean import SpatialMean
from .EVI import EVI
from .EVI import OperatorProcessingException

def get_operator(operator_name, operator_args):

    operator_class = globals()[operator_name]
    if operator_args:
        return operator_class(*eval(operator_args))
    else:
        return operator_class()
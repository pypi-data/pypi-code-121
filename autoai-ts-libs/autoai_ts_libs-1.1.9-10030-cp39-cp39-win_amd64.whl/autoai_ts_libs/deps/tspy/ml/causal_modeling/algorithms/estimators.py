import abc
import sys
from sklearn.base import BaseEstimator

if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})


class CausalityEstimator(BaseEstimator):
    """ 
    """
    def __init__(self, *argv, **kwargs):
        """
        """

    @abc.abstractmethod
    def fit(self, *argv, **kwargs):
        """ 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_weighted_causes(self, *argv, **kwargs):
        """ 
        """
        raise NotImplementedError


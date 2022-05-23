"""Test algo functionality."""
import inspect
from .errors import TestError
from .tabular import test_tabular_algo
from ..base.algo import Algo
from ..base.tabular import TabularClassificationAutoML, TabularRegressionAutoML

def test_algo(algo, output_dir, timeout = 100, nan_fraction = 0.1):
    """
    Function for testing algo functionality.

    Args:
        algo: Algo class.
        output_dir: local directory for saving model.
        timeout: search time in seconds.
        nan_fraction: probability of null values in data.

    Returns:
        None.
    """
    if issubclass(algo, TabularClassificationAutoML) or issubclass(algo, TabularRegressionAutoML):
        return test_tabular_algo(algo, output_dir, timeout, nan_fraction)
    else:
        raise TestError('invalid algo class')

def test_package(package, output_dir, **kwargs):
    """
    Function for testing algos in package.

    Args:
        package: module.
        output_dir: local directory for saving model.
        kwargs: keyword args passed to test_algo

    Returns:
        None.
    """
    for field in dir(package):
        attr = getattr(package, field)
        if inspect.isclass(attr) and issubclass(attr, Algo):
            test_algo(attr, output_dir, **kwargs)

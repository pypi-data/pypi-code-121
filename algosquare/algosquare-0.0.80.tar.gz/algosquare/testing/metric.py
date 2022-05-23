"""Test of metric functionality."""
import numpy as np
import pandas as pd

from .targets import create_classification_target, create_regression_target
from .errors import TestError
from ..base.metric import Metric
from ..base.types import Metatype, TARGET_METATYPES

def test_metric(metric, n_outputs = 3):
    """
    Function for testing metric functionality.

    Args:
        metric: ClassificationMetric or RegressionMetric.
        n_outputs: dimensionality of targets

    Returns:
        None.
    """
    test_metatypes = [metatype for metatype in TARGET_METATYPES if metric.supports_metatype(metatype)]
    if not test_metatypes:
        raise ValueError('no supported metatypes')

    for metatype in test_metatypes:
        if metric.supports_metatype(metatype):
            if metatype == Metatype.NUMERICAL:
                _test_regression_metric(metric, n_cols = n_outputs)
            else:
                if metatype == Metatype.BINARY:
                    _test_classification_metric(metric, ['good', 'bad'], n_cols = n_outputs)
                else:
                    _test_classification_metric(metric, ['dog', 'cat', 'mouse', 'elephant'], n_cols = n_outputs)


def _test_classification_metric(metric, categories, n_rows = 1000, n_cols = 3):
    index = range(n_rows)

    n_categories = len(categories)

    if len(set(categories)) != n_categories:
        raise TestError('categories must be unique')

    y = create_classification_target(index, n_cols, categories, 0)
    if metric._prediction_method == 'predict_proba':
        if n_cols == 1:
            p = np.random.rand(n_rows, n_categories)
            p /= p.sum(axis=1).reshape(-1,1)
            pred = pd.DataFrame(p, index = index, columns = categories)
        else:
            pred = []
            for i in range(n_cols):
                p = np.random.rand(n_rows, n_categories)
                p /= p.sum(axis=1).reshape(-1,1)
                pred.append(pd.DataFrame(p, index = index, columns = categories))
    elif metric._prediction_method == 'decision_function':
        if n_cols == 1:
            pred = pd.DataFrame(np.random.randn(n_rows, n_categories), index = index, columns = categories)
        else:
            pred = [pd.DataFrame(np.random.randn(n_rows, n_categories), index = index, columns = categories) for i in range(n_cols)]
    else:
        pred = create_classification_target(index, n_cols, categories, 1)
    score = metric.score(y, pred)
    print(f'TESTING DONE: {metric}={score}')

def _test_regression_metric(metric, n_rows = 1000, n_cols = 3):
    index = range(n_rows)
    y = create_regression_target(index, n_cols, 0)
    pred = create_regression_target(index, n_cols, 1)
    score = metric.score(y, pred)
    print(f'TESTING DONE: {metric}={score}')
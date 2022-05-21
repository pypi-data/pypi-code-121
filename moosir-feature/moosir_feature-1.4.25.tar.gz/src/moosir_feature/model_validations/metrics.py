import pandas as pd
import numpy as np
from sklearn.metrics import get_scorer, SCORERS, make_scorer

def binary_returns_metric_fn(y_true: pd.DataFrame, y_pred: np.array):
    assert len(y_true.columns) == 1
    assert np.all((y_pred == 0) | (y_pred == 1)), "predictions must be either 0 or 1"

    temp = y_true.copy()
    temp["_preds"] = y_pred
    score = (temp[temp.columns[0]] * temp["_preds"]).sum()

    return score

def binary_returns_avg_metric_fn(y_true: pd.DataFrame, y_pred: np.array):
    assert len(y_true.columns) == 1
    assert np.all((y_pred == 0) | (y_pred == 1)), "predictions must be either 0 or 1"

    temp = y_true.copy()
    temp["_preds"] = y_pred
    score = (temp[temp.columns[0]] * temp["_preds"]).sum()/len(temp)

    return score


CUSTOM_SCORERS = dict(
    binary_returns=make_scorer(binary_returns_metric_fn),
    binary_returns_avg=make_scorer(binary_returns_avg_metric_fn),
)


def get_any_metric(metrics: list):
    scorers = {}
    for metric in metrics:
        if metric in SCORERS.keys():
            scorers.update({metric: get_scorer(metric)})
        else:
            scorers.update({metric: CUSTOM_SCORERS[metric]})

    return scorers
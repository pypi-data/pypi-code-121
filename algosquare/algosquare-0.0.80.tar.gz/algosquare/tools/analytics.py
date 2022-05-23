import numpy as np
import pandas as pd
from sklearn.utils import check_random_state

def calculate_metric_stats(y, pred, metric, num_samples = None, num_repeats = 1000):
    """
    Calculate metric stats.

    Args:
        y: targets.
        pred: output of Predictor.
        metric: Metric
        num_samples: number of samples to sample.
        num_repeats: number of experiments.

    Returns:
        dict.

    Raises:
        ValueError
    """
    y_np = np.array(y)
    pred_np = np.array(pred)

    random_state = check_random_state(None)

    if num_samples is None:
        num_samples = y.shape[0]
    else:
        if num_samples > y.shape[0]:
            raise ValueError('num_samples greater than samples in y')

    scores = np.zeros(num_repeats)
    idx = np.arange(y.shape[0])
    for n_round in range(num_repeats):
        choice_idx = random_state.choice(idx, num_samples)

        y_sample = y_np[choice_idx]
        pred_sample = pred_np[choice_idx]

        scores[n_round] = metric.score(pd.DataFrame(y_sample, columns = y.columns), pd.DataFrame(pred_sample, columns = pred.columns))

    output = dict()
    output['num_samples'] = num_samples
    output['num_repeats'] = num_repeats
    output['mean'] = np.mean(scores)
    output['std'] = np.std(scores)
    return output
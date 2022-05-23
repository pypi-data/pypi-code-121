"""Metrics to evaluate models."""

import numpy as np

from sklearn.metrics._scorer import SCORERS, get_scorer, _PredictScorer, _ProbaScorer, _ThresholdScorer
from sklearn.utils.multiclass import type_of_target 

from ..base.metric import Metric
from ..base.types import Metatype, is_target_metatype

class SklearnMetric(Metric):
    def __init__(self, scorer_name, metatypes, aggregation = 'mean'):
        """
        Invokes underlying score function.

        Args:
            scorer_name: sklearn scorer.
            metatypes: Metatype or set thereof.
            aggregation: combine multi-output problems using 'min','max','mean','median' or None.
        """
        scorer = get_scorer(scorer_name)
        if isinstance(scorer, _ProbaScorer):
            prediction_method = 'predict_proba'
        elif isinstance(scorer, _ThresholdScorer):
            prediction_method = 'decision_function'
        else:
            prediction_method = 'predict'

        if aggregation not in ('min','max','mean','median', None):
            raise ValueError('aggregation must be min, max, mean, median or None')

        super().__init__(_map_scorer_name(scorer_name), metatypes, prediction_method, scorer._sign == 1)
        self._aggregation = aggregation
        self._scorer_name = scorer_name
        self._score_func = scorer._score_func
        self._kwargs = scorer._kwargs

        self.pos_label = None

    def to_dict(self):
        output = super().to_dict()
        if self.pos_label is not None:
            output['kwargs'] = dict(pos_label = self.pos_label)
        return output

    def score(self, y, pred):
        """
        Invokes underlying score function.

        Args:
            y: targets.
            pred: model predictions.

        Returns:
            float.
        """
        if self._metatypes == {Metatype.BINARY} and self.pos_label is None:
            raise RuntimeError('pos_label missing')

        if y.shape[1] == 1:
            return self._score(y, pred, self.pos_label)

        if self._prediction_method == 'predict':
            scores = [self._score(y[col], pred[col], self._get_pos_label(i)) for i, col in enumerate(y.columns)]
        else:
            scores = [self._score(y[col], pred[i], self._get_pos_label(i)) for i, col in enumerate(y.columns)]

        if self._aggregation is None:
            return scores

        return getattr(np, self._aggregation)(scores)

    def _score(self, y, pred, pos_label = None):
        if pos_label is None:
            return self._score_func(y, pred, **self._kwargs)

        if self._prediction_method == 'predict':
            return self._score_func(y == pos_label, pred == pos_label, **self._kwargs)

        return self._score_func(y == pos_label, pred[pos_label], **self._kwargs)

    def _get_pos_label(self, i):
        if self.pos_label is None:
            return None

        return self.pos_label[i]

def _map_scorer_name(name):
    return name.replace('neg_', '')

REGRESSION_SCORERS = {
 'explained_variance',
 'max_error',
 'neg_mean_absolute_error',
 'neg_mean_absolute_percentage_error',
 'neg_mean_gamma_deviance',
 'neg_mean_poisson_deviance',
 'neg_mean_squared_error',
 'neg_mean_squared_log_error',
 'neg_median_absolute_error',
 'neg_root_mean_squared_error',
 'r2'}

CLUSTERING_SCORERS = {
 'adjusted_mutual_info_score',
 'adjusted_rand_score',
 'completeness_score',
 'fowlkes_mallows_score',
 'homogeneity_score',
 'mutual_info_score',
 'normalized_mutual_info_score',
 'rand_score',
 'v_measure_score'}

CLASSIFICATION_SCORERS = {
 'accuracy',
 'average_precision',
 'balanced_accuracy',
 'f1',
 'f1_macro',
 'f1_micro',
 'f1_samples',
 'f1_weighted',
 'jaccard',
 'jaccard_macro',
 'jaccard_micro',
 'jaccard_samples',
 'jaccard_weighted',
 'neg_brier_score',
 'neg_log_loss',
 'precision',
 'precision_macro',
 'precision_micro',
 'precision_samples',
 'precision_weighted',
 'recall',
 'recall_macro',
 'recall_micro',
 'recall_samples',
 'recall_weighted',
 'roc_auc',
 'roc_auc_ovo',
 'roc_auc_ovo_weighted',
 'roc_auc_ovr',
 'roc_auc_ovr_weighted',
 'top_k_accuracy'}

#exclusively 2 classes
XBINARY_SCORERS = {
 'average_precision',
 'f1',
 'jaccard',
 'neg_brier_score',
 'precision',
 'recall',
 'roc_auc',
}

#exclusively more than 2 classes
XCATEGORICAL_SCORERS = {
 'f1_macro',
 'f1_micro',
 'f1_weighted',
 'jaccard_macro',
 'jaccard_micro',
 'jaccard_weighted',
 'precision_macro',
 'precision_micro',
 'precision_weighted',
 'recall_macro',
 'recall_micro',
 'recall_weighted',
 'roc_auc_ovo',
 'roc_auc_ovo_weighted',
 'roc_auc_ovr',
 'roc_auc_ovr_weighted',
 'top_k_accuracy'}

EXCLUDE_SCORERS = {
 'f1_samples',
 'jaccard_samples',
 'precision_samples',
 'recall_samples',
 'top_k_accuracy'}

METRICS = dict()

for scorer_name in SCORERS:
    if scorer_name not in EXCLUDE_SCORERS:
        if scorer_name in REGRESSION_SCORERS:
            metric = SklearnMetric(scorer_name, Metatype.NUMERICAL)
            METRICS[str(metric)] = metric
        elif scorer_name in CLASSIFICATION_SCORERS:
            if scorer_name in XBINARY_SCORERS:
                metric = SklearnMetric(scorer_name, {Metatype.BINARY})
            elif scorer_name in XCATEGORICAL_SCORERS:
                metric = SklearnMetric(scorer_name, {Metatype.CATEGORICAL})
            else:
                metric = SklearnMetric(scorer_name, {Metatype.BINARY, Metatype.CATEGORICAL})
            METRICS[str(metric)] = metric

def get_metric(metric):
    """
    Returns metric from string.

    Args:
        metric: string

    Returns:
        Metric.

    Raises: 
        KeyError.
    """
    try:
        return METRICS[metric]
    except KeyError:
        raise KeyError(f'valid metrics are: {sorted(list(METRICS))}')

def get_metatype_metrics(metatype):
    """
    Returns metrics that support a given metatype.

    Args:
        metatype: Metatype

    Returns:
        Metric.

    Raises: 
        KeyError.
    """
    if not is_target_metatype(metatype, strict = True):
        raise ValueError('invalid target metatype')

    return {name : metric for name, metric in METRICS.items() if metric.supports_metatype(metatype)}


def _expand_dim(x):
    if x.ndim == 1:
        return np.expand_dims(x, 1)
    return x

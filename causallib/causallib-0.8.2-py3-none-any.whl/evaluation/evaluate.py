"""
(C) IBM Corp, 2018, All rights reserved
Created on Aug 22, 2018

@author: EHUD KARAVANI
"""
import warnings
from copy import deepcopy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import StratifiedKFold

from .plots import get_subplots, plot_propensity_score_distribution_folds, plot_counterfactual_common_support_folds, \
                   plot_calibration_folds, plot_roc_curve_folds, plot_precision_recall_curve_folds, \
                   plot_continuous_prediction_accuracy_folds, plot_residual_folds

from ..estimation.base_weight import WeightEstimator, PropensityEstimator
from ..estimation.base_estimator import IndividualOutcomeEstimator
from ..utils.stat_utils import is_vector_binary

# TODO: How doubly robust fits in to show both weight and outcome model (at least show the plots on the same figure?)


def score_binary_prediction(y_true, y_pred, y_pred_proba, metrics_to_evaluate=None):
    metrics_to_evaluate = metrics_to_evaluate or {"accuracy": metrics.accuracy_score,
                                                  "precision": metrics.precision_score,
                                                  "recall": metrics.recall_score,
                                                  "f1": metrics.f1_score,
                                                  "roc_auc": metrics.roc_auc_score,
                                                  "avg_precision": metrics.average_precision_score,
                                                  "hinge": metrics.hinge_loss,
                                                  "matthews": metrics.matthews_corrcoef,
                                                  "0/1": metrics.zero_one_loss,
                                                  "brier": metrics.brier_score_loss,
                                                  "confusion_matrix": metrics.confusion_matrix,
                                                  "roc_curve": metrics.roc_curve,
                                                  "pr_curve": metrics.precision_recall_curve}
    # TODO: consider removing confusion matrix and roc curves and pr-curves from the list
    scores = {}
    for metric_name, metric_func in metrics_to_evaluate.items():
        if metric_name in {"hinge", "brier", "roc_curve", "roc_auc", "pr_curve", "avg_precision"}:
            prediction = y_pred_proba
        else:
            prediction = y_pred
        try:
            scores[metric_name] = metric_func(y_true, prediction)
        except ValueError as v:  # if y_true has single value
            warnings.warn('metric {} could not be evaluated'.format(metric_name))
            warnings.warn(str(v))
            scores[metric_name] = np.nan
    dtype = np.dtype(object) if any([metric_name in metrics_to_evaluate.keys()
                                     for metric_name in ["confusion_matrix", "roc_curve", "pr_curve"]]) else np.float64
    return pd.Series(scores, dtype=dtype)


def score_continuous_prediction(y_true, y_pred, metrics_to_evaluate=None):
    metrics_to_evaluate = metrics_to_evaluate or {"expvar": metrics.explained_variance_score,
                                                  "mae": metrics.mean_absolute_error,
                                                  "mse": metrics.mean_squared_error,
                                                  "msle": metrics.mean_squared_log_error,
                                                  "mdae": metrics.median_absolute_error,
                                                  "r2": metrics.r2_score}
    scores = {}
    for metric_name, metric_func in metrics_to_evaluate.items():
        try:
            scores[metric_name] = metric_func(y_true, y_pred)
        except ValueError as v:
            scores[metric_name] = np.nan
            warnings.warn('While evaluating ' + metric_name + ': ' + str(v))
    return pd.Series(scores)


def _score_prediction_per_strata(y_true, y_pred, to_stratify, strata, metrics_to_evaluate=None):
    """
    
    Args:
        y_true: 
        y_pred: 
        strata: 
        to_stratify: 
        metrics_to_evaluate: 

    Returns:

    """
    y_is_binary = is_vector_binary(y_true)
    scores = {}
    for stratum in strata:
        y_true_s = y_true[to_stratify.isin(stratum)]
        y_pred_s = y_pred[to_stratify.isin(stratum)]
        if y_is_binary:
            score = score_binary_prediction(y_true_s, y_pred_s > 0.5, y_pred_s, metrics_to_evaluate)
        else:
            score = score_continuous_prediction(y_true_s, y_pred_s, metrics_to_evaluate)
        score = pd.DataFrame(score).T
        score = score.apply(pd.to_numeric, errors="ignore")  # change dtype of each column to numerical if possible.
        scores[str(stratum)[1:-1]] = score  # remove the parenthesis from the string
    index = pd.Index(scores.keys(), name="strata")
    scores = pd.concat(scores, ignore_index=True)
    scores.index = index
    return scores


def evaluate_simple(estimator, X, a, y, plots=None):
    # simple evaluation without cross validation on the provided data
    # (can be to test the model on its train data or on new data

    # FIXME: not tested. Only an implementation idea, general scheme.

    phases = ["simple"]     # dummy phase
    cv = pd.RangeIndex(start=0, stop=X.shape[0])     # All DataFrame rows when using iloc
    cv = [(cv, cv)]     # wrap in a tuple format compatible with sklearn's cv output
    results = evaluate_cv(estimator, X, a, y, cv=cv, refit=False, phases=phases, plots=plots)
    results = list(results)     # if tuple, convert to mutable list, if non-iterable convert to a singleton.

    # Remove the redundant phase and fold information, since it was done once on the entire data:
    results[0] = results[0].reset_index(level=["phase", "fold"], drop=True)
    results = results[0] if len(results) == 1 else tuple(results)
    return results


def evaluate_bootstrap(estimator, X, a, y, n_bootstrap, refit=False):
    # Evaluation using bootstrap

    # FIXME: not tested. Only an implementation idea, general scheme.

    phases = ["simple"]  # dummy phase
    # Generate bootstrap sample:
    cv = []
    for i in range(n_bootstrap):
        # Get iloc positions (reset_index) of a bootstrap sample (sample the size of X with replacement):
        idx = X.sample(n=X.shape[0], replace=True).reset_index().index
        cv.append((idx, idx))
    results = evaluate_cv(estimator, X, a, y, cv=cv, refit=refit, phases=phases, plots=None)
    return results


def evaluate_cv(estimator, X, a, y, cv=None, kfold=None, refit=True, phases=("train", "valid"), plots=None):
    """

    Args:
        estimator: CausalLib causal estimator. Should be train if refit is False.
        X:
        a:
        y:
        cv (list[tuples] | generator[tuples]): list the number of folds containing tuples of indices
                                               (train_idx, validation_idx)
        kfold(sklearn.model_selection.BaseCrossValidator): Initialized fold object (e.g. KFold).
                                                           defaults to StratifiedKFold of 5 splits based on treatment.
        refit (bool): Whether to refit the model on each fold. This is ideal to examine true performance of the model
                      specification, but can be turned off in case fitting takes to many resources or there's a need
                      to examine performance on test data.
        phases (list[str]|tuple[str]): {["train", "valid"], ["train"], ["valid"]}.
                                       What phases to evaluate on - train ("train"), validation ("valid") or both.
                                       Should be iterable.
        plots (list[str] | None): What (or if any) plots to plot. Will None function will only score and won't plot.

    Returns:

    """
    # There's a need to have consistent splits for predicting, scoring and plotting.
    # If cv is a generator, it would be lost after after first use. if kfold has shuffle=True, it would be inconsistent.
    # In order to keep consistent reproducible folds across the process, we save them as a list.
    if cv is not None:
        cv = list(cv)   # if cv is generator it would listify it, if cv is already a list this is idempotent
    else:
        kfold = kfold or StratifiedKFold(n_splits=5)
        cv = list(kfold.split(X=X, y=a))

    predictions, models = predict_cv(estimator, X, a, y, cv, refit, phases)

    scores = score_cv(estimator, predictions, X, a, y, cv)

    if plots is not None:
        plots = plot_cv(predictions, X, a, y, cv, plots)

    return_values = (scores, )
    return_values += (plots, ) if plots is not None else ()
    return_values += (models, ) if refit is True else ()    # since the model used is the exact one that was provided
    return_values = return_values[0] if len(return_values) == 1 else return_values  # unpack scores from tuple if alone
    # TODO: unpacking via * so not to return explicit tuple, but an 'expanded' tuple -> return *return_values
    return return_values


def plot_cv(predictions, X, a, y, cv, plots):

    phases = predictions.keys()
    all_axes = {phase: {} for phase in phases}

    for phase in phases:
        phase_fig, phase_axes = get_subplots(len(plots))
        phase_axes = phase_axes.ravel()     # squeeze a vector out of the matrix-like structure of the returned fig.

        # Retrieve all indices of the different folds in the phase [idx_fold_1, idx_folds_2, ...]
        cv_idx_folds = [fold_idx[0] if phase == "train" else fold_idx[1] for fold_idx in cv]
        predictions_folds = predictions[phase]

        for i, plot_name in enumerate(plots):
            # Plot:
            # TODO: how to pass parameters to plots?
            if plot_name == "propensity_dist":
                phase_axes[i] = plot_propensity_score_distribution_folds(predictions_folds, X, a, y, cv_idx_folds,
                                                                         reflect=True, ax=phase_axes[i])
            elif plot_name == "common_support":
                phase_axes[i] = plot_counterfactual_common_support_folds(predictions_folds, X, a, y, cv_idx_folds,
                                                                         ax=phase_axes[i])
            elif plot_name == "propensity_calibration":
                phase_axes[i] = plot_calibration_folds(predictions_folds, X=X, a=a, y=None, cv=cv_idx_folds,
                                                       n_bins=10, plot_rug=False, plot_histogram=False, quantile=True,
                                                       ax=phase_axes[i])
            elif plot_name == "outcome_calibration":
                phase_axes[i] = plot_calibration_folds(predictions_folds, X=X, a=a, y=y, cv=cv_idx_folds,
                                                       n_bins=10, plot_rug=False, plot_histogram=False, quantile=True,
                                                       ax=phase_axes[i])
            elif plot_name == "weight_roc_curve":
                phase_axes[i] = plot_roc_curve_folds(predictions_folds, X=X, a=a, y=None, cv=cv_idx_folds,
                                                     ax=phase_axes[i])
            elif plot_name == "outcome_roc_curve":
                phase_axes[i] = plot_roc_curve_folds(predictions_folds, X=X, a=a, y=y, cv=cv_idx_folds,
                                                     ax=phase_axes[i])
            elif plot_name == "weight_precision_recall_curve":
                phase_axes[i] = plot_precision_recall_curve_folds(predictions_folds, X=X, a=a, y=None, cv=cv_idx_folds,
                                                                  ax=phase_axes[i])
            elif plot_name == "outcome_precision_recall_curve":
                phase_axes[i] = plot_precision_recall_curve_folds(predictions_folds, X=X, a=a, y=y, cv=cv_idx_folds,
                                                                  ax=phase_axes[i])
            elif plot_name == "continuous_accuracy_plot":
                phase_axes[i] = plot_continuous_prediction_accuracy_folds(predictions_folds, X=X, a=a, y=y,
                                                                          cv=cv_idx_folds, ax=phase_axes[i])
            elif plot_name == "residual_plot":
                phase_axes[i] = plot_residual_folds(predictions_folds, X=X, a=a, y=y, cv=cv_idx_folds, ax=phase_axes[i])
            else:
                raise ValueError("Plot name provided ({}) is not supported.".format(plot_name))

            all_axes[phase][plot_name] = phase_axes[i]

            # All plots types = ["support" (common), "calibration", "roc-curve", "propensity" (distribution),
            #                    "accuracy" (predicted over actual), "balancing" (covariates)]

    return all_axes


def score_cv(estimator, predictions, X, a, y, cv):
    """

    Args:
        estimator: CausalLib causal estimator. Used only to know what scoring scheme to apply
        predictions (dict[str, list[pd.Series | pd.DataFrame]]): the output of predict_cv.
        X (pd.DataFrame):
        a (pd.Series):
        y (pd.Series):
        cv (list[tuples]): list the number of folds containing tuples of indices (train_idx, validation_idx)

    Returns:
        pd.DataFrame: DataFrame whose columns are different metrics and each row is a product of phase x fold x strata.
    """
    phases = predictions.keys()
    scores = {phase: [] for phase in phases}
    for i, (train_idx, valid_idx) in enumerate(cv):
        data = {"train": {"X": X.iloc[train_idx], "a": a.iloc[train_idx], "y": y.iloc[train_idx]},
                "valid": {"X": X.iloc[valid_idx], "a": a.iloc[valid_idx], "y": y.iloc[valid_idx]}}

        for phase in phases:
            X_fold, a_fold, y_fold = data[phase]["X"], data[phase]["a"], data[phase]["y"]
            prediction = predictions[phase][i]

            fold_scores = _estimator_score(estimator, prediction, a_fold, y_fold)
            scores[phase].append(fold_scores)

    # Concatenate the scores from list of folds to DataFrame with rows as folds, keeping it by different phases:
    scores = {phase: pd.concat(scores_fold, axis="index", keys=range(len(scores_fold)), names=["fold"])
              for phase, scores_fold in scores.items()}
    # Concatenate the train/validation DataFrame scores into DataFrame with rows as phases:
    scores = pd.concat(scores, axis="index", names=["phase"])
    return scores


def predict_cv(estimator, X, a, y, cv, refit=True, phases=("train", "valid")):
    """

    Args:
        estimator (WeightEstimator | EstimateIndividualOutcome): CausalLib causal estimator
        X (pd.DataFrame):
        a (pd.Series):
        y (pd.Series):
        cv (list[tuples]): list the number of folds containing tuples of indices (train_idx, validation_idx)
        refit (bool): Whether to refit the model on each fold. This is ideal to examine true performance of the model
                      specification, but can be turned off in case fitting takes to many resources or there's a need
                      to examine performance on test data.
        phases (list[str]|tuple[str]): {["train", "valid"], ["train"], ["valid"]}.
                                       What phases to evaluate on - train ("train"), validation ("valid") or both.
                                       Should be iterable.
    Returns:
        (dict[str, list[pd.Series | pd.DataFrame]], list): A two-tuple containing:

            * predictions: dictionary with keys being the phases provided and values are list the size of the number of
                           folds in cv and containing the output of the estimator on that corresponding fold.
                           For example, predictions["valid"][3] contains the prediction of the estimator on untrained
                            data of the third (i.e. validation set of the third fold)
            * models: list the size of the number of folds in cv containing of fitted estimator on the training data
                      of that fold.
    """

    predictions = {phase: [] for phase in phases}
    models = []
    for train_idx, valid_idx in cv:
        data = {"train": {"X": X.iloc[train_idx], "a": a.iloc[train_idx], "y": y.iloc[train_idx]},
                "valid": {"X": X.iloc[valid_idx], "a": a.iloc[valid_idx], "y": y.iloc[valid_idx]}}

        if refit:
            _estimator_fit(estimator, data)

        for phase in phases:
            fold_prediction = _estimator_predict(estimator, data, phase)
            predictions[phase].append(fold_prediction)

        models.append(deepcopy(estimator))
    return predictions, models


def score_weight_estimation(a_true, predicted_weights, metrics_to_evaluate=None):
    propensity = 1 / predicted_weights      # TODO: remove
    scores = score_binary_prediction(y_true=a_true, y_pred=propensity > 0.5, y_pred_proba=propensity,
                                     metrics_to_evaluate=metrics_to_evaluate)
    scores = pd.DataFrame(scores).T
    scores = scores.apply(pd.to_numeric, errors="ignore")  # change dtype of each column to numerical if possible.
    return scores


def score_individual_outcome_estimation(y_true, prediction, stratify_target, metrics_to_evaluate=None):

    unique_stratification_values = np.sort(np.unique(stratify_target))
    scores = {}
    # Score by strata:
    labels_to_stratify_upon = [[_] for _ in unique_stratification_values]  # wrap singleton as iterable to use is_in
    for treatment_value, counterfactual_outcome in prediction.items():
        score = _score_prediction_per_strata(y_true, counterfactual_outcome, stratify_target,
                                             labels_to_stratify_upon, metrics_to_evaluate)
        scores[str(treatment_value)] = score
    # Score overall:
    prediction = prediction.lookup(stratify_target.index, stratify_target)      # Extract prediction on actual treatment
    prediction = pd.Series(prediction, index=stratify_target.index)
    scores["actual"] = _score_prediction_per_strata(y_true, prediction, stratify_target,
                                                    [tuple(unique_stratification_values)], metrics_to_evaluate)
    scores = pd.concat(scores, names=["model"])
    return scores


# ################ #
# HELPER FUNCTIONS #
# ################ #
# For managing API differences between Weight and IndividualOutcome Estimators

def _estimator_score(estimator, prediction, a_fold, y_fold):
    if isinstance(estimator, WeightEstimator):
        fold_scores = score_weight_estimation(a_fold, prediction)
        # TODO: Table1? using X_fold
    elif isinstance(estimator, IndividualOutcomeEstimator):
        fold_scores = score_individual_outcome_estimation(y_fold, prediction, a_fold)
    else:
        raise TypeError("Causal estimator provided is unknown or not supported")
    return fold_scores


def _estimator_predict(estimator, data, phase):
    if isinstance(estimator, PropensityEstimator):
        fold_prediction = estimator.compute_propensity(data[phase]["X"], data[phase]["a"])
    elif isinstance(estimator, WeightEstimator):
        fold_prediction = estimator.compute_weights(data[phase]["X"], data[phase]["a"], use_stabilized=False)
    elif isinstance(estimator, IndividualOutcomeEstimator):
        # Use predict_probability if possible since it is needed for most evaluations:
        fold_prediction = estimator.estimate_individual_outcome(data[phase]["X"], data[phase]["a"], predict_proba=True)
        # Prediction probability evaluation is only applicable for binary outcome:
        y_values = data[phase]["y"].unique()
        if y_values.size == 2:
            event_value = y_values.max()    # get the maximal value, assumes binary 0-1 (1: event, 0: non-event)
            # Extract the probability for event:
            fold_prediction = fold_prediction.xs(key=event_value, axis="columns", level="y")
        else:
            warnings.warn("Multiclass probabilities are not well defined  and supported for evaluation.\n"
                          "Falling back to class predictions.\n"
                          "Plots might be uninformative due to input being classes and not probabilities.")
            fold_prediction = estimator.estimate_individual_outcome(data[phase]["X"], data[phase]["a"],
                                                                    predict_proba=False)
    else:
        raise TypeError("Causal estimator provided is unknown or not supported")
    return fold_prediction


def _estimator_fit(estimator, data):
    if isinstance(estimator, WeightEstimator):
        estimator.fit(X=data["train"]["X"], a=data["train"]["a"])
    elif isinstance(estimator, IndividualOutcomeEstimator):
        estimator.fit(X=data["train"]["X"], a=data["train"]["a"], y=data["train"]["y"])
    else:
        raise TypeError("Causal estimator provided is unknown or not supported")




#
# def evaluate_weight_estimator(estimator, X, a, y, metrics_to_evaluate=None):
#     """
#
#     Args:
#         estimator (WeightEstimator): fitted estimator
#         X (pd.DataFrame):
#         a (pd.Series):
#         y (pd.Series):
#         metrics_to_evaluate (dict):
#
#     Returns:
#
#     """
#     estimation = estimator.compute_weights(X=X, a=a)
#     scores = score_binary_prediction(a, estimation.gt(0.5), estimation, metrics_to_evaluate)
#     return scores
#
#
# def evaluate_individual_outcome_estimator(estimator, X, a, y, metrics_to_evaluate=None):
#     """
#
#     Args:
#         estimator (EstimateIndividualOutcome): fitted estimator
#         X (pd.DataFrame):
#         a (pd.Series):
#         y (pd.Series):
#         metrics_to_evaluate (dict):
#
#     Returns:
#
#     """
#     unique_treatment_values = np.sort(np.unique(a))
#     values_to_stratify_upon = [tuple(unique_treatment_values)]          # Overall - no stratification.
#     values_to_stratify_upon += [[_] for _ in unique_treatment_values]   # wrap singleton as iterable to use is_in
#     scores = {}
#     estimation = estimator.estimate_individual_outcome(X=X, a=a)
#     for treatment_value, counterfactual_outcome in estimation.items():
#         scores[treatment_value] = _score_prediction_per_strata(y, counterfactual_outcome, a, values_to_stratify_upon,
#                                                                metrics_to_evaluate)
#     scores = pd.concat(scores, names=["model"])
#     return scores


# def evaluate_old(estimator, X, a, y, cv=None, kfold=None):
#     """
#
#     Args:
#         estimator: CausalLib causal estimator
#         X:
#         a:
#         y:
#         cv (list[tuples]): list the number of folds containing tuples of indices (train_idx, validation_idx)
#         kfold(sklearn.model_selection.BaseCrossValidator): Initialized fold object (e.g. KFold).
#                                                            defaults to StratifiedKFold of 5 splits based on treatment.
#
#     Returns:
#
#     """
#     kfold = kfold or StratifiedKFold(n_splits=5)
#
#     scores = {"train": [], "valid": []}
#     models = []
#     for train_idx, valid_idx in cv or kfold.split(X, a):
#         data = {"train": {"X": X.iloc[train_idx, :], "a": a.iloc[train_idx, :], "y": y.iloc[train_idx, :]},
#                 "valid": {"X": X.iloc[valid_idx, :], "a": y.iloc[valid_idx, :], "y": y.iloc[valid_idx, :]}}
#
#         estimator.fit(X=data["train"]["X"], a=data["train"]["a"], y=data["train"]["y"])
#
#         for phase in ["train", "valid"]:
#             if isinstance(estimator, WeightEstimator):
#                 scores_fold = evaluate_weight_estimator(estimator, **data[phase])
#             elif isinstance(estimator, IndividualOutcomeEstimator):
#                 scores_fold = evaluate_individual_outcome_estimator(estimator, **data[phase])
#
#             else:
#                 raise TypeError("Causal estimator provided is unknown or not supported")
#             scores[phase].append(scores_fold)
#
#         models.append(deepcopy(estimator))
#
#     axes = None
#
#
#     # Concatenate the scores from list of folds to DataFrame with rows as folds, keeping it by different phases:
#     scores = {phase: pd.concat(scores_fold, axis="index", keys=range(len(scores_fold)), names=["fold"])
#               for phase, scores_fold in scores.items()}
#     # Concatenate the train/validation DataFrame scores into DataFrame with rows as phases:
#     scores = pd.concat(scores, axis="index", names=["phase"])
#
#     return scores, axes, models

"""Module for training BDTs."""

from __future__ import annotations

# stdlib
import json
import logging
import os
from pathlib import PosixPath
from pprint import pformat
from typing import Any

# externals
import matplotlib

matplotlib.use("pdf")
import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pygram11 import histogram
from scipy import interp
from sklearn.base import BaseEstimator
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import auc, roc_auc_score, roc_curve, RocCurveDisplay
from sklearn.ensemble import HistGradientBoostingClassifier

# tdub
from tdub.art import setup_tdub_style, draw_atlas_label
from tdub.data import (
    Region,
    as_region,
    features_for,
    quick_files,
    selection_for,
    selection_as_numexpr,
)
from tdub.frames import iterative_selection, drop_cols
from tdub.hist import bin_centers
from tdub.math import ks_twosample_binned
import tdub.config

setup_tdub_style()
log = logging.getLogger(__name__)


class SingleTrainingSummary:
    """Describes some properties of a single training.

    Parameters
    ----------
    auc : float
        the AUC value for the model
    ks_test_sig : float
        the binned KS test value for signal
    ks_pvalue_sig : float
        the binned KS test p-value for signal
    ks_test_bkg : float
        the binned KS test value for background
    ks_pvalue_bkg : float
        the binned KS test p-value for background
    kwargs : dict
        currently unused

    Attributes
    ----------
    auc : float
        the AUC value for the model
    ks_test_sig : float
        the binned KS test value for signal
    ks_pvalue_sig : float
        the binned KS test p-value for signal
    ks_test_bkg : float
        the binned KS test value for background
    ks_pvalue_bkg : float
        the binned KS test p-value for background

    """

    def __init__(
        self,
        *,
        auc: float = -1.0,
        ks_test_sig: float = -1.0,
        ks_pvalue_sig: float = -1.0,
        ks_test_bkg: float = -1.0,
        ks_pvalue_bkg: float = -1.0,
        **kwargs,
    ) -> None:
        """Class init."""
        self.auc = auc
        self.ks_test_sig = ks_test_sig
        self.ks_pvalue_sig = ks_pvalue_sig
        self.ks_test_bkg = ks_test_bkg
        self.ks_pvalue_bkg = ks_pvalue_bkg
        self.bad_ks = self.ks_pvalue_sig < 0.2 or self.ks_pvalue_bkg < 0.2

    def __repr__(self) -> str:
        """Clean representation of the result."""
        p1 = f"auc={self.auc:0.3}"
        p2 = f"ks_test_sig={self.ks_test_sig:0.5}"
        p3 = f"ks_pvalue_sig={self.ks_pvalue_sig:0.5}"
        p4 = f"ks_test_bkg={self.ks_test_bkg:0.5}"
        p5 = f"ks_pvalue_bkg={self.ks_pvalue_bkg:0.5}"
        return f"SingleTrainingSummary({p1}, {p2}, {p3}, {p4}, {p5})"


class ResponseHistograms:
    """Create and use histogrammed model response information.

    Parameters
    ----------
    response_type : str
        Models provide different types of response, like a raw
        prediction or a probability of signal. This class supports:

        - `"predict"` (for LGBM),
        - `"decision_function"` (for Scikit-learn)
        - `"proba"` (for either).
    model : BaseEstimator
        The trained model.
    X_train : array_like
        Training data feature matrix.
    X_test : array_like
        Testing data feature matrix.
    y_train : array_like
        Training data labels.
    y_test : array_like
        Testing data labels.
    w_train : array_like
        Training data event weights
    w_test : array_like
        Testing data event weights
    nbins : int
        Number of bins to use.

    """

    def __init__(
        self,
        response_type,
        model,
        X_train,
        X_test,
        y_train,
        y_test,
        w_train,
        w_test,
        nbins: int = 30,
    ):
        """Class constructor."""
        self.response_type = response_type
        self.r_train, self.r_test = self._eval_model(model, X_train, X_test)
        self._calculate(
            self.r_train, self.r_test, y_train, y_test, w_train, w_test, nbins
        )

    def _eval_model(self, model, X_train, X_test):
        if self.response_type == "predict":
            try:
                r_test = model.predict(X_test, raw_score=True)
                r_train = model.predict(X_train, raw_score=True)
            except TypeError:
                r_test = model.predict(X_test)
                r_train = model.predict(X_train)
        elif self.response_type == "decision_function":
            r_test = model.decision_function(X_test)
            r_train = model.decision_function(X_train)
        elif self.response_type == "proba":
            r_test = model.predict_proba(X_test)[:, 1]
            r_train = model.predict_proba(X_train)[:, 1]
        else:
            raise ValueError("response_type must be 'predict' or 'proba'")
        return r_train, r_test

    def _calculate(self, r_train, r_test, y_train, y_test, w_train, w_test, nbins):
        sig_test_p = y_test == 1
        sig_train_p = y_train == 1
        bkg_test_p = np.invert(sig_test_p)
        bkg_train_p = np.invert(sig_train_p)
        sig_train = r_train[sig_train_p]
        sig_test = r_test[sig_test_p]
        bkg_train = r_train[bkg_train_p]
        bkg_test = r_test[bkg_test_p]
        xmin = min(bkg_train.min(), bkg_test.min())
        xmax = max(sig_train.max(), sig_test.max())
        self.bins = np.linspace(xmin, xmax, nbins + 1)
        # fmt: off
        sig_test_h = histogram(sig_test, bins=self.bins, density=True, weights=w_test[sig_test_p])
        bkg_test_h = histogram(bkg_test, bins=self.bins, density=True, weights=w_test[bkg_test_p])
        sig_train_h = histogram(sig_train, bins=self.bins, density=True, weights=w_train[sig_train_p])
        bkg_train_h = histogram(bkg_train, bins=self.bins, density=True, weights=w_train[bkg_train_p])
        # fmt: on
        self.train_sig_h = sig_train_h[0]
        self.train_sig_e = sig_train_h[1]
        self.train_bkg_h = bkg_train_h[0]
        self.train_bkg_e = bkg_train_h[1]
        self.test_sig_h = sig_test_h[0]
        self.test_sig_e = sig_test_h[1]
        self.test_bkg_h = bkg_test_h[0]
        self.test_bkg_e = bkg_test_h[1]
        self.ks_sig = ks_twosample_binned(
            self.train_sig_h, self.test_sig_h, self.train_sig_e, self.test_sig_e
        )
        self.ks_bkg = ks_twosample_binned(
            self.train_bkg_h, self.test_bkg_h, self.train_bkg_e, self.test_bkg_e
        )

    @property
    def ks_sig_test(self) -> float:
        """float: Two sample binned KS test for signal."""
        return round(float(self.ks_sig[0]), 5)

    @property
    def ks_sig_pval(self) -> float:
        """float: Two sample binned KS p-value for signal."""
        return round(float(self.ks_sig[1]), 5)

    @property
    def ks_bkg_test(self) -> float:
        """float: Two sample binned KS test for background."""
        return round(float(self.ks_bkg[0]), 5)

    @property
    def ks_bkg_pval(self) -> float:
        """float: Two sample binned KS p-value for background."""
        return round(float(self.ks_bkg[1]), 5)

    def as_dict(self) -> dict[str, np.ndarray]:
        """dict: The histogram information as a dictionary."""
        return {
            "train_sig": list(self.train_sig_h),
            "train_bkg": list(self.train_bkg_h),
            "test_sig": list(self.test_sig_h),
            "test_bkg": list(self.test_bkg_h),
            "bins": list(self.bins),
        }

    def draw(
        self,
        ax: plt.Axes | None = None,
        xlabel: str | None = None,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Draw the response histograms.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Predefined matplotlib axes to use.
        xlabel : str, optional
            Override the automated xlabel definition.

        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib figure object.
        matplotlib.axes.Axes
            The matplotlib axes object.

        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(5.06, 4.5))
        else:
            fig = ax.get_figure()
        bc = bin_centers(self.bins)
        ax.hist(
            bc,
            bins=self.bins,
            weights=self.train_sig_h,
            label=r"$tW$ (train)",
            histtype="stepfilled",
            alpha=0.5,
            edgecolor="C0",
            color="C0",
        )
        ax.errorbar(
            bc,
            self.test_sig_h,
            yerr=self.test_sig_e,
            label=r"$tW$ (test)",
            color="C0",
            fmt="o",
            markersize=4,
        )
        ax.hist(
            bc,
            bins=self.bins,
            weights=self.train_bkg_h,
            label=r"$t\bar{t}$ (train)",
            histtype="stepfilled",
            alpha=0.4,
            edgecolor="C3",
            color="C3",
        )
        ax.errorbar(
            bc,
            self.test_bkg_h,
            yerr=self.test_bkg_e,
            label=r"$t\bar{t}$ (test)",
            color="C3",
            fmt="o",
            markersize=4,
        )
        if self.response_type == "proba":
            ax.set_xlim([0, 1])
        else:
            ax.set_xlim([self.bins[0], self.bins[-1]])
        ax.set_ylim([0, 1.35 * ax.get_ylim()[1]])
        ax.legend(loc="upper right", ncol=1, frameon=False, numpoints=1)
        handles, labels = ax.get_legend_handles_labels()
        handles = [handles[0], handles[2], handles[1], handles[3]]
        labels = [labels[0], labels[2], labels[1], labels[3]]
        ax.legend(
            handles, labels, loc="upper right", ncol=1, frameon=False, numpoints=1
        )
        ax.set_ylabel("Arbitrary Units")
        draw_atlas_label(
            ax,
            cme_and_lumi=False,
            extra_lines=["$tW$ BDT Training"],
            follow_shift=0.22,
        )
        if xlabel is None:
            if self.response_type == "proba":
                ax.set_xlabel("Classifier Signal Probability")
            else:
                ax.set_xlabel("Classifier Response")
        else:
            ax.set_xlabel(xlabel)
        return fig, ax


def prepare_from_root(
    sig_files: list[str],
    bkg_files: list[str],
    region: Region | str,
    branches: list[str] | None = None,
    override_selection: str | None = None,
    weight_mean: float | None = None,
    weight_scale: float | None = None,
    scale_sum_weights: bool = True,
    use_campaign_weight: bool = False,
    use_tptrw: bool = False,
    use_trrw: bool = False,
    test_case_size: int | None = None,
    bkg_sample_frac: float | None = None,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Prepare the data to train in a region with signal and background ROOT files.

    Parameters
    ----------
    sig_files : list(str)
        List of signal ROOT files.
    bkg_files : list(str)
        List of background ROOT files.
    region : Region or str
        Region where we're going to perform the training.
    branches : list(str), optional
        Override the list of features (usually defined by the region).
    override_selection : str, optional
        Manual selection string to apply to the dataset (this will
        override the region defined selection).
    weight_mean : float, optional
        Scale all weights such that the mean weight is this value. Cannot be
        used with `weight_scale`.
    weight_scale : float, optional
        Value to scale all weights by, cannot be used with `weight_mean`.
    scale_sum_weights : bool
        Scale sum of weights of signal to be sum of weights of background.
    use_campaign_weight : bool
        See the parameter description for :py:func:`tdub.frames.iterative_selection`.
    use_tptrw : bool
        Apply the top pt reweighting factor.
    use_trrw : bool
        Apply the top recursive reweighting factor.
    test_case_size : int, optional
        Prepare a small test case dataset using this many training and
        testing samples.
    bkg_sample_frac : float, optional
        Sample a fraction of the background data.

    Returns
    -------
    :py:obj:`pandas.DataFrame`
       Event feature matrix.
    :py:obj:`numpy.ndarray`
       Event labels (0 for background; 1 for signal).
    :py:obj:`numpy.ndarray`
       Event weights.

    Examples
    --------
    >>> from tdub.data import quick_files
    >>> from tdub.train import prepare_from_root
    >>> qfiles = quick_files("/path/to/data")
    >>> df, labels, weights = prepare_from_root(qfiles["tW_DR"], qfiles["ttbar"], "2j2b")

    """
    if weight_scale is not None and weight_mean is not None:
        raise ValueError("weight_scale and weight_mean cannot be used together")

    log.info("Preparing a single dataset from ROOT files")
    log.info("Signal files:")
    for f in sig_files:
        log.info(" - %s" % f)
    log.info("Background files:")
    for f in bkg_files:
        log.info(" - %s" % f)

    if override_selection is not None:
        selection = override_selection
        log.info(f"Overriding selection (in region {region}) to {override_selection}")
    else:
        selection = selection_for(region)
    selection = selection_as_numexpr(selection)
    log.info("Total selection is: '%s'" % selection)

    if branches is None:
        log.info("Using features defined by the region")
        branches = features_for(region)

    sig_df = iterative_selection(
        files=sig_files,
        selection=selection,
        weight_name="weight_nominal",
        keep_category="kinematics",
        branches=branches,
        exclude_avoids=True,
        use_campaign_weight=use_campaign_weight,
    )
    bkg_df = iterative_selection(
        files=bkg_files,
        selection=selection,
        weight_name="weight_nominal",
        keep_category="kinematics",
        branches=branches,
        exclude_avoids=True,
        use_campaign_weight=use_campaign_weight,
        use_tptrw=use_tptrw,
        use_trrw=use_trrw,
        sample_frac=bkg_sample_frac,
    )

    if test_case_size is not None:
        if test_case_size > 5000:
            log.warn("why bother with test_case_size > 5000?")
        sig_df = sig_df.sample(n=test_case_size, random_state=tdub.config.RANDOM_STATE)
        bkg_df = bkg_df.sample(n=test_case_size, random_state=tdub.config.RANDOM_STATE)

    w_sig = sig_df.pop("weight_nominal").to_numpy()
    w_bkg = bkg_df.pop("weight_nominal").to_numpy()
    w_sig[w_sig < 0] = 0.0
    w_bkg[w_bkg < 0] = 0.0
    if scale_sum_weights:
        w_sig *= w_bkg.sum() / w_sig.sum()
    if "weight_campaign" in sig_df:
        drop_cols(sig_df, "weight_campaign")
    if "weight_campaign" in bkg_df:
        drop_cols(bkg_df, "weight_campaign")

    sorted_cols = sorted(sig_df.columns.to_list(), key=str.lower)
    sig_df = sig_df[sorted_cols]
    bkg_df = bkg_df[sorted_cols]

    cols = sig_df.columns.to_list()
    assert cols == bkg_df.columns.to_list(), "sig/bkg columns are different. bad."
    log.info("Features in prepared dataset:")
    for c in cols:
        log.info(" - %s" % c)

    df = pd.concat([sig_df, bkg_df])
    y = np.concatenate([np.ones_like(w_sig), np.zeros_like(w_bkg)])
    w = np.concatenate([w_sig, w_bkg])

    if weight_scale is not None:
        w *= weight_scale
    if weight_mean is not None:
        w *= weight_mean * len(w) / np.sum(w)

    df.selection_used = selection
    return df, y, w


def persist_prepared_data(
    out_dir: str | os.PathLike,
    df: pd.DataFrame,
    labels: np.ndarray,
    weights: np.ndarray,
) -> None:
    """Persist prepared data to disk.

    The product of :py:func:`tdub.ml_train.prepare_from_root` is
    easily persistable to disk; this function performs that task. If
    the same prepared data is going to be used for multiple training
    executations, one can save CPU cycles by saving the prepared data
    instead of starting higher upstream with our ROOT ntuples.

    Parameters
    ----------
    out_dir : str or os.PathLike
        Directory to save output to.
    df : pandas.DataFrame
        Prepared DataFrame object.
    labels : numpy.ndarray
        Prepared labels.
    weights : numpy.ndarray
        Prepared weights.

    Examples
    --------
    >>> from tdub.data import quick_files
    >>> from tdub.train import prepare_from_root, persist_prepared_data
    >>> qfiles = quick_files("/path/to/data")
    >>> df, y, w = prepare_from_root(qfiles["tW_DR"], qfiles["ttbar"], "2j2b")
    >>> persist_prepared_data("/path/to/output/data", df, y, w)

    """
    out_dir = PosixPath(out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    df.to_hdf(out_dir / "df.h5", "df", mode="w", complevel=0)
    np.save(out_dir / "labels.npy", labels)
    np.save(out_dir / "weights.npy", weights)
    selection_file = PosixPath(out_dir / "selection.txt")
    selection_file.write_text(f"{df.selection_used}\n")


def tdub_train_axes(
    learning_rate: float = 0.1,
    max_depth: int = 5,
    min_child_samples: int = 50,
    num_leaves: int = 31,
    reg_lambda: float = 0.0,
    **kwargs,
) -> dict[str, Any]:
    """Construct a dictionary of default tdub training tune.

    Extra keyword arguments are swallowed but never used.

    Parameters
    ----------
    learning_rate : float
        Learning rate for a classifier.
    max_depth : int
        Max depth for a classifier.
    min_child_samples : int
        Min child samples for a classifier.
    num_leaves : int
        Num leaves for a classifier.
    reg_lambda : float
        Lambda regularation (L2 regularation).

    Returns
    -------
    dict(str, Any)
        The argument names and values

    """
    return dict(
        learning_rate=learning_rate,
        max_depth=max_depth,
        min_child_samples=min_child_samples,
        num_leaves=num_leaves,
        reg_lambda=reg_lambda,
    )


def sklearn_gen_classifier(
    early_stopping_rounds: int = 10,
    validation_fraction: float = 0.20,
    train_axes: dict[str, Any] | None = None,
    **clf_params,
) -> BaseEstimator:
    """Create a classifier using scikit-learn.

    This uses Scikit-learn's
    :py:obj:`sklearn.ensemble.HistGradientBoostingClassifier`.

    The constructor to define early stopping rounds. Extra keyword
    arguments passed to the classifier initialization

    Parameters
    ----------
    early_stopping_rounds : int
        Passed as the `n_iter_no_change` argument to scikit-learn's
        HistGradientBoostingClassifier.
    validation_fraction : float
        Passed to the `validation_fraction` argument in scikit-learn's
        HistGradientBoostingClassifier.
    train_axes : dict[str, Any]
        Values of required tdub training parameters.
    clf_params : kwargs
        Extra arguments passed to the constructor.

    Returns
    -------
    sklearn.ensemble.HistGradientBoostingClassifier
        The classifier.

    """
    if train_axes is None:
        train_axes = tdub_train_axes()

    params = dict(
        loss="binary_crossentropy",
        early_stopping=True,
        verbose=1,
        n_iter_no_change=early_stopping_rounds,
        validation_fraction=validation_fraction,
        max_iter=500,
        learning_rate=train_axes.get("learning_rate"),
        max_depth=train_axes.get("max_depth"),
        min_samples_leaf=train_axes.get("min_child_samples"),
        max_leaf_nodes=train_axes.get("num_leaves"),
        l2_regularization=train_axes.get("reg_lambda"),
    )
    for k, v in clf_params.items():
        if k not in params.keys():
            params[k] = v
    clf = HistGradientBoostingClassifier(**params)
    log.info("Prepared sklearn classifier with parameters:")
    for k, v in clf.get_params().items():
        log.info(f"{k:>20} = {v}")
    return clf


def sklearn_train_classifier(
    clf: BaseEstimator,
    X_train: Any,
    y_train: Any,
    w_train: Any,
    **fit_params,
) -> BaseEstimator:
    """Train a Scikit-learn classifier.

    Parameters
    ----------
    clf : sklearn.ensemble.HistGradientBoostingClassifier
        The classifier
    X_train : array_like
        Training events matrix
    y_train : array_like
        Training event labels
    w_train : array_like
        Training event weights
    fit_params : kwargs
        Extra keyword arguments passed to the classifier.

    Returns
    -------
    sklearn.ensemble.HistGradientBoostingClassifier
        The same classifier object passed to the function.

    """
    params = {}
    for k, v in fit_params.items():
        if k not in params.keys():
            params[k] = v
    return clf.fit(X_train, y_train, sample_weight=w_train)


def lgbm_gen_classifier(
    train_axes: dict[str, Any] = None, **clf_params
) -> BaseEstimator:
    """Create a classifier using LightGBM.

    Parameters
    ----------
    train_axes : dict[str, Any]
        Values of required tdub training parameters.
    clf_params : kwargs
        Extra arguments passed to the constructor.

    Returns
    -------
    lightgbm.LGBMClassifier
        The classifier.

    """
    import lightgbm as lgbm

    if train_axes is None:
        train_axes = tdub_train_axes()

    params = dict(
        learning_rate=train_axes.get("learning_rate", 0.1),
        max_depth=train_axes.get("max_depth", 5),
        min_child_samples=train_axes.get("min_child_samples", 50),
        num_leaves=train_axes.get("num_leaves", 50),
        reg_lambda=train_axes.get("reg_lambda", 0.0),
    )
    for k, v in clf_params.items():
        if k not in params.keys():
            params[k] = v
    clf = lgbm.LGBMClassifier(boosting_type="gbdt", n_estimators=500, **params)
    for k, v in clf.get_params().items():
        log.info(f"{k:>20} = {v}")
    return clf


def lgbm_train_classifier(
    clf: BaseEstimator,
    X_train: Any,
    y_train: Any,
    w_train: Any,
    validation_fraction: float = 0.20,
    early_stopping_rounds: int = 10,
    **fit_params,
) -> BaseEstimator:
    """Train a LGBMClassifier.

    Parameters
    ----------
    clf : lightgbm.LGBMClassifier
        The classifier
    X_train : array_like
        Training events matrix
    y_train : array_like
        Training event labels
    w_train : array_like
        Training event weights
    validation_fraction : float
        Fraction of training events to use in validation set.
    early_stopping_rounds : int
        Number of early stopping rounds to use in training.
    fit_params : keyword arguments
        Extra keyword arguments passed to the classifier.

    Returns
    -------
    lightgbm.LGBMClassifier
        The same classifier object passed to the function

    """
    X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
        X_train,
        y_train,
        w_train,
        test_size=validation_fraction,
        random_state=tdub.config.RANDOM_STATE,
        shuffle=True,
    )
    return clf.fit(
        X_t,
        y_t,
        sample_weight=w_t,
        eval_set=[(X_v, y_v)],
        eval_metric="auc",
        eval_sample_weight=[w_v],
        early_stopping_rounds=early_stopping_rounds,
    )


def xgb_gen_classifier(
    train_axes: dict[str, Any] = None, **clf_params
) -> BaseEstimator:
    """Create a classifier using XGBoost.

    Parameters
    ----------
    train_axes : dict[str, Any]
        Values of required tdub training parameters.
    clf_params : kwargs
        Extra arguments passed to the constructor.

    Returns
    -------
    xgboost.XGBClassifier
        The classifier.

    """
    import xgboost as xgb

    if train_axes is None:
        train_axes = tdub_train_axes()
    params = dict(
        learning_rate=train_axes.get("learning_rate", 0.1),
        max_depth=train_axes.get("max_depth", 5),
        min_child_weight=train_axes.get("min_child_samples", 50),
        reg_lambda=train_axes.get("reg_lambda", 0.0),
    )
    clf = xgb.XGBClassifier(booster="gbtree", n_estimators=500, **params)
    for k, v in clf.get_params().items():
        log.info(f"{k:>20} = {v}")
    return clf


def xgb_train_classifier(
    clf: BaseEstimator,
    X_train: Any,
    y_train: Any,
    w_train: Any,
    validation_fraction: float = 0.20,
    early_stopping_rounds: int = 10,
    **fit_params,
) -> BaseEstimator:
    """Train a XGBClassifier.

    clf : xgboost.XGBClassifier
        The classifier
    X_train : array_like
        Training events matrix
    y_train : array_like
        Training event labels
    w_train : array_like
        Training event weights
    validation_fraction : float
        Fraction of training events to use in validation set.
    early_stopping_rounds : int
        Number of early stopping rounds to use in training.
    fit_params : keyword arguments
        Extra keyword arguments passed to the classifier.

    Returns
    -------
    xgboost.XGBClassifier
        The same classifier object passed to the function

    """

    X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
        X_train,
        y_train,
        w_train,
        test_size=validation_fraction,
        random_state=tdub.config.RANDOM_STATE,
        shuffle=True,
    )
    return clf.fit(
        X_t,
        y_t,
        sample_weight=w_t,
        eval_set=[(X_v, y_v)],
        eval_metric="auc",
        sample_weight_eval_set=[w_v],
        early_stopping_rounds=early_stopping_rounds,
    )


def single_training(
    df: pd.DataFrame,
    labels: np.ndarray,
    weights: np.ndarray,
    train_axes: dict[str, Any],
    output_dir: str | os.PathLike,
    test_size: float = 0.40,
    early_stopping_rounds: int | None = None,
    extra_summary_entries: dict[str, Any] | None = None,
    use_sklearn: bool = False,
    use_xgboost: bool = False,
    save_lgbm_txt: bool = False,
) -> None:
    """Execute a single training with some parameters.

    The model and some useful information (mostly plots) are saved to
    `output_dir`.

    Parameters
    ----------
    df : pandas.DataFrame
        Feature matrix in dataframe format
    labels : numpy.ndarray
        Event labels (`1` for signal; `0` for background)
    weights : numpy.ndarray
        Event weights
    train_axes : dict(str, Any)
        Dictionary of parameters defining the tdub train axes.
    output_dir : str or os.PathLike
        Directory to save results of training
    test_size : float
        Test size for splitting into training and testing sets
    early_stopping_rounds : int, optional
        Number of rounds to have no improvement for stopping training.
    extra_summary_entries : dict, optional
        Extra entries to save in the JSON output summary.
    use_sklearn : bool
        Use Scikit-learn's HistGradientBoostingClassifier.
    use_xgboost : bool
        Use XGBoost's XGBClassifier.
    save_lgbm_txt : bool
        Save fitted LGBM model to text file (ignored if either
        ``use_sklearn`` or ``use_xgboost`` is ``True``).

    Returns
    -------
    SingleTrainingSummary
        Useful information about the training

    Examples
    --------
    >>> from tdub.data import quick_files
    >>> from tdub.train import prepare_from_root, single_round, tdub_train_axes
    >>> qfiles = quick_files("/path/to/data")
    >>> df, labels, weights = prepare_from_root(qfiles["tW_DR"], qfiles["ttbar"], "2j2b")
    >>> train_axes = tdub_train_axes()
    ...     learning_rate=0.05
    ...     max_depth=5,
    ... )
    >>> single_round(
    ...     df,
    ...     labels,
    ...     weights,
    ...     tdub_train_axes,
    ...     "training_output",
    ... )

    """
    use_lgbm = not use_sklearn and not use_xgboost

    if sum([use_sklearn, use_lgbm, use_xgboost]) != 1:
        raise RuntimeError("BDT provider not defined properly.")

    starting_dir = os.getcwd()
    output_path = PosixPath(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    log.info("Saving training output to %s" % output_path.resolve())
    os.chdir(output_path)

    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        df,
        labels,
        weights,
        test_size=test_size,
        random_state=tdub.config.RANDOM_STATE,
        shuffle=True,
    )

    log.info(f"test size used: {test_size}")
    log.info("selection used on the datasets:")
    log.info("  '%s'" % df.selection_used)
    log.info("features training with:")
    for c in X_train.columns:
        log.info(" - %s" % c)

    # Create and train model
    train_axes = tdub_train_axes(**train_axes)
    if use_sklearn:
        model = sklearn_gen_classifier(
            early_stopping_rounds=early_stopping_rounds,
            validation_fraction=0.33,
            train_axes=train_axes,
        )
        sklearn_train_classifier(model, X_train, y_train, w_train)
    elif use_xgboost:
        model = xgb_gen_classifier(train_axes=train_axes)
        xgb_train_classifier(
            model,
            X_train,
            y_train,
            w_train,
            early_stopping_rounds=early_stopping_rounds,
        )
    elif use_lgbm:
        model = lgbm_gen_classifier(train_axes=train_axes)
        lgbm_train_classifier(
            model,
            X_train,
            y_train,
            w_train,
            early_stopping_rounds=early_stopping_rounds,
        )

    # Save the model
    joblib.dump(model, "model.joblib.gz", compress=("gzip", 3))
    if use_lgbm and save_lgbm_txt:
        model.booster_.save_model("model.txt")

    importances_gain = {}
    importances_split = {}
    # Plot Importances
    if use_lgbm:
        import lightgbm as lgbm

        fig_imp, (ax_imp_gain, ax_imp_split) = plt.subplots(2, 1)
        lgbm.plot_importance(model, ax=ax_imp_gain, importance_type="gain", precision=2)
        lgbm.plot_importance(
            model, ax=ax_imp_split, importance_type="split", precision=2
        )
        ax_imp_gain.set_xlabel("Importance (gain)")
        ax_imp_split.set_xlabel("Importance (split)")
        ax_imp_gain.set_title("")
        ax_imp_split.set_title("")
        fig_imp.subplots_adjust(left=0.475, top=0.975, bottom=0.09, right=0.925)
        fig_imp.savefig("imp.pdf")
        imp_gain = model.booster_.feature_importance(importance_type="gain")
        imp_split = model.booster_.feature_importance(importance_type="split")
        feat_name = model.booster_.feature_name()
        imp_gain = np.array(imp_gain, dtype=np.float64)
        imp_split = np.array(imp_split, dtype=np.float64)
        imp_gain *= 1.0 / np.sum(imp_gain)
        imp_split *= 1.0 / np.sum(imp_split)
        for n, g, s in zip(feat_name, imp_gain, imp_split):
            importances_gain[n] = float(g)
            importances_split[n] = float(s)

    # Histograms: plot and extract information from them
    proba_histograms = ResponseHistograms(
        "proba", model, X_train, X_test, y_train, y_test, w_train, w_test
    )
    if use_sklearn:
        pred_histograms = ResponseHistograms(
            "decision_function",
            model,
            X_train,
            X_test,
            y_train,
            y_test,
            w_train,
            w_test,
        )
    elif use_xgboost:
        pred_histograms = ResponseHistograms(
            "predict", model, X_train, X_test, y_train, y_test, w_train, w_test
        )
    elif use_lgbm:
        pred_histograms = ResponseHistograms(
            "predict", model, X_train, X_test, y_train, y_test, w_train, w_test
        )

    # ROC curve
    fig_roc, ax_roc = plt.subplots(figsize=(4.5, 4))
    # rcd = plot_roc_curve(model, X_test, y_test, sample_weight=w_test, ax=ax_roc, lw=2)
    rcd = RocCurveDisplay.from_predictions(
        y_test,
        pred_histograms.r_test,
        sample_weight=w_test,
        ax=ax_roc,
        lw=2,
        label="Test",
    )
    rcd_train = RocCurveDisplay.from_predictions(
        y_train,
        pred_histograms.r_train,
        sample_weight=w_train,
        ax=ax_roc,
        lw=2,
        label="Train",
    )

    fig_pred, ax_pred = pred_histograms.draw()
    fig_proba, ax_proba = proba_histograms.draw()
    fig_pred.subplots_adjust(bottom=0.125, left=0.15)
    fig_pred.savefig("pred.pdf")
    fig_proba.subplots_adjust(bottom=0.125, left=0.15)
    fig_proba.savefig("proba.pdf")
    sts = SingleTrainingSummary(
        auc=float(rcd.roc_auc),
        ks_test_sig=proba_histograms.ks_sig_test,
        ks_pvalue_sig=proba_histograms.ks_sig_pval,
        ks_test_bkg=proba_histograms.ks_bkg_test,
        ks_pvalue_bkg=proba_histograms.ks_bkg_pval,
    )

    ax_roc.set_ylabel("True postive rate")
    ax_roc.set_xlabel("False positive rate")
    ax_roc.grid(color="black", alpha=0.125)
    ax_roc.legend(loc="lower right")

    if extra_summary_entries is not None:
        r = extra_summary_entries["region"]
        draw_atlas_label(
            ax_roc,
            cme_and_lumi=False,
            follow="Simulation",
            extra_lines=[f"{r} Region"],
            follow_shift=0.25,
        )

    fig_roc.subplots_adjust(bottom=0.125, left=0.15)
    fig_roc.savefig("roc.pdf")

    # JSON Summary
    summary = {"auc": round(rcd.roc_auc, 5)}
    summary["selection_used"] = df.selection_used
    summary["bad_ks"] = sts.bad_ks
    summary["ks_test_sig"] = sts.ks_test_sig
    summary["ks_test_bkg"] = sts.ks_test_bkg
    summary["ks_pvalue_sig"] = sts.ks_pvalue_sig
    summary["ks_pvalue_bkg"] = sts.ks_pvalue_bkg
    summary["features"] = [c for c in df.columns]
    summary["set_params"] = train_axes
    summary["all_params"] = model.get_params()
    summary["best_iteration"] = -1
    summary["importances_gain"] = importances_gain
    summary["importances_split"] = importances_split
    summary["proba_histograms"] = proba_histograms.as_dict()
    summary["pred_histograms"] = pred_histograms.as_dict()

    if early_stopping_rounds is not None:
        if hasattr(model, "n_iter_"):
            summary["best_iteration"] = int(model.n_iter_)
        elif hasattr(model, "best_iteration"):
            summary["best_iteration"] = int(model.best_iteration)
        elif hasattr(model, "best_iteration_"):
            summary["best_iteration"] = int(model.best_iteration_)
        else:
            log.warn("best iteration undetected")
    if extra_summary_entries is not None:
        for k, v in extra_summary_entries.items():
            summary[k] = v
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    # Finish by going back to starting directory
    os.chdir(starting_dir)


def folded_training(
    df: pd.DataFrame,
    labels: np.ndarray,
    weights: np.ndarray,
    params: dict[str, Any],
    fit_kw: dict[str, Any],
    output_dir: str | os.PathLike,
    region: str,
    kfold_kw: dict[str, Any] = None,
) -> float:
    """Execute a folded training.

    Train a :obj:`lightgbm.LGBMClassifier` model using :math:`k`-fold
    cross validation using the given input data and parameters. The
    models resulting from the training (and other important training
    information) are saved to ``output_dir``. The entries in the
    ``kfold_kw`` argument are forwarded to the
    :obj:`sklearn.model_selection.KFold` class for data preprocessing.
    The default arguments that we use are (random_state is controlled
    by the tdub.config module):

    - ``n_splits``: 3
    - ``shuffle``: ``True``

    Parameters
    ----------
    df : pandas.DataFrame
        Feature matrix in dataframe format
    labels : numpy.ndarray
        Event labels (``1`` for signal; ``0`` for background)
    weights : :obj:`numpy.ndarray`
        Event weights
    params : dict(str, Any)
        Dictionary of :obj:`lightgbm.LGBMClassifier` parameters
    fit_kw : dict(str, Any)
        Dictionary of arguments forwarded to :py:func:`lightgbm.LGBMClassifier.fit`.
    output_dir : str or os.PathLike
        Directory to save results of training
    region : str
        String representing the region
    kfold_kw : optional dict(str, Any)
        Arguments passed to :obj:`sklearn.model_selection.KFold`

    Returns
    -------
    float
        Negative mean area under the ROC curve (AUC)

    Examples
    --------
    >>> from tdub.data import quick_files
    >>> from tdub.train import prepare_from_root
    >>> from tdub.train import folded_training
    >>> qfiles = quick_files("/path/to/data")
    >>> df, labels, weights = prepare_from_root(qfiles["tW_DR"], qfiles["ttbar"], "2j2b")
    >>> params = dict(
    ...     boosting_type="gbdt",
    ...     num_leaves=42,
    ...     learning_rate=0.05
    ...     reg_alpha=0.2,
    ...     reg_lambda=0.8,
    ...     max_depth=5,
    ... )
    >>> folded_training(
    ...     df,
    ...     labels,
    ...     weights,
    ...     params,
    ...     {"verbose": 20},
    ...     "/path/to/train/output",
    ...     "2j2b",
    ...     kfold_kw={"n_splits": 5, "shuffle": True},
    ... )

    """
    import lightgbm as lgbm

    starting_dir = os.getcwd()
    output_path = PosixPath(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    os.chdir(output_path)

    log.info("selection used on the datasets:")
    log.info("  '%s'" % df.selection_used)
    log.info("features training with:")
    for c in df.columns:
        log.info(" - %s" % c)

    log.info("model parameters:")
    for k, v in params.items():
        if v is not None:
            log.info(f"{k:>20} | {v:<12}")

    log.info("saving output to %s" % output_path.resolve())

    fig_proba_hists, ax_proba_hists = plt.subplots()
    fig_pred_hists, ax_pred_hists = plt.subplots()
    fig_rocs, ax_rocs = plt.subplots()

    tprs = []
    aucs = []
    importances = np.zeros(len(df.columns))
    mean_fpr = np.linspace(0, 1, 100)
    folder = KFold(**kfold_kw, random_state=tdub.config.RANDOM_STATE)
    fold_number = 0
    nfits = 0
    for train_idx, test_idx in folder.split(df):
        # fmt: off
        X_train, X_test = df.iloc[train_idx], df.iloc[test_idx]
        y_train, y_test = labels[train_idx], labels[test_idx]
        w_train, w_test = weights[train_idx], weights[test_idx]
        validation_data = [(X_test, y_test)]
        validation_w = w_test

        # n_sig = y_train[y_train == 1].shape[0]
        # n_bkg = y_train[y_train == 0].shape[0]
        # scale_pos_weight = n_bkg / n_sig
        # log.info(f"n_bkg / n_sig = {n_bkg} / {n_sig} = {scale_pos_weight}")
        # params["scale_pos_weight"] = scale_pos_weight

        model = lgbm.LGBMClassifier(**params)
        fitted_model = model.fit(
            X_train,
            y_train,
            sample_weight=w_train,
            eval_set=validation_data,
            eval_metric="auc",
            eval_sample_weight=[validation_w],
            **fit_kw,
        )

        joblib.dump(fitted_model, f"model_fold{fold_number}.joblib.gz", compress=("gzip", 3))

        nfits += 1
        importances += fitted_model.feature_importances_

        fold_fig_proba, fold_ax_proba = plt.subplots()
        fold_fig_pred, fold_ax_pred = plt.subplots()

        test_proba = fitted_model.predict_proba(X_test)[:, 1]
        train_proba = fitted_model.predict_proba(X_train)[:, 1]
        test_pred = fitted_model.predict(X_test, raw_score=True)
        train_pred = fitted_model.predict(X_train, raw_score=True)

        proba_sig_test = test_proba[y_test == 1]
        proba_bkg_test = test_proba[y_test == 0]
        proba_sig_train = train_proba[y_train == 1]
        proba_bkg_train = train_proba[y_train == 0]
        pred_sig_test = test_pred[y_test == 1]
        pred_bkg_test = test_pred[y_test == 0]
        pred_sig_train = train_pred[y_train == 1]
        pred_bkg_train = train_pred[y_train == 0]
        w_sig_test = w_test[y_test == 1]
        w_bkg_test = w_test[y_test == 0]
        w_sig_train = w_train[y_train == 1]
        w_bkg_train = w_train[y_train == 0]
        proba_bins = np.linspace(0, 1, 31)
        proba_bc = bin_centers(proba_bins)
        predxmin = min(pred_bkg_test.min(), pred_bkg_train.min())
        predxmax = max(pred_sig_test.max(), pred_sig_train.max())
        pred_bins = np.linspace(predxmin, predxmax, 31)

        # Axis with all folds (proba histograms)
        ax_proba_hists.hist(proba_sig_test, bins=proba_bins, label=f"F{fold_number} Sig. (test)",
                            density=True, histtype="step", weights=w_sig_test)
        ax_proba_hists.hist(proba_bkg_test, bins=proba_bins, label=f"F{fold_number} Bkg. (test)",
                            density=True, histtype="step", weights=w_bkg_test)
        ax_proba_hists.hist(proba_sig_train, bins=proba_bins, label=f"F{fold_number} Sig. (train)",
                            density=True, histtype="step", weights=w_sig_train)
        ax_proba_hists.hist(proba_bkg_train, bins=proba_bins, label=f"F{fold_number} Bkg. (train)",
                            density=True, histtype="step", weights=w_bkg_train)

        # Axis specific to the fold (proba histograms)
        fold_ax_proba.hist(proba_sig_train, bins=proba_bins, label=f"F{fold_number} Sig. (train)", density=True,
                           weights=w_sig_train, histtype="stepfilled", color="C0", edgecolor="C0", alpha=0.5, linewidth=1)
        fold_ax_proba.hist(proba_bkg_train, bins=proba_bins, label=f"F{fold_number} Bkg. (train)", density=True,
                           weights=w_bkg_train, histtype="stepfilled", color="C3", edgecolor="C3", alpha=0.4, linewidth=1)

        train_h_sig = histogram(proba_sig_test, bins=proba_bins, weights=w_sig_test, flow=False, density=True)
        train_h_bkg = histogram(proba_bkg_test, bins=proba_bins, weights=w_bkg_test, flow=False, density=True)

        fold_ax_proba.errorbar(proba_bc, train_h_sig[0], yerr=train_h_sig[1], markersize=4,
                               color="C0", fmt="o", label=f"F{fold_number} Sig. (test)")
        fold_ax_proba.errorbar(proba_bc, train_h_bkg[0], yerr=train_h_bkg[1], markersize=4,
                               color="C3", fmt="o", label=f"F{fold_number} Bkg. (test)")
        fold_ax_proba.set_ylim([0, 1.5 * fold_ax_proba.get_ylim()[1]])

        # Axis with all
        ax_pred_hists.hist(pred_sig_test, bins=pred_bins, label=f"F{fold_number} Sig. (test)",
                           density=True, histtype="step", weights=w_sig_test)
        ax_pred_hists.hist(pred_bkg_test, bins=pred_bins, label=f"F{fold_number} Bkg. (test)",
                           density=True, histtype="step", weights=w_bkg_test)
        ax_pred_hists.hist(pred_sig_train, bins=pred_bins, label=f"F{fold_number} Sig. (train)",
                           density=True, histtype="step", weights=w_sig_train)
        ax_pred_hists.hist(pred_bkg_train, bins=pred_bins, label=f"F{fold_number} Bkg. (train)",
                           density=True, histtype="step", weights=w_bkg_train)

        fold_ax_pred.hist(pred_sig_test, bins=pred_bins, label=f"F{fold_number} Sig. (test)",
                          density=True, histtype="step", weights=w_sig_test)
        fold_ax_pred.hist(pred_bkg_test, bins=pred_bins, label=f"F{fold_number} Bkg. (test)",
                          density=True, histtype="step", weights=w_bkg_test)
        fold_ax_pred.hist(pred_sig_train, bins=pred_bins, label=f"F{fold_number} Sig. (train)",
                          density=True, histtype="step", weights=w_sig_train)
        fold_ax_pred.hist(pred_bkg_train, bins=pred_bins, label=f"F{fold_number} Bkg. (train)",
                          density=True, histtype="step", weights=w_bkg_train)
        fold_ax_pred.set_ylim([0, 1.5 * fold_ax_pred.get_ylim()[1]])

        fpr, tpr, thresholds = roc_curve(y_test, test_proba, sample_weight=w_test)
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        ax_rocs.plot(fpr, tpr, lw=1, alpha=0.45, label=f"fold {fold_number}, AUC = {roc_auc:0.3}")

        fold_ax_proba.set_ylabel("Arb. Units")
        fold_ax_proba.set_xlabel("Classifier Output")
        fold_ax_proba.legend(ncol=2, loc="upper center")

        fold_ax_pred.set_ylabel("Arb. Units")
        fold_ax_pred.set_xlabel("Classifier Output")
        fold_ax_pred.legend(ncol=2, loc="upper center")

        # fold_fig_proba.subplots_adjust(**_fig_adjustment_dict)
        fold_fig_proba.savefig(f"fold{fold_number}_histograms_proba.pdf")
        # fold_fig_pred.subplots_adjust(**_fig_adjustment_dict)
        fold_fig_pred.savefig(f"fold{fold_number}_histograms_pred.pdf")

        plt.close(fold_fig_proba)
        plt.close(fold_fig_pred)

        # fmt: on
        fold_number += 1

    relative_importances = importances / nfits
    relative_importances = relative_importances / relative_importances.sum()

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    ax_rocs.plot(
        mean_fpr,
        mean_tpr,
        color="b",
        label=f"AUC = {mean_auc:0.2} $\\pm$ {std_auc:0.2}",
        lw=2,
        alpha=0.8,
    )
    ax_rocs.set_xlabel("False Positive Rate")
    ax_rocs.set_ylabel("True Positive Rate")

    ax_proba_hists.set_ylabel("Arb. Units")
    ax_proba_hists.set_xlabel("Classifier Output")
    ax_proba_hists.legend(ncol=3, loc="upper center", fontsize="small")
    ax_proba_hists.set_ylim([0, 1.5 * ax_proba_hists.get_ylim()[1]])
    # fig_proba_hists.subplots_adjust(**_fig_adjustment_dict)
    fig_proba_hists.savefig("histograms_proba.pdf")

    ax_pred_hists.set_ylabel("Arb. Units")
    ax_pred_hists.set_xlabel("Classifier Output")
    ax_pred_hists.legend(ncol=3, loc="upper center", fontsize="small")
    ax_pred_hists.set_ylim([0, 1.5 * ax_pred_hists.get_ylim()[1]])
    # fig_pred_hists.subplots_adjust(**_fig_adjustment_dict)
    fig_pred_hists.savefig("histograms_pred.pdf")

    ax_rocs.grid(color="black", alpha=0.15)
    ax_rocs.legend(ncol=2, loc="lower right")
    # fig_rocs.subplots_adjust(**_fig_adjustment_dict)
    fig_rocs.savefig("roc.pdf")

    summary: dict[str, Any] = {}
    summary["selection_used"] = df.selection_used
    summary["region"] = region
    summary["features"] = [str(c) for c in df.columns]
    summary["importances"] = list(relative_importances)
    summary["kfold"] = kfold_kw
    summary["roc"] = {
        "auc": mean_auc,
        "std": std_auc,
        "mean_fpr": list(mean_fpr),
        "mean_tpr": list(mean_tpr),
    }

    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    os.chdir(starting_dir)
    negative_roc_score = -1.0 * np.mean(aucs)
    return negative_roc_score


_best_fit = None
_best_auc = None
_best_parameters = None
_best_paramdict = None
_ifit = None


def gp_minimize_auc(
    data_dir: str,
    region: Region | str,
    nlo_method: str,
    output_dir: str | os.PathLike = "_unnamed_optimization",
    n_calls: int = 15,
    esr: int | None = 10,
):
    """Minimize AUC using Gaussian processes.

    This is our hyperparameter optimization procedure which uses the
    :py:func:`skopt.gp_minimize` functions from Scikit-Optimize.

    Parameters
    ----------
    data_dir : str
        Path containing ROOT files
    region : Region or str
        Rregion where we're going to perform the training
    nlo_method : str
        Which tW NLO method sample ('DR' or 'DS' or 'Both')
    output_dir : str or os.PathLike
        Path to save optimization output
    n_calls : int
        Number of times to train during the minimization procedure
    esr : int, optional
        Early stopping rounds for fitting the model
    random_state: int
        Random state for splitting data into training/testing

    Examples
    --------
    >>> from tdub.data import Region
    >>> from tdub.train import prepare_from_root, gp_minimize_auc
    >>> gp_minimize_auc("/path/to/data", Region.r2j1b, "DS", "opt_DS_2j1b")
    >>> gp_minimize_auc("/path/to/data", Region.r2j1b, "DR", "opt_DR_2j1b")

    """
    from skopt.utils import use_named_args
    from skopt.space import Real, Integer
    from skopt.plots import plot_convergence
    from skopt import gp_minimize
    import lightgbm as lgbm

    qfiles = quick_files(f"{data_dir}")
    if nlo_method == "DR":
        tW_files = qfiles["tW_DR"]
    elif nlo_method == "DS":
        tW_files = qfiles["tW_DS"]
    elif nlo_method == "Both":
        tW_files = qfiles["tW_DR"] + qfiles["tW_DS"]
        tW_files.sort()
    else:
        raise ValueError("nlo_method must be 'DR' or 'DS' or 'Both'")

    df, labels, weights = prepare_from_root(tW_files, qfiles["ttbar"], region)
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        df,
        labels,
        weights,
        train_size=0.333,
        random_state=tdub.config.RANDOM_STATE,
        shuffle=True,
    )
    validation_data = [(X_test, y_test)]
    validation_w = w_test

    # n_sig = y_train[y_train == 1].shape[0]
    # n_bkg = y_train[y_train == 0].shape[0]
    # scale_pos_weight = n_bkg / n_sig
    # sample_size = n_bkg + n_sig
    # log.info(f"n_bkg / n_sig = {n_bkg} / {n_sig} = {scale_pos_weight}")

    dimensions = [
        Real(low=0.01, high=0.2, prior="log-uniform", name="learning_rate"),
        Integer(low=40, high=250, name="num_leaves"),
        Integer(low=20, high=250, name="min_child_samples"),
        Integer(low=3, high=10, name="max_depth"),
    ]
    default_parameters = [0.1, 100, 50, 5]

    run_from_dir = os.getcwd()
    save_dir = PosixPath(output_dir)
    save_dir.mkdir(exist_ok=True, parents=True)
    os.chdir(save_dir)

    global _best_fit
    global _best_auc
    global _best_parameters
    global _best_paramdict
    global _ifit
    _best_fit = 0
    _best_auc = 0.0
    _best_parameters = [{"teste": 1}]
    _best_paramdict = {}
    _ifit = 0

    @use_named_args(dimensions=dimensions)
    def afit(
        learning_rate,
        num_leaves,
        min_child_samples,
        max_depth,
    ):
        global _ifit
        global _best_fit
        global _best_auc
        global _best_parameters
        global _best_paramdict

        log.info(f"on iteration {_ifit} out of {n_calls}")
        log.info(f"learning_rate: {learning_rate}")
        log.info(f"num_leaves: {num_leaves}")
        log.info(f"min_child_samples: {min_child_samples}")
        log.info(f"max_depth: {max_depth}")

        curdir = os.getcwd()
        p = PosixPath(f"training_{_ifit}")
        p.mkdir(exist_ok=False)
        os.chdir(p.resolve())

        with open("features.txt", "w") as f:
            for c in df.columns:
                print(c, file=f)

        model = lgbm.LGBMClassifier(
            boosting_type="gbdt",
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            min_child_samples=min_child_samples,
            max_depth=max_depth,
            n_estimators=500,
        )

        fitted_model = model.fit(
            X_train,
            y_train,
            sample_weight=w_train,
            eval_set=validation_data,
            eval_metric="auc",
            verbose=20,
            early_stopping_rounds=esr,
            eval_sample_weight=[validation_w],
        )

        pred = fitted_model.predict_proba(X_test)[:, 1]
        score = roc_auc_score(y_test, pred, sample_weight=w_test)

        train_pred = fitted_model.predict_proba(X_train)[:, 1]
        fig, ax = plt.subplots()
        bins = np.linspace(0, 1, 31)
        ax.hist(
            train_pred[y_train == 0],
            bins=bins,
            label="Bkg. (train)",
            density=True,
            histtype="step",
            weights=w_train[y_train == 0],
        )
        ax.hist(
            train_pred[y_train == 1],
            bins=bins,
            label="Sig. (train)",
            density=True,
            histtype="step",
            weights=w_train[y_train == 1],
        )
        ax.hist(
            pred[y_test == 0],
            bins=bins,
            label="Bkg. (test)",
            density=True,
            histtype="step",
            weights=w_test[y_test == 0],
        )
        ax.hist(
            pred[y_test == 1],
            bins=bins,
            label="Sig. (test)",
            density=True,
            histtype="step",
            weights=w_test[y_test == 1],
        )
        ax.set_ylim([0, 1.5 * ax.get_ylim()[1]])
        ax.legend(ncol=2, loc="upper center")
        # fig.subplots_adjust(**_fig_adjustment_dict)
        fig.savefig("histograms.pdf")
        plt.close(fig)

        binning_sig = np.linspace(0, 1, 31)
        binning_bkg = np.linspace(0, 1, 31)

        h_sig_test, err_sig_test = histogram(
            pred[y_test == 1], bins=binning_sig, weights=w_test[y_test == 1]
        )
        h_sig_train, err_sig_train = histogram(
            train_pred[y_train == 1], bins=binning_sig, weights=w_train[y_train == 1]
        )

        h_bkg_test, err_bkg_test = histogram(
            pred[y_test == 0], bins=binning_bkg, weights=w_test[y_test == 0]
        )
        h_bkg_train, err_bkg_train = histogram(
            train_pred[y_train == 0], bins=binning_bkg, weights=w_train[y_train == 0]
        )

        ks_statistic_sig, ks_pvalue_sig = ks_twosample_binned(
            h_sig_test, h_sig_train, err_sig_test, err_sig_train
        )
        ks_statistic_bkg, ks_pvalue_bkg = ks_twosample_binned(
            h_bkg_test, h_bkg_train, err_bkg_test, err_bkg_train
        )

        if ks_pvalue_sig < 0.1 or ks_pvalue_bkg < 0.1:
            score = score * 0.9

        log.info(f"ksp sig: {ks_pvalue_sig}")
        log.info(f"ksp bkg: {ks_pvalue_bkg}")

        curp = pformat(model.get_params())
        curp = eval(curp)

        with open("params.json", "w") as f:
            json.dump(curp, f, indent=4)

        with open("auc.txt", "w") as f:
            print(f"{score}", file=f)

        with open("ks.txt", "w") as f:
            print(f"sig: {ks_pvalue_sig}", file=f)
            print(f"bkg: {ks_pvalue_bkg}", file=f)

        os.chdir(curdir)

        if score > _best_auc:
            _best_parameters[0] = model.get_params()
            _best_auc = score
            _best_fit = _ifit
            _best_paramdict = curp

        _ifit += 1

        del model
        return -score

    search_result = gp_minimize(
        func=afit,
        dimensions=dimensions,
        acq_func="gp_hedge",
        n_calls=n_calls,
        x0=default_parameters,
    )

    summary = {
        "region": region,
        "nlo_method": nlo_method,
        "features": list(df.columns),
        "best_iteration": _best_fit,
        "best_auc": _best_auc,
        "best_params": _best_paramdict,
    }

    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    fig, ax = plt.subplots()
    plot_convergence(search_result, ax=ax)
    # fig.subplots_adjust(**_fig_adjustment_dict)
    fig.savefig("gpmin_convergence.pdf")

    os.chdir(run_from_dir)
    return 0


def load_prepped(datadir: PosixPath) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Load prepped training data.

    Parameters
    ----------
    datadir : pathlib.PosixPath
        Path to the preppared output.

    Returns
    -------
    :py:obj:`pandas.DataFrame`
        DataFrame containing training variables
    :py:obj:`numpy.ndarray`
        Labels for each event.
    :py:obj:`numpy.ndarray`
        Weights for each event.

    """
    df = pd.read_hdf(datadir / "df.h5", "df")
    y = np.load(datadir / "labels.npy")
    w = np.load(datadir / "weights.npy")
    return df, y, w


def var_and_binning_for_region(
    df: pd.DataFrame, region: str | Region, meta_table: Any
) -> Any:
    """Create list of training variables associated with a region.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containg training variables
    region : str
        String representation of region.
    meta_table : dict(str, Any)
        Variable meta data table.

    Returns
    -------
    list
        List of variables with associated region and binning.
    """
    results = []
    cols = list(df.columns)
    for entry in meta_table["regions"][f"r{str(Region.from_str(str(region)))}"]:
        if entry["var"] in cols:
            results.append(
                (entry["var"], region, (entry["nbins"], entry["xmin"], entry["xmax"]))
            )
    return results


def default_bdt_parameters(region: str | Region) -> Region:
    r = as_region(region)
    if r == Region.r1j1b:
        return dict(
            learning_rate=0.2,
            num_leaves=20,
            min_child_samples=50,
            max_depth=4,
            reg_lambda=0,
        )
    if r == Region.r2j1b:
        return dict(
            learning_rate=0.1,
            num_leaves=20,
            min_child_samples=120,
            max_depth=7,
            reg_lambda=0,
        )
    if r == Region.r2j2b:
        return dict(
            learning_rate=0.2,
            num_leaves=20,
            min_child_samples=50,
            max_depth=4,
            reg_lambda=0,
        )
    raise ValueError(f"Region {region} unknown")

"""Module for selecting features."""

from __future__ import annotations

# stdlib
import copy
import gc
import logging
import os
import json
from pathlib import PosixPath

from typing import Optional, List, Dict, Any, Union, Tuple

# externals
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# tdub
from tdub.frames import iterative_selection, drop_cols
from tdub.data import quick_files, Region, selection_for
import tdub.config

log = logging.getLogger(__name__)


class FeatureSelector:
    """A class to steer the steps of feature selection.

    Parameters
    ----------
    df : pandas.DataFrame
       The dataframe which contains signal and background events; it
       should also only contain features we wish to test for (it is
       expected to be "clean" from non-kinematic information, like
       metadata and weights).
    weights : numpy.ndarray
       the weights array compatible with the dataframe
    importance_type : str
       the importance type ("gain" or "split")
    labels : numpy.ndarray
       array of labels compatible with the dataframe (``1`` for
       :math:`tW` and ``0`` for :math:`t\\bar{t}`.
    corr_threshold : float
       the threshold for excluding features based on correlations
    name : str, optional
       give the selector a name

    Attributes
    ----------
    data : pandas.DataFrame
       the raw dataframe as fed to the class instance
    weights : numpy.ndarray
       the raw weights array compatible with the dataframe
    labels : numpy.ndarray
       the raw labels array compatible with the dataframe (we expect
       ``1`` for signal, :math:`tW`, and ``0`` for background,
       :math:`t\\bar{t}`).
    raw_features : list(str)
       the list of all features determined at initialization
    name : str, optional
       a name for the selector pipeline, required to save the result)
    corr_threshold : float
       the threshold for excluding features based on correlations
    default_clf_opts : dict
       the default arguments we initialize classifiers with.
    corr_matrix : pandas.DataFrame
       the raw correlation matrix for the features (requires calling the
       ``check_collinearity`` function)
    correlated : pandas.DataFrame
       a dataframe matching features that satisfy the correlation threshold
    importances : pandas.DataFrame
       the importances as determined by a vanilla GBDT (requires
       calling the ``check_importances`` function)
    candidates : list(str)
       list of candiate featurese (sorted by importance) as determined
       by calling the ``check_candidates``
    iterative_remove_aucs : dict(str, float)
       a dictionary of the form ``{feature : auc}`` providing the AUC
       value for a BDT trained _without_ the feature given in the
       key. The keys are built from the ``candidates`` list.
    iterative_add_aucs : numpy.ndarray
       an array of AUC values built by iteratively adding the next
       best feature in the candidates list. (the first entry is
       calculated using only the top feature, the second entry uses
       the top 2 features, and so on).

    Examples
    --------
    >>> from tdub.features import FeatureSelector, prepare_from_parquet
    >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
    >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)

    """

    def __init__(
        self,
        df: pd.DataFrame,
        labels: np.ndarray,
        weights: np.ndarray,
        importance_type: str = "gain",
        corr_threshold: float = 0.85,
        name: str | None = None,
    ) -> None:
        assert np.unique(labels).shape[0] == 2, "labels should have 2 unique values"
        assert (
            labels.shape == weights.shape
        ), "labels and weights must have identical shape"
        assert corr_threshold < 1.0, "corr_threshold must be less than 1.0"
        assert (
            df.shape[0] == weights.shape[0]
        ), "df and weights must have the same number of entries"

        # hidden behind properties
        self._df = df
        self._weights = weights
        self._labels = labels
        self._raw_features = df.columns.to_list()

        # completely hidden
        self._nsig = self._labels[self._labels == 1].shape[0]
        self._nbkg = self._labels[self._labels == 0].shape[0]
        self._scale_pos_weight = self._nbkg / self._nsig

        # self._sow_sig = np.sum(self._weights[self._labels == 1])
        # self._sow_bkg = np.sum(self._weights[self._labels == 0])
        # self._weights[self._labels == 1] *= self._sow_bkg / self._sow_sig
        # self._weights *= len(self._weights) / np.sum(self._weights)

        # public attributes
        self.name = name
        self.corr_threshold = corr_threshold
        self.default_clf_opts = dict(
            boosting_type="gbdt",
            importance_type=importance_type,
            learning_rate=0.1,
            n_estimators=200,
            num_leaves=100,
            max_depth=5,
        )

        # Calculated later by some member functions
        # we hide these behind properties
        self._corr_matrix = None
        self._correlated = None
        self._importances = None
        self._candidates = None
        self._iterative_remove_aucs = None
        self._iterative_add_aucs = None
        self._model_params = None

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def weights(self) -> np.ndarray:
        return self._weights

    @property
    def labels(self) -> np.ndarray:
        return self._labels

    @property
    def raw_features(self) -> list[str]:
        return self._raw_features

    @property
    def corr_matrix(self) -> pd.DataFrame:
        return self._corr_matrix

    @property
    def correlated(self) -> pd.DataFrame:
        return self._correlated

    @property
    def importances(self) -> pd.DataFrame:
        return self._importances

    @property
    def candidates(self) -> list[str]:
        return self._candidates

    @property
    def iterative_add_aucs(self) -> list[str]:
        return self._iterative_add_aucs

    @property
    def model_params(self) -> dict[str, Any]:
        return self._model_params

    def check_for_uniques(self, and_drop: bool = True) -> None:
        """Check the dataframe for features that have a single unique value.

        Parameters
        ----------
        and_drop : bool
           If ``True``, and_drop any unique columns.

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        """
        log.info("starting check_for_uniques step")
        uqcounts = pd.DataFrame(self.df.nunique()).T
        to_drop = []
        for col in uqcounts.columns:
            if uqcounts[col].to_numpy()[0] == 1:
                to_drop.append(col)
        if not to_drop:
            log.info("we didn't find any features with single unique values")
        if to_drop and and_drop:
            for d in to_drop:
                log.info(
                    f"dropping {d} because it's a feature with a single unique value"
                )
            self._df.drop(columns=to_drop, inplace=True)

    def check_collinearity(self, threshold: float | None = None) -> None:
        """Calculate the correlations of the features.

        Given a correlation threshold this will construct a list of
        features that should be dropped based on the correlation
        values. This also adds a new property to the instance.

        If the ``threshold`` argument is not None then the class
        instance's ``corr_threshold`` property is updated.

        Parameters
        ----------
        threshold : float, optional
           Override the existing correlations threshold.

        Examples
        --------
        Overriding the exclusion threshold:

        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.corr_threshold
        0.90
        >>> fs.check_collinearity(threshold=0.85)
        >>> fs.corr_threshold
        0.85

        """
        log.info("starting check_collinearity step")
        if threshold is not None:
            self.corr_threshold = threshold

        log.info("calculating correlations")
        self._corr_matrix = self.df.corr()

        uptri = np.triu(np.ones(self.corr_matrix.shape), k=1).astype(np.bool)
        uptri = self.corr_matrix.where(uptri)
        log.info(f"testing correlations above threshold: {self.corr_threshold}")
        dropcols = [
            c for c in uptri.columns if any(uptri[c].abs() > self.corr_threshold)
        ]
        log.info(f"found {len(dropcols)} features with correlations above threshold")

        self._correlated = pd.DataFrame(columns=["drop_this", "because", "coeff"])
        for col in dropcols:
            above_threshold = uptri[col].abs() > self.corr_threshold
            other_features = list(uptri.index[above_threshold])
            coeffs = list(uptri[col][above_threshold])
            this_col = [col for _ in range(len(other_features))]
            self._correlated.append(
                pd.DataFrame(
                    dict(drop_this=this_col, because=other_features, coeff=coeffs)
                )
            )

        log.info("correlations now calculated")

    def check_importances(
        self,
        extra_clf_opts: dict[str, Any] | None = None,
        extra_fit_opts: dict[str, Any] | None = None,
        n_fits: int = 5,
        test_size: float = 0.5,
    ) -> None:
        """Train vanilla GBDT to calculate feature importance.

        some default options are used for the
        :py:class:`lightgbm.LGBMClassifier` instance and fit (see
        implementation); you can provide extras via function some
        arguments.

        Parameters
        ----------
        extra_clf_opts : dict
           extra arguments forwarded to :py:class:`lightgbm.LGBMClassifier`.
        extra_fit_opts : dict
           extra arguments forwarded to :py:func:`lightgbm.LGBMClassifier.fit`.
        n_fits : int
           number of models to fit to determine importances
        test_size : float
           forwarded to :py:func:`sklearn.model_selection.train_test_split`

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.check_collinearity()
        >>> fs.check_importances(extra_fit_opts=dict(verbose=40, early_stopping_round=15))

        """
        import lightgbm as lgbm

        log.info("starting check_importances step")
        clf_opts = copy.deepcopy(self.default_clf_opts)
        if extra_clf_opts is not None:
            for k, v in extra_clf_opts.items():
                clf_opts[k] = v

        log.info("Classifier is configured with parameters:")
        model = lgbm.LGBMClassifier(**clf_opts)
        self._model_params = copy.deepcopy(model.get_params())
        for k, v in model.get_params().items():
            if v is not None:
                log.info(f"{k:>20} | {v:<12}")
        del model

        importance_counter = np.zeros(len(self.raw_features))

        log.info("starting importance testing training iterations")
        for i in range(1, n_fits + 1):
            log.info(f"iteration {i}/{n_fits}")
            model = lgbm.LGBMClassifier(**clf_opts)
            train_df, test_df, train_y, test_y, train_w, test_w = train_test_split(
                self.df,
                self.labels,
                self.weights,
                shuffle=True,
                test_size=test_size,
                random_state=(i * tdub.config.RANDOM_STATE),
            )
            fit_opts = dict(
                eval_metric="auc",
                eval_set=[(test_df, test_y)],
                eval_sample_weight=[test_w],
                early_stopping_rounds=10,
                verbose=20,
            )
            if extra_fit_opts is not None:
                for k, v in extra_fit_opts:
                    fit_opts[k] = v
            model.fit(train_df, train_y, sample_weight=train_w, **fit_opts)
            importance_counter += model.feature_importances_
            gc.enable()
            del train_df, test_df, train_y, test_y, train_w, test_w
            gc.collect()

        self._importances = pd.DataFrame(
            dict(feature=self.raw_features, importance=(importance_counter / n_fits))
        )
        self._importances.sort_values("importance", ascending=False, inplace=True)
        self._importances.reset_index(inplace=True)

    def check_candidates(self, n: int = 20) -> None:
        """Get the top uncorrelated features.

        This will parse the correlations and most important features
        and build a list of ordered important features. When a feature
        that should be dropped due to a collinear feature is found, we
        ensure that the more important member of the pair is included
        in the resulting list and drop the other member of the pair.
        This will populate the ``candidates`` attribute for the class.

        Parameters
        ----------
        n : int
           the total number of features to retrieve

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.check_collinearity()
        >>> fs.check_importances(extra_fit_opts=dict(verbose=40, early_stopping_round=15))
        >>> fs.check_candidates(n=25)

        """
        log.info("starting check_candidates step")
        if self._correlated is None:
            log.error("correlations are not calculated; call check_collinearity()")
            return None
        if self._importances is None:
            log.error(
                "feature importances are not calculated; call check_importances()"
            )
            return None

        log.info(f"checking for top {n} candidates")
        drop_because_corr = self.correlated.drop_this.to_list()
        features_ordered = self.importances.feature.to_list()
        n_top, exclude = [], []
        raw_top_n = features_ordered[:n]
        for f in raw_top_n:
            if f not in drop_because_corr:
                n_top.append(f)
                continue
            log.info(
                f"{f} is in the top {n}; but correlations say drop it; closer look:"
            )
            dropped_df = self.correlations.query("drop == '{f}'")
            for corr_feat in dropped_df.because.to_list():
                if corr_feat not in drop_because_corr:
                    log.info("{corr_feat} will be kept without swap")
                if features_ordered.index(f) < features_ordered.index(corr_feat):
                    log.info("{corr_feat} to be replaced with {f}")
                    n_top.append(f)
                    exclude.append(corr_feat)

        for f in exclude:
            if f in n_top:
                n_top.remove(f)

        temp_dict = {f: None for f in n_top}
        self._candidates = list(temp_dict.keys())

    def check_iterative_remove_aucs(
        self,
        max_features: int | None = None,
        extra_clf_opts: dict[str, Any] | None = None,
        extra_fit_opts: dict[str, Any] | None = None,
    ) -> None:
        """Calculate the aucs iteratively removing one feature at a time.

        After calling the check_candidates function we have a good
        sete of candidate features; this function will train vanilla
        BDTs one at a time removing one of the candidate features. We
        rank the feature based on how impactful its removal is.

        Parameters
        ----------
        max_features : int
           the maximum number of features to allow to be
           checked. default will be the length of the ``candidates``
           list.
        extra_clf_opts : dict
           extra arguments forwarded to :py:class:`lightgbm.LGBMClassifier`.
        extra_fit_opts : dict
           extra arguments forwarded to :py:func:`lightgbm.LGBMClassifier.fit`.

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.check_collinearity()
        >>> fs.check_importances(extra_fit_opts=dict(verbose=40, early_stopping_round=15))
        >>> fs.check_candidates(n=25)
        >>> fs.check_iterative_remove_aucs(max_features=20)

        """
        import lightgbm as lgbm

        log.info("Starting check_iterative_remove_aucs step")
        if self._candidates is None:
            log.error("candidates are not calculated; call check_candidates()")
            return None

        if max_features is None:
            max_features = len(self.candidates)

        train_df, test_df, train_y, test_y, train_w, test_w = train_test_split(
            self.df[self.candidates],
            self.labels,
            self.weights,
            test_size=0.33,
            random_state=tdub.config.RANDOM_STATE,
            shuffle=True,
        )

        clf_opts = copy.deepcopy(self.default_clf_opts)
        if extra_clf_opts is not None:
            for k, v in extra_clf_opts.items():
                clf_opts[k] = v

        log.info("Classifier is configured with parameters:")
        for k, v in clf_opts.items():
            log.info(f"{k:>20} | {v:<12}")

        self._iterative_remove_aucs = {}
        for i, candidate in enumerate(self.candidates):
            log.info(f"removing {candidate} and training a BDT")
            copy_of_candidates = copy.deepcopy(self.candidates[:max_features])
            copy_of_candidates.remove(candidate)
            assert len(copy_of_candidates) == len(self.candidates[:max_features]) - 1
            log.info(f"iteration {i}/{max_features}")
            ifeatures = copy_of_candidates
            itrain_df = train_df[copy_of_candidates]
            itest_df = test_df[copy_of_candidates]
            model = lgbm.LGBMClassifier(**clf_opts)
            fit_opts = dict(
                eval_metric="auc",
                eval_set=[(itest_df, test_y)],
                eval_sample_weight=[test_w],
                early_stopping_rounds=15,
                verbose=20,
            )
            if extra_fit_opts is not None:
                for k, v in extra_fit_opts:
                    fit_opts[k] = v
            model.fit(itrain_df, train_y, sample_weight=train_w, **fit_opts)
            self._iterative_remove_aucs[candidate] = model.best_score_["valid_0"]["auc"]

            gc.enable()
            del ifeatures, itrain_df, itest_df
            gc.collect()

        # sort by value (AUC)
        self._iterative_remove_aucs = {
            k: v
            for k, v in sorted(
                self._iterative_remove_aucs.items(), key=lambda item: item[1]
            )
        }

        for i, (k, v) in enumerate(self._iterative_remove_aucs.items()):
            log.info(f"without rank {i}, {k}, AUC is {v}")
        self._candidates = list(self._iterative_remove_aucs.keys())

    def check_iterative_add_aucs(
        self,
        max_features: int | None = None,
        extra_clf_opts: dict[str, Any] | None = None,
        extra_fit_opts: dict[str, Any] | None = None,
    ) -> None:
        """Calculate aucs iteratively adding the next best feature.

        After calling the check_candidates function we have a good set
        of candidate features; this function will train vanilla BDTs
        iteratively including one more feater at a time starting with
        the most important.

        Parameters
        ----------
        max_features : int
           the maximum number of features to allow to be
           checked. default will be the length of the ``candidates``
           list.
        extra_clf_opts : dict
           extra arguments forwarded to :py:class:`lightgbm.LGBMClassifier`.
        extra_fit_opts : dict
           extra arguments forwarded to :py:func:`lightgbm.LGBMClassifier.fit`.

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.check_collinearity()
        >>> fs.check_importances(extra_fit_opts=dict(verbose=40, early_stopping_round=15))
        >>> fs.check_candidates(n=25)
        >>> fs.check_iterative_add_aucs(max_features=20)

        """
        import lightgbm as lgbm

        log.info("starting check_iterative_add_aucs step")
        if self._candidates is None:
            log.error("candidates are not calculated; call check_candidates()")
            return None

        if max_features is None:
            max_features = len(self.candidates)

        train_df, test_df, train_y, test_y, train_w, test_w = train_test_split(
            self.df[self.candidates],
            self.labels,
            self.weights,
            test_size=0.33,
            random_state=tdub.config.RANDOM_STATE,
            shuffle=True,
        )

        clf_opts = copy.deepcopy(self.default_clf_opts)
        if extra_clf_opts is not None:
            for k, v in extra_clf_opts.items():
                clf_opts[k] = v

        log.info("Classifier is configured with parameters:")
        for k, v in clf_opts.items():
            log.info(f"{k:>20} | {v:<12}")

        self._iterative_add_aucs = []
        for i in range(1, max_features + 1):
            log.info(f"iteration {i}/{max_features}")
            ifeatures = self.candidates[:i]
            itrain_df = train_df[ifeatures]
            itest_df = test_df[ifeatures]
            model = lgbm.LGBMClassifier(**clf_opts)
            fit_opts = dict(
                eval_metric="auc",
                eval_set=[(itest_df, test_y)],
                eval_sample_weight=[test_w],
                early_stopping_rounds=15,
                verbose=20,
            )
            if extra_fit_opts is not None:
                for k, v in extra_fit_opts:
                    fit_opts[k] = v
            model.fit(itrain_df, train_y, sample_weight=train_w, **fit_opts)
            self._iterative_add_aucs.append(model.best_score_["valid_0"]["auc"])

            gc.enable()
            del ifeatures, itrain_df, itest_df
            gc.collect()

        self._iterative_add_aucs = np.array(self._iterative_add_aucs)

    def save_result(self) -> None:
        """Save the results to a directory.

        Parameters
        ----------
        output_dir : str or os.PathLike
           the directory to save relevant results to

        Examples
        --------
        >>> from tdub.features import FeatureSelector, prepare_from_parquet
        >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")
        >>> fs = FeatureSelector(df=df, labels=labels, weights=weights, corr_threshold=0.90)
        >>> fs.check_for_uniques(and_drop=True)
        >>> fs.check_collinearity()
        >>> fs.check_importances(extra_fit_opts=dict(verbose=40, early_stopping_round=15))
        >>> fs.check_candidates(n=25)
        >>> fs.check_iterative_add_aucs(max_features=20)
        >>> fs.name = "2j1b_DR"
        >>> fs.save_result()

        """
        if self.name is None:
            raise ValueError("name attribute cannot be None to save result")
        outdir = PosixPath(f"fsel_result.{self.name}")
        try:
            outdir.mkdir(exist_ok=False)
        except FileExistsError:
            log.warn(f"{outdir} already exists; contents will be overwritten")

        out_raw_aucs = outdir / "raw_aucs.txt"
        out_raw_tf = outdir / "raw_top_features.txt"
        out_params = outdir / "model_params.json"
        with out_raw_aucs.open("w") as f2w:
            np.savetxt(f2w, self.iterative_add_aucs, fmt="%.10f")
        with out_raw_tf.open("w") as f2w:
            f2w.write("\n".join(self.candidates))
            f2w.write("\n")
        with out_params.open("w") as f2w:
            json.dump(self.model_params, f2w, indent=4)


def create_parquet_files(
    qf_dir: str | os.PathLike,
    out_dir: str | os.PathLike | None = None,
    entrysteps: Any | None = None,
    use_campaign_weight: bool = False,
) -> None:
    """Create slimmed and selected parquet files from ROOT files.

    this function requires pyarrow_.

    .. _pyarrow: https://arrow.apache.org/docs/python/

    Parameters
    ----------
    qf_dir : str or os.PathLike
       directory to run :py:func:`tdub.data.quick_files`
    out_dir : str or os.PathLike, optional
       directory to save output files
    entrysteps : any, optional
       entrysteps option forwarded to
       :py:func:`tdub.frames.iterative_selection`
    use_campaign_weight : bool
       multiply the nominal weight by the campaign weight. this is
       potentially necessary if the samples were prepared without the
       campaign weight included in the product which forms the nominal
       weight

    Examples
    --------
    >>> from tdub.features import create_parquet_files
    >>> create_parquet_files("/path/to/root/files", "/path/to/pq/output", entrysteps="250 MB")

    """
    indir = str(PosixPath(qf_dir).resolve())
    qf = quick_files(indir)
    if out_dir is None:
        out_dir = PosixPath(".")
    else:
        out_dir = PosixPath(out_dir)
        out_dir.mkdir(exist_ok=True, parents=True)
    if entrysteps is None:
        entrysteps = "1 GB"

    for r in ("1j1b", "2j1b", "2j2b"):
        always_drop = ["eta_met", "bdt_response"]
        if r == "1j1b":
            always_drop.append("minimaxmbl")
        for sample in ("tW_DR", "tW_DS", "ttbar"):
            log.info(f"preparing to save a {sample} {r} parquet file using the files:")
            for f in qf[sample]:
                log.info(f" - {f}")
            df = iterative_selection(
                qf[sample],
                selection_for(r),
                keep_category="kinematics",
                concat=True,
                entrysteps=entrysteps,
                use_campaign_weight=use_campaign_weight,
            )
            df.drop_cols(*always_drop)
            df.drop_avoid(region=r)
            if r == "1j1b":
                df.drop_jet2()
            outname = str(out_dir / f"{sample}_{r}.parquet")
            df.to_parquet(outname, engine="pyarrow")
            log.info(f"{outname} saved")


def prepare_from_parquet(
    data_dir: str | os.PathLike,
    region: str | Region,
    nlo_method: str = "DR",
    ttbar_frac: str | float | None = None,
    weight_mean: float | None = None,
    weight_scale: float | None = None,
    scale_sum_weights: bool = True,
    test_case_size: int | None = None,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Prepare feature selection data from parquet files.

    this function requires pyarrow_.

    .. _pyarrow: https://arrow.apache.org/docs/python/

    Parameters
    ----------
    data_dir : str or os.PathLike
       directory where the parquet files live
    region : str or tdub.data.Region
       the region where we're going to select features
    nlo_method : str
       the :math:`tW` sample (``DR`` or ``DS``)
    ttbar_frac : str or float, optional
       if not ``None``, this is the fraction of :math:`t\\bar{t}`
       events to use, "auto" (the default) uses some sensible defaults
       to fit in memory: 0.70 for 2j2b and 0.60 for 2j1b.
    weight_mean : float, optional
       scale all weights such that the mean weight is this
       value. Cannot be used with ``weight_scale``.
    weight_scale : float, optional
       value to scale all weights by, cannot be used with
       ``weight_mean``.
    scale_sum_weights : bool
       scale sum of weights of signal to be sum of weights of
       background
    test_case_size : int, optional
       if we want to perform a quick test, we use a subset of the
       data, for ``test_case_size=N`` we use ``N`` events from both
       signal and background. Cannot be used with ``ttbar_frac``.

    Returns
    -------
    pandas.DataFrame
       the dataframe which contains kinematic features
    numpy.ndarray
       the labels array for the events
    numpy.ndarray
       the weights array for the events

    Examples
    --------
    >>> from tdub.features import prepare_from_parquet
    >>> df, labels, weights = prepare_from_parquet("/path/to/pq/output", "2j1b", "DR")

    """
    if weight_scale is not None and weight_mean is not None:
        raise ValueError("weight_scale and weight_mean cannot be used together")

    if ttbar_frac is not None and test_case_size is not None:
        raise ValueError("ttbar_frac and test_case_size cannot be used together")

    data_path = PosixPath(data_dir)
    if not data_path.exists():
        raise RuntimeError(f"{data_dir} doesn't exist")
    sig_file = str(data_path / f"tW_{nlo_method}_{region}.parquet")
    bkg_file = str(data_path / f"ttbar_{region}.parquet")
    sig = pd.read_parquet(sig_file, engine="pyarrow")
    bkg = pd.read_parquet(bkg_file, engine="pyarrow")
    log.info(f"sig file loaded: {sig_file}")
    log.info(f"bkg file loaded: {bkg_file}")

    sig_wsys_cols = [c for c in sig.columns.to_list() if "weight_sys" in c]
    bkg_wsys_cols = [c for c in bkg.columns.to_list() if "weight_sys" in c]
    drop_cols(sig, *sig_wsys_cols)
    drop_cols(sig, *bkg_wsys_cols)

    for c in sig.columns.to_list():
        if c not in bkg.columns.to_list():
            log.warn(f"{c} not in bkg")
    for c in bkg.columns.to_list():
        if c not in sig.columns.to_list():
            log.warn(f"{c} not in sig")

    if ttbar_frac is not None:
        if ttbar_frac == "auto":
            if region == "2j2b":
                ttbar_frac = 0.70
            elif region == "2j1b":
                ttbar_frac = 0.60
            elif region == "1j1b":
                ttbar_frac = 1.00
        if ttbar_frac < 1:
            log.info(f"sampling a fraction ({ttbar_frac}) of the background")
            bkg = bkg.sample(frac=ttbar_frac, random_state=tdub.config.RANDOM_STATE)

    if test_case_size is not None:
        if test_case_size > 5000:
            log.warn("why bother with test_case_size > 5000?")
        sig = sig.sample(n=test_case_size, random_state=tdub.config.RANDOM_STATE)
        bkg = bkg.sample(n=test_case_size, random_state=tdub.config.RANDOM_STATE)

    sig_weights = sig.pop("weight_nominal").to_numpy()
    bkg_weights = bkg.pop("weight_nominal").to_numpy()
    sig_weights[sig_weights < 0] = 0.0
    bkg_weights[bkg_weights < 0] = 0.0
    if scale_sum_weights:
        sig_weights *= bkg_weights.sum() / sig_weights.sum()
    if "weight_campaign" in sig:
        drop_cols(sig, "weight_campaign")
    if "weight_campaign" in bkg:
        drop_cols(bkg, "weight_campaign")

    sig_labels = np.ones_like(sig_weights)
    bkg_labels = np.zeros_like(bkg_weights)

    df = pd.concat([sig, bkg])
    labels = np.concatenate([sig_labels, bkg_labels])
    weights = np.concatenate([sig_weights, bkg_weights])
    gc.enable()
    del sig, bkg, sig_labels, bkg_labels, sig_weights, bkg_weights
    gc.collect()

    if weight_scale is not None:
        weights *= weight_scale
    if weight_mean is not None:
        weights *= weight_mean * len(weights) / np.sum(weights)

    return df, labels, weights

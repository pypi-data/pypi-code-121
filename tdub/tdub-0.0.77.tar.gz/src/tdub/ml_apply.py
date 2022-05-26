"""Module for applying trained models."""

from __future__ import annotations

# stdlib
import json
import logging
import os
from pathlib import PosixPath
from typing import List, Dict, Any

# external
import numpy as np
import joblib
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator

# tdub
from tdub.data import Region


log = logging.getLogger(__name__)


class BaseTrainSummary:
    """Base class for describing a completed training to apply to other data."""

    @property
    def features(self) -> list[str]:
        """Features used by the model."""
        return self._features

    @property
    def region(self) -> Region:
        """Region where the training was executed."""
        return self._region

    @property
    def selection_used(self) -> str:
        """Numexpr selection used on the trained datasets."""
        return self._selection_used

    @property
    def summary(self) -> dict[str, Any]:
        """Training summary dictionary from the training json."""
        return self._summary

    def parse_summary_json(self, summary_file: os.PathLike) -> None:
        """Parse a traning's summary json file.

        This populates the class properties with values and the
        resulting dictionary is saved to be accessible via the summary
        property. The common class properties (which all
        BaseTrainSummarys have by defition) besides `summary` are
        `features`, `region`, and `selecton_used`. This function will
        define those, so all BaseTrainSummary inheriting classes
        should call the super implementation of this method if a
        daughter implementation is necessary to add additional summary
        properties.

        Parameters
        ----------
        summary_file : os.PathLike
            The summary json file.

        """
        self._summary = json.loads(summary_file.read_text())
        self._features = self.summary["features"]
        self._region = self.summary["region"]
        self._selection_used = self.summary["selection_used"]

    def apply_to_dataframe(
        self, df: pd.DataFrame, column_name: str, do_query: bool
    ) -> None:
        """Apply trained model(s) to events in a dataframe `df`.

        All BaseTrainSummary classes must implement this function.
        """
        raise NotImplementedError("This method must be implemented")


class FoldedTrainSummary(BaseTrainSummary):
    """Provides access to the properties of a folded training.

    Parameters
    ----------
    fold_output : str
        Directory with the folded training output.

    Examples
    --------
    >>> from tdub.apply import FoldedTrainSummary
    >>> fr_1j1b = FoldedTrainSummary("/path/to/folded_training_1j1b")

    """

    def __init__(self, fold_output: str) -> None:
        """Class constructor."""
        fold_path = PosixPath(fold_output).resolve()
        self._model0 = joblib.load(fold_path / "model_fold0.joblib.gz")
        self._model1 = joblib.load(fold_path / "model_fold1.joblib.gz")
        self._model2 = joblib.load(fold_path / "model_fold2.joblib.gz")
        self.parse_summary_json(fold_path / "summary.json")

    def parse_summary_json(self, summary_file: os.PathLike) -> None:
        """Parse a training's summary json file.

        Parameters
        ----------
        summary_file : str or os.PathLike
            the summary json file

        """
        super().parse_summary_json(summary_file)
        self._folder = KFold(**(self.summary["kfold"]))

    @property
    def model0(self) -> BaseEstimator:
        """Model for the 0th fold."""
        return self._model0

    @property
    def model1(self) -> BaseEstimator:
        """Model for the 1st fold."""
        return self._model1

    @property
    def model2(self) -> BaseEstimator:
        """Model for the 2nd fold."""
        return self._model2

    @property
    def folder(self) -> KFold:
        """Folding object used during training."""
        return self._folder

    def apply_to_dataframe(
        self,
        df: pd.DataFrame,
        column_name: str = "unnamed_response",
        do_query: bool = False,
    ) -> None:
        """Apply trained models to an arbitrary dataframe.

        This function will augment the dataframe with a new column
        (with a name given by the ``column_name`` argument) if it
        doesn't already exist. If the dataframe is empty this function
        does nothing.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe to read and augment.
        column_name : str
            Name to give the BDT response variable.
        do_query : bool
            Perform a query on the dataframe to select events
            belonging to the region associated with training result;
            necessary if the dataframe hasn't been pre-filtered.

        Examples
        --------
        >>> from tdub.apply import FoldedTrainSummary
        >>> from tdub.frames import raw_dataframe
        >>> df = raw_dataframe("/path/to/file.root")
        >>> fr_1j1b = FoldedTrainSummary("/path/to/folded_training_1j1b")
        >>> fr_1j1b.apply_to_dataframe(df, do_query=True)

        """
        if df.shape[0] == 0:
            log.info("Dataframe is empty, doing nothing")
            return None

        if column_name not in df.columns:
            log.info(f"Creating {column_name} column")
            df[column_name] = -9999.0

        if do_query:
            log.info(f"applying selection filter '{self.selection_used}'")
            mask = df.eval(self.selection_used)
            X = df[self.features].to_numpy()[mask]
        else:
            X = df[self.features].to_numpy()

        if X.shape[0] == 0:
            return None

        y0 = self.model0.predict_proba(X)[:, 1]
        y1 = self.model1.predict_proba(X)[:, 1]
        y2 = self.model2.predict_proba(X)[:, 1]
        y = np.mean([y0, y1, y2], axis=0)

        if do_query:
            df.loc[mask, column_name] = y
        else:
            df[column_name] = y


class SingleTrainSummary(BaseTrainSummary):
    """Provides access to the properties of a single result.

    Parameters
    ----------
    training_output : str
        Directory containing the training result.

    Examples
    --------
    >>> from tdub.apply import SingleTrainSummary
    >>> res_1j1b = SingleTrainSummary("/path/to/some_1j1b_training_outdir")

    """

    def __init__(self, training_output: os.PathLike) -> None:
        """Class constructor."""
        training_path = PosixPath(training_output)
        self._model = joblib.load(training_path / "model.joblib.gz")
        self.parse_summary_json(training_path / "summary.json")

    @property
    def model(self) -> BaseEstimator:
        """Trained model."""
        return self._model

    def apply_to_dataframe(
        self,
        df: pd.DataFrame,
        column_name: str = "unnamed_response",
        do_query: bool = False,
    ) -> None:
        """Apply trained model to an arbitrary dataframe.

        This function will augment the dataframe with a new column
        (with a name given by the ``column_name`` argument) if it
        doesn't already exist. If the dataframe is empty this function
        does nothing.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe to read and augment.
        column_name : str
            Name to give the BDT response variable.
        do_query : bool
            Perform a query on the dataframe to select events
            belonging to the region associated with training result;
            necessary if the dataframe hasn't been pre-filtered.

        Examples
        --------
        >>> from tdub.apply import FoldedTrainSummary
        >>> from tdub.frames import raw_dataframe
        >>> df = raw_dataframe("/path/to/file.root")
        >>> sr_1j1b = SingleTrainSummary("/path/to/single_training_1j1b")
        >>> sr_1j1b.apply_to_dataframe(df, do_query=True)

        """
        if df.shape[0] == 0:
            log.info("Dataframe is empty, doing nothing")
            return None

        if column_name not in df.columns:
            log.info(f"Creating {column_name} column")
            df[column_name] = -9999.0

        if do_query:
            log.info(f"applying selection filter '{self.selection_used}'")
            mask = df.eval(self.selection_used)
            X = df[self.features].to_numpy()[mask]
        else:
            X = df[self.features].to_numpy()

        if X.shape[0] == 0:
            return None

        yhat = self.model.predict_proba(X)[:, 1]

        if do_query:
            df.loc[mask, column_name] = yhat
        else:
            df[column_name] = yhat


def build_array(summaries: list[BaseTrainSummary], df: pd.DataFrame) -> np.ndarray:
    """Get a NumPy array which is the response for all events in `df`.

    This will use the :py:func:`~BaseTrainSummary.apply_to_dataframe`
    function from the list of summaries. We query the input dataframe
    to ensure that we apply to the correct events. If the input
    dataframe is empty then an empty array is written to disk.

    Parameters
    ----------
    summaries : list(BaseTrainSummary)
        Sequence of training summaries to use.
    df : pandas.DataFrame
        Dataframe of events to use to calculate the response.

    Examples
    --------
    Using folded summaries:

    >>> from tdub.apply import FoldedTrainSummary, build_array
    >>> from tdub.frames import raw_dataframe
    >>> df = raw_dataframe("/path/to/file.root")
    >>> fr_1j1b = FoldedTrainSummary("/path/to/folded_training_1j1b")
    >>> fr_2j1b = FoldedTrainSummary("/path/to/folded_training_2j1b")
    >>> fr_2j2b = FoldedTrainSummary("/path/to/folded_training_2j2b")
    >>> res = build_array([fr_1j1b, fr_2j1b, fr_2j2b], df)

    Using single summaries:

    >>> from tdub.apply import SingleTrainSummary, build_array
    >>> from tdub.frames import raw_dataframe
    >>> df = raw_dataframe("/path/to/file.root")
    >>> sr_1j1b = SingleTrainSummary("/path/to/single_training_1j1b")
    >>> sr_2j1b = SingleTrainSummary("/path/to/single_training_2j1b")
    >>> sr_2j2b = SingleTrainSummary("/path/to/single_training_2j2b")
    >>> res = build_array([sr_1j1b, sr_2j1b, sr_2j2b], df)

    """
    if df.shape[0] == 0:
        log.info("build_array: Returning an empty array")
        return np.array([], dtype=np.float64)

    colname = "_temp_col"
    log.info(f"The {colname} column will be deleted at the end of this function")
    for trsum in summaries:
        trsum.apply_to_dataframe(df, column_name=colname, do_query=True)
    return df.pop(colname).to_numpy()

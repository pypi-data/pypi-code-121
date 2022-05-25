################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""Customized pipeline for AutoAI-Time Series which supports generating predictions when there are no
additional observations (i.e., X=None) and imputing future exogenous values using an imputer present
in the pipeline."""

import logging
import pprint
from typing import Dict, Any, List, Union

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_array

from autoai_ts_libs.transforms.imputers import AutoAITSImputer
from autoai_ts_libs.transforms.imputers import previous
from autoai_ts_libs.utils.score import Score
from autoai_ts_libs.utils.messages.messages import Messages
logger = logging.getLogger(__name__)


class TSPipeline(Pipeline):
    """Time series pipeline. Performs similar function to scikit-learn pipeline but adds support for
    predicting when there are no additional observations. Also adds functionality to manage future
    exogenous values.

    Args:
        steps (List[tuple]): List of pipeline steps, each step consists of name (string) and object.
        feature_columns (List[int], optional): List of feature column indices. Defaults to [].
        target_columns (List[int], optional): List of target column indices. Defaults to [].
        prediction_horizon (int, optional): Prediction horizon. Defaults to 1.
    """

    def __init__(
        self,
        steps: List[tuple],
        feature_columns: List[int] = [],
        target_columns: List[int] = [],
        prediction_horizon: int = 1,
        **kwargs: Dict[str, Any],
    ):
        self.target_columns = target_columns
        self.feature_columns = (
            feature_columns if feature_columns != -1 else self.target_columns
        )
        self.prediction_horizon = prediction_horizon

        self.is_exogenous_pipeline_ = set(self.target_columns) != set(
            self.feature_columns
        )

        self.future_exogenous_cache_ = None
        self.exogenous_state_ = None

        # to handle missing future exogenous we apply a model which uses previous values
        self.default_exogenous_model_ = previous(default_value=0)

        super().__init__(steps, **kwargs)

    def __setstate__(self, state):
        super().__setstate__(state)

        # exogenous version pipelines will have is_exogenous_pipeline_
        # for backward compatibility with older pipelines we need to infer parameters
        if not hasattr(self, "is_exogenous_pipeline_"):
            # anything that lacks the attribute above will be non-exogenous
            logger.info("Inferring parameters")
            try:
                targets = Score.get_target_columns(self)
                inferred_params = dict(
                    is_exogenous_pipeline_=False,
                    feature_columns=targets,
                    target_columns=targets,
                    prediction_horizon=Score.get_prediction_win(self),
                )
            except:
                logger.warning("Encounter an issue inferring parameters")
                inferred_params = dict(
                    is_exogenous_pipeline_=False,
                    feature_columns=[],
                    target_columns=[],
                    prediction_horizon=Score.get_prediction_win(self),
                )

            logger.info(pprint.pformat(inferred_params))
            for k, v in inferred_params.items():
                if not hasattr(self, k):
                    self.__setattr__(k, v)

    def _get_exogenous_indices(self) -> List[int]:
        """Simple helper function to get indices of exogenous columns.

        Returns:
            List[int]: List of exogenous indices
        """
        exogenous_indices = [
            c
            for i, c in enumerate(self.feature_columns)
            if c not in self.target_columns
        ]

        # exogenous indices are the features which are not targets

        return exogenous_indices

    def _get_future_exogenous(
        self, X: Union[np.ndarray, None], future_exogenous: Union[np.ndarray, None]
    ) -> np.ndarray:
        """Function to get the values for the future exogenous if needed.

        Args:
            X (Union[np.ndarray, None]): Any additional observations provided during predict.
            future_exogenous (Union[np.ndarray, None]): Values of future exogenous, any missing will be handled. Currently, handling
            is done by filling missing values using the last valid value for each dimension.

        Raises:
            ValueError: Raised wheen thee exogenous input contains the wrong number of columns.

        Returns:
            np.ndarray: Properly shaped future exogenous with no missing values.
        """

        exogenous_indices = self._get_exogenous_indices()

        # check future exogenous
        # check that there are no zero dimensions when not none, if so treat as none
        if future_exogenous is not None:
            if any([_ == 0 for _ in future_exogenous.shape]):
                future_exogenous = None
        # if so, set future_exogenous to None
        if future_exogenous is not None:
            # call check_array if we have proper matrix
            future_exogenous = check_array(future_exogenous, dtype=np.float64, force_all_finite=False)
            # if array is too long, we should use first avaiable rows
            if future_exogenous.shape[0] > self.prediction_horizon:
                logger.warning(
                    f"Using the first {self.prediction_horizon} rows of provided future exogenous."
                )
                future_exogenous = future_exogenous[: self.prediction_horizon, :]
            if future_exogenous.shape[1] != len(exogenous_indices):
                raise ValueError(
                    f"Provided future exogenous value must be None or have {len(exogenous_indices)} columns."
                )

        # create empty future exogenous and fill it properly
        fut_exog_new = np.NaN * np.ones(
            (self.prediction_horizon, len(exogenous_indices))
        )
        if future_exogenous is not None:
            fut_exog_new[: future_exogenous.shape[0], :] = future_exogenous

        # apply exogenous model
        if X is not None:
            exog_input = np.vstack(
                (self.exogenous_state_, X[:, exogenous_indices], fut_exog_new)
            )
        else:
            exog_input = np.vstack((self.exogenous_state_, fut_exog_new))

        logger.info(
            "Future exogenous in: {} dtype: {}".format(
                str(fut_exog_new),
                fut_exog_new.dtype if fut_exog_new is not None else "",
            )
        )

        fut_exog_out = self.default_exogenous_model_.transform(exog_input)[
            -self.prediction_horizon :, :
        ]
        self.future_exogenous_cache_ = fut_exog_out

        logger.info(
            "Future exogenous out: {} dtype: {}".format(
                str(fut_exog_out),
                fut_exog_out.dtype if fut_exog_out is not None else "",
            )
        )
        return fut_exog_out

    def _save_exogenous_state(self, X: np.ndarray):
        """Helper function to save state required to handle future exogenous values.

        State is saved to the private class attribute exogenous_state_ and has dimension
        (1, number exogenous).

        Handling of missing values in the exogenous columns is done using the transform
        method of thee class attribute default_exogenous_model_.

        Args:
            X (np.ndarray): Observations provided in the fit call.

        Raises:
            ValueError: If there are any missing values in the exogenous state after
            attempting to handle them.
        """
        exogenous_indices = self._get_exogenous_indices()
        if np.count_nonzero(np.isnan(X[-1, exogenous_indices])) > 0:
            W = self.default_exogenous_model_.transform(X[:, exogenous_indices])

            if np.count_nonzero(np.isnan(W[-1, :])) > 0:
                raise ValueError("Unable to properly save state for exogenous features")
        else:
            # no missing in exogenous state
            W = X[:, exogenous_indices]
        self.exogenous_state_ = W[-1, :]

    def _adjust_indices(self, target_columns: List[int]=[], feature_columns: List[int]=[]):
        """Adjusts feature and target columns as specified by calling the _adjust_indices function
        (if available) for all the steps in the pipeline. This is intended to be used on
        non-exogenous pipelines so that only the required columns are needed in calls to fit/predict.

        Args:
            target_columns (List[int], optional): New target columns to use. Defaults to [].
            feature_columns (List[int], optional): New feature columns to use. Defaults to [].
        """
        if self.is_exogenous_pipeline_:
            raise RuntimeError("Should not call adjust_indices on an exogenous pipeline")

        self.target_columns = target_columns
        self.feature_columns = feature_columns

        # for all the steps in pipeline call similar adjust function
        for _, s in self.steps:
            if hasattr(s, "_adjust_indices") and callable(s._adjust_indices):
                s._adjust_indices(target_columns=target_columns, feature_columns=feature_columns)

    def fit(
        self,
        X: Union[np.ndarray, None] = None,
        y: Union[np.ndarray, None] = None,
        **fit_params,
    ) -> object:
        """Provides similar functionality to the predict method on standard scikit-learn pipelines,
        but adds functionality for future exogenous. If the pipeline contains exogenous columns the
        last known valid values from the exogenous columns are retained.

        Args:
            X (Union[np.ndarray, None], optional): Input time series
            y (Union[np.ndarray, None], optional): Ignored, but passed along to pipeline fit method. Defaults to None.

        Returns:
            object: self
        """
        if self.is_exogenous_pipeline_:
            self._save_exogenous_state(X)

        return super().fit(X, y=y, **fit_params)

    def predict(
        self, X: Union[np.ndarray, None] = None, **predict_params: Dict[str, Any]
    ) -> np.ndarray:
        """Provides similar functionality to the predict method on standard scikit-learn pipelines,
        but adds functionality for future exogenous. If the pipeline contains exogenous columns
        additional processing of future exogenous will occur.
        1) If future exogenous is None, a substitute consisting of the last known values will be used
        2) If some future exogenous is provided but it is incomplete, the missing values will be
        filled using the previous values.

        Args:
            X (Union[np.ndarray, None], optional): Additional observations. Defaults to None.

        Returns:
            np.ndarray: Predictions from the pipeline.
        """
        # if we are exogenous, then we process future exogenous values
        if not "future_exogenous" in predict_params.keys():
            if self.is_exogenous_pipeline_:
                if self.steps[-1][-1]:
                    if not ("Ensembler" in type(self.steps[-1][-1]).__name__) or \
                            (("Ensembler" in type(self.steps[-1][-1]).__name__) and self.steps[-1][-1].is_future_exogenous_pipeline_):
                        logger.warning(
                            Messages.get_message(message_id='AUTOAITSLIBS0009W'))
        else:
            if self.is_exogenous_pipeline_:
                if self.steps[-1][-1]:
                    if "Ensembler" in type(self.steps[-1][-1]).__name__:
                        if not self.steps[-1][-1].is_future_exogenous_pipeline_:
                            logger.warning(
                                Messages.get_message(message_id='AUTOAITSLIBS0010W'))
            else:
                logger.warning(
                    Messages.get_message(message_id='AUTOAITSLIBS0011W'))

        if self.is_exogenous_pipeline_:
            future_exognous = self._get_future_exogenous(
                X, predict_params.pop("future_exogenous", None)
            )
            predict_params.update({"future_exogenous": future_exognous})

        return super().predict(X, **predict_params)

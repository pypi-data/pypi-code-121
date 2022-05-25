# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Calibrated model"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

from azureml._base_sdk_common._docstring_wrapper import experimental

from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import GenericFitError, GenericPredictError
from .._diagnostics.reference_codes import ReferenceCodes
from ._abstract_model_wrapper import _AbstractModelWrapper


@experimental
class CalibratedModel(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Trains a calibrated model.

    Takes a base estimator as input and trains a calibrated model.
    :param base_estimator: Base Model on which calibration has to be performed.
    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState

    Read more at:
    https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html.
    """

    def __init__(self, base_estimator, random_state=None):
        """
        Initialize Calibrated Model.

        :param base_estimator: Base Model on which calibration has to be
            performed.
        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        """
        super().__init__()
        self._train_ratio = 0.8
        self.random_state = random_state
        self.model = CalibratedClassifierCV(base_estimator=base_estimator, cv="prefit")

    def get_params(self, deep=True):
        """
        Return parameters for Calibrated Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Calibrated Model.
        """
        params = {"random_state": self.random_state}
        assert isinstance(self.model, CalibratedClassifierCV)
        params["base_estimator"] = self.model.base_estimator
        return params

    def get_model(self):
        """
        Return the sklearn Calibrated Model.

        :return: The Calibrated Model.
        :rtype: sklearn.calibration.CalibratedClassifierCV
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Calibrated Model.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: self: Returns an instance of self.
        :rtype: azureml.automl.runtime.shared.model_wrappers.CalibratedModel
        """
        arrays = [X, y]
        if "sample_weight" in kwargs:
            arrays.append(kwargs["sample_weight"])
        self.args = kwargs
        out_arrays = train_test_split(
            *arrays, train_size=self._train_ratio, random_state=self.random_state, stratify=y
        )
        X_train, X_valid, y_train, y_valid = out_arrays[:4]

        if "sample_weight" in kwargs:
            sample_weight_train, sample_weight_valid = out_arrays[4:]
        else:
            sample_weight_train = None
            sample_weight_valid = None

        try:
            # train model
            self.model.base_estimator.fit(X_train, y_train, sample_weight=sample_weight_train)
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError,
                target="CalibratedModel",
                reference_code=ReferenceCodes._CALIBRATED_MODEL_BASE_ESTIMATOR_FIT_FAILURE,
                transformer_name="CalibratedModel",
            ) from e

        # fit calibration model
        try:
            self.model.fit(X_valid, y_valid, sample_weight=sample_weight_valid)
        except ValueError as e:
            y_labels = np.unique(y)
            y_train_labels = np.unique(y_train)
            y_valid_labels = np.unique(y_valid)
            y_train_missing_labels = np.setdiff1d(y_labels, y_train_labels, assume_unique=True)
            y_valid_missing_labels = np.setdiff1d(y_labels, y_valid_labels, assume_unique=True)
            if y_train_missing_labels.shape[0] > 0 or y_valid_missing_labels.shape[0] > 0:
                raise AzureMLError.create(
                    GenericFitError,
                    target="CalibratedModel",
                    reference_code=ReferenceCodes._CALIBRATED_MODEL_FIT_SPLIT_FAILURE,
                    transformer_name=self.__class__.__name__,
                    message="Fitting calibrated model failed. Train/validation sets could not be split, even with "
                            f"stratification. - Missing train: {y_train_missing_labels} "
                            f"Missing valid: {y_valid_missing_labels}",
                ) from e
            else:
                # We don't know what happened in this case, so just re-raise with the same inner exception
                raise AzureMLError.create(
                    GenericFitError,
                    target="CalibratedModel",
                    reference_code=ReferenceCodes._CALIBRATED_MODEL_FIT_UNKNOWN_FAILURE,
                    transformer_name=self.__class__.__name__,
                ) from e
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError,
                target="CalibratedModel",
                reference_code=ReferenceCodes._CALIBRATED_MODEL_FIT_CALIBRATION_FAILURE,
                transformer_name=self.__class__.__name__,
            ) from e

        try:
            # retrain base estimator on full dataset
            self.model.base_estimator.fit(X, y, **kwargs)
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError,
                target="CalibratedModel",
                reference_code=ReferenceCodes._CALIBRATED_MODEL_FIT_RETRAIN_FAILURE,
                transformer_name=self.__class__.__name__,
            ) from e

        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)
        return self

    def predict(self, X):
        """
        Prediction function for Calibrated Model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction values from Calibrated model.
        :rtype: array
        """
        try:
            return self.model.predict(X)
        except Exception as e:
            raise AzureMLError.create(
                GenericPredictError,
                target="CalibratedModel",
                reference_code=ReferenceCodes._CALIBRATED_MODEL_PREDICT_FAILURE,
                transformer_name="CalibratedModel",
            ) from e

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Calibrated model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction proba values from Calibrated model.
        :rtype: array
        """
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise AzureMLError.create(
                GenericPredictError,
                target="CalibratedModel",
                reference_code=ReferenceCodes._CALIBRATED_MODEL_PREDICT_PROBA_FAILURE,
            ) from e

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stack ensemble"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, cast

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin, RegressorMixin, clone
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.utils.metaestimators import _BaseComposition

from azureml._base_sdk_common._docstring_wrapper import experimental

from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import GenericFitError, GenericPredictError
from .._types import CoreDataInputType
from ..score import _scoring_utilities, scoring


@experimental
class Scorer:
    """Scorer class that encapsulates our own metric computation."""

    def __init__(self, metric: str):
        """Create an AutoMLScorer for a particular metric.

        :param metric: The metric we need to calculate the score for.
        """
        self._metric = metric

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(metric='{self._metric}')"

    def __call__(self, estimator, X, y=None):
        """Return the score of the estimator.

        :param estimator: The estimator to score
        :param X: the input data to compute the score on
        :param y: the target values associate to the input
        """
        # The LogisticRegressionCV estimator transforms labels to -1 and 1 when multi_class is ovr.
        # We cannot use the original dataset class labels or sample weights here
        # and must rely on the sklearn scorer function interface.
        cv_labels = estimator.classes_
        if estimator.multi_class == "ovr":
            cv_labels = cv_labels.astype(float)
        y_pred_proba = estimator.predict_proba(X)

        scores = scoring.score_classification(
            y, y_pred_proba, [self._metric], cv_labels, cv_labels, None, None, use_binary=False, positive_label=None
        )
        return scores[self._metric]


class StackEnsembleBase(ABC, _BaseComposition):
    """StackEnsemble class. Represents a 2 layer Stacked Ensemble."""

    def __new__(cls: Type["StackEnsembleBase"], *args: Any, **kwargs: Any) -> "StackEnsembleBase":
        """
        Mark all subclasses as experimental (but with their proper names, not StackEnsembleBase).

        TODO: Remove this function once no longer experimental.
        """
        cls = experimental(cls)
        return super().__new__(cls)

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsemble.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__()
        self._base_learners = base_learners
        self._meta_learner = meta_learner
        self._training_cv_folds = training_cv_folds

    def get_params(self, deep=True):
        """
        Return parameters for StackEnsemble model.

        :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for the StackEnsemble model.
        """
        result = {
            "base_learners": self._base_learners,
            "meta_learner": self._meta_learner,
            "training_cv_folds": self._training_cv_folds,
        }

        if not deep:
            return result

        base_layer_params = super(StackEnsembleBase, self)._get_params("_base_learners", deep=True)
        result.update(base_layer_params)
        meta_params = self._meta_learner.get_params(deep=True)
        for key, value in meta_params.items():
            result["%s__%s" % ("metalearner", key)] = value

        return result

    def fit(self, X: CoreDataInputType, y: np.ndarray) -> "StackEnsembleBase":
        """
        Fit function for StackEnsemble model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        predictions = None  # type: np.ndarray

        # cache the CV split indices into a list
        cv_indices = list(self._get_cv_split_indices(X, y))

        y_out_of_fold_concat = None
        for _, test_indices in cv_indices:
            y_test = y[test_indices]
            if y_out_of_fold_concat is None:
                y_out_of_fold_concat = y_test
            else:
                y_out_of_fold_concat = np.concatenate((y_out_of_fold_concat, y_test))

        for index, (_, learner) in enumerate(self._base_learners):
            temp = None  # type: np.ndarray
            for train_indices, test_indices in cv_indices:
                if isinstance(X, pd.DataFrame):
                    X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
                else:
                    X_train, X_test = X[train_indices], X[test_indices]
                y_train, y_test = y[train_indices], y[test_indices]
                cloned_learner = clone(learner)
                try:
                    cloned_learner.fit(X_train, y_train)
                except Exception as e:
                    raise AzureMLError.create(
                        GenericFitError, target="StackEnsemble", transformer_name=self.__class__.__name__
                    ) from e

                model_predictions = self._get_base_learner_predictions(cloned_learner, X_test)

                if temp is None:
                    temp = model_predictions
                else:
                    temp = np.concatenate((temp, model_predictions))

                if len(temp.shape) == 1:
                    predictions = np.zeros((y.shape[0], 1, len(self._base_learners)))
                else:
                    predictions = np.zeros((y.shape[0], temp.shape[1], len(self._base_learners)))

            if len(temp.shape) == 1:
                # add an extra dimension so that we can reuse the predictions array
                # across multiple training types
                temp = temp[:, None]
            predictions[:, :, index] = temp

        all_out_of_fold_predictions = []
        for idx in range(len(self._base_learners)):
            # get the vertical concatenation of the out of fold predictions from the selector
            # as they were already computed during the selection phase
            model_predictions = predictions[:, :, idx]
            all_out_of_fold_predictions.append(model_predictions)

        meta_learner_training = self._horizontal_concat(all_out_of_fold_predictions)
        cloned_meta_learner = clone(self._meta_learner)
        try:
            cloned_meta_learner.fit(meta_learner_training, y_out_of_fold_concat)
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError, target="StackEnsemble", transformer_name=self.__class__.__name__
            ) from e

        final_base_learners = []
        for name, learner in self._base_learners:
            final_learner = clone(learner)
            final_learner.fit(X, y)
            final_base_learners.append((name, final_learner))

        self._base_learners = final_base_learners
        self._meta_learner = cloned_meta_learner

        return self

    def predict(self, X):
        """
        Predict function for StackEnsemble class.

        :param X: Input data.
        :return: Weighted average of predicted values.
        """
        predictions = self._get_base_learners_predictions(X)
        try:
            return self._meta_learner.predict(predictions)
        except Exception as e:
            raise AzureMLError.create(
                GenericPredictError, target="StackEnsembleBase", transformer_name=self.__class__.__name__
            ) from e

    @staticmethod
    def _horizontal_concat(predictions_list: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Concatenate multiple base learner predictions horizontally.

        Given a list of out-of-fold predictions from base learners, it concatenates these predictions
        horizontally to create one 2D matrix which will be used as training set for the meta learner.
        In case we're dealing with a classification problem, we need to drop one column out of each
        element within the input list, so that the resulting matrix is not collinear (because the sum of all class
        probabilities would be equal to 1 )
        """
        if len(predictions_list) == 0:
            return None
        preds_shape = predictions_list[0].shape
        if len(preds_shape) == 2 and preds_shape[1] > 1:
            # remove first class prediction probabilities so that the matrix isn't collinear
            predictions_list = [np.delete(pred, 0, 1) for pred in predictions_list]
        elif len(preds_shape) == 1:
            # if we end up with a single feature, we'd have a single dimensional array, so we'll need to reshape it
            # in order for SKLearn to accept it as input
            predictions_list = [pred.reshape(-1, 1) for pred in predictions_list if pred.ndim == 1]

        # now let's concatenate horizontally all the predictions
        predictions = np.hstack(predictions_list)
        return cast(np.ndarray, predictions)

    def _get_base_learners_predictions(self, X: List[np.ndarray]) -> Optional[np.ndarray]:
        predictions = [self._get_base_learner_predictions(estimator, X) for _, estimator in self._base_learners]
        return StackEnsembleBase._horizontal_concat(predictions)

    @abstractmethod
    def _get_cv_split_indices(self, X, y):
        pass

    @abstractmethod
    def _get_base_learner_predictions(self, model, X):
        pass


class StackEnsembleClassifier(StackEnsembleBase, ClassifierMixin):
    """StackEnsembleClassifier class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleClassifier.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)
        if hasattr(meta_learner, "classes_"):
            self.classes_ = meta_learner.classes_
        else:
            self.classes_ = None

    def fit(self, X: CoreDataInputType, y: np.ndarray) -> "StackEnsembleClassifier":
        """
        Fit function for StackEnsembleClassifier model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        self.classes_ = np.unique(y)
        return super().fit(X, y)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X from StackEnsemble model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from StackEnsemble model.
        """
        predictions = self._get_base_learners_predictions(X)
        try:
            result = self._meta_learner.predict_proba(predictions)
        except Exception as e:
            raise AzureMLError.create(
                GenericPredictError, target="StackEnsembleClassifier", transformer_name=self.__class__.__name__
            ) from e
        # let's make sure the meta learner predictions have same number of columns as classes
        # During AutoML training, both base learners and the meta learner can potentially see less classes than
        # what the whole dataset contains, so, we rely on padding at each layer (base learners, meta learner)
        # to have a consistent view over the classes of the dataset. The classes_ attributes from base_learners
        # and meta learner are being determined during fit time based on what were trained on, while the Stack
        # Ensemble's classes_ attribute is being set based on the entire dataset which was passed to AutoML.
        if self.classes_ is not None and hasattr(self._meta_learner, "classes_"):
            result = _scoring_utilities.pad_predictions(result, self._meta_learner.classes_, self.classes_)
        return result

    def _get_cv_split_indices(self, X, y):
        result = None
        try:
            kfold = StratifiedKFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)
        except Exception as ex:
            print("Error trying to perform StratifiedKFold split. Falling back to KFold. Exception: {}".format(ex))
            # StratifiedKFold fails when there is a single example for a given class
            # so if that happens will fallback to regular KFold
            kfold = KFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)

        return result

    def _get_base_learner_predictions(self, model, X):
        result = model.predict_proba(X)
        # let's make sure all the predictions have same number of columns
        if self.classes_ is not None and hasattr(model, "classes_"):
            result = _scoring_utilities.pad_predictions(result, model.classes_, self.classes_)
        return result


class StackEnsembleRegressor(StackEnsembleBase, RegressorMixin):
    """StackEnsembleRegressor class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleRegressor.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)

    def _get_base_learner_predictions(self, model, X):
        try:
            return model.predict(X)
        except Exception as e:
            raise AzureMLError.create(
                GenericPredictError, target="StackEnsembleRegressor", transformer_name=self.__class__.__name__
            ) from e

    def _get_cv_split_indices(self, X, y):
        kfold = KFold(n_splits=self._training_cv_folds)
        return kfold.split(X, y)

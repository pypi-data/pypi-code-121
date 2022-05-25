# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Pipeline With Y Transformations"""
from typing import cast

import numpy as np
import pandas as pd
import sklearn

from .._diagnostics.azureml_error import AzureMLError, AzureMLException
from .._diagnostics.error_definitions import GenericFitError, GenericTransformError
from .._diagnostics.reference_codes import ReferenceCodes


class PipelineWithYTransformations(sklearn.pipeline.Pipeline):
    """
    Pipeline transformer class.

    Pipeline and y_transformer are assumed to be already initialized.

    But fit could change this to allow for passing the parameters of the
    pipeline and y_transformer.

    :param pipeline: sklearn.pipeline.Pipeline object.
    :type pipeline: sklearn.pipeline.Pipeline
    :param y_trans_name: Name of y transformer.
    :type y_trans_name: string
    :param y_trans_obj: Object that computes a transformation on y values.
    :return: Object of class PipelineWithYTransformations.
    """

    def __init__(self, pipeline, y_trans_name, y_trans_obj):
        """
        Pipeline and y_transformer are assumed to be already initialized.

        But fit could change this to allow for passing the parameters of the
        pipeline and y_transformer.

        :param pipeline: sklearn.pipeline.Pipeline object.
        :type pipeline: sklearn.pipeline.Pipeline
        :param y_trans_name: Name of y transformer.
        :type y_trans_name: string
        :param y_trans_obj: Object that computes a transformation on y values.
        :return: Object of class PipelineWithYTransformations.
        """
        self.pipeline = pipeline
        self.y_transformer_name = y_trans_name
        self.y_transformer = y_trans_obj
        super().__init__(self.pipeline.steps, memory=self.pipeline.memory)
        self.steps = pipeline.__dict__.get("steps")

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of pipeline transform.
        """
        return "%s\nY_transformer(['%s', %s])" % (self.pipeline.__str__(),
                                                  self.y_transformer_name,
                                                  self.y_transformer.__str__())

    def fit(self, X, y, y_min=None, **kwargs):
        """
        Fit function for pipeline transform.

        Perform the fit_transform of y_transformer, then fit into the sklearn.pipeline.Pipeline.

        :param X: Input training data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :param kwargs: Other parameters
        :type kwargs: dict
        :return: self: Returns an instance of PipelineWithYTransformations.
        """
        try:
            if y_min is not None:
                # Regression task related Y transformers use y_min
                self.pipeline.fit(X, self.y_transformer.fit_transform(y, y_min=y_min), **kwargs)
            else:
                # Classification task transformers (e.g. LabelEncoder) do not need y_min
                self.pipeline.fit(X, self.y_transformer.fit_transform(y), **kwargs)
        except AzureMLException:
            raise
        except Exception:
            raise AzureMLError.create(
                GenericFitError, target="PipelineWithYTransformations",
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_FIT,
                transformer_name=self.__class__.__name__
            )
        return self

    def fit_predict(self, X, y, y_min=None):
        """
        Fit predict function for pipeline transform.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :return: Prediction values after performing fit.
        """
        try:
            return self.fit(X, y, y_min).predict(X)
        except AzureMLException:
            raise
        except Exception:
            raise AzureMLError.create(GenericFitError,
                                      target="PipelineWithYTransformations",
                                      reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_FIT_PREDICT,
                                      transformer_name=self.__class__.__name__
                                      )

    def get_params(self, deep=True):
        """
        Return parameters for Pipeline Transformer.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Pipeline Transformer.
        """
        return {
            "Pipeline": self.pipeline.get_params(deep),
            "y_transformer": self.y_transformer.get_params(deep),
            "y_transformer_name": self.y_transformer_name
        }

    def predict(self, X):
        """
        Prediction function for Pipeline Transformer.

        Perform the prediction of sklearn.pipeline.Pipeline, then do the inverse transform from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values from Pipeline Transformer.
        :rtype: array
        """
        try:
            return self.y_transformer.inverse_transform(self.pipeline.predict(X))
        except AzureMLException:
            raise
        except Exception:
            raise AzureMLError.create(
                GenericTransformError, target="PipelineWithYTransformations",
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_PREDICT,
                transformer_name=self.__class__.__name__
            )

    def predict_proba(self, X):
        """
        Prediction probability function for Pipeline Transformer with classes.

        Perform prediction and obtain probability using the sklearn.pipeline.Pipeline, then do the inverse transform
        from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction probability values from Pipeline Transformer for each class (column name). The shape of
        the returned data frame is (n_samples, n_classes). Each row corresponds to the row from the input X.
        Column name is the class name and column entry is the probability.
        :rtype: pandas.DataFrame
        """
        try:
            return pd.DataFrame(self.pipeline.predict_proba(X), columns=self.classes_)
        except AzureMLException:
            raise
        except Exception:
            raise AzureMLError.create(
                GenericTransformError,
                target="PipelineWithYTransformations.predict_proba",
                transformer_name=self.__class__.__name__,
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_PREDICT_PROBA
            )

    @ property
    def classes_(self) -> np.ndarray:
        """
        LabelEncoder could have potentially seen more classes than the underlying pipeline as we `fit` the
        LabelEncoder on full data whereas, the underlying pipeline is `fit` only on train data.

        Override the classes_ attribute of the model so that we can return only those classes that are seen by
        the fitted_pipeline.
        :return: Set of classes the pipeline has seen.
        """
        return cast(np.ndarray, self.y_transformer.inverse_transform(self.pipeline.classes_))

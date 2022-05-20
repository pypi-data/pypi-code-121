# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module includes Learner regressors. The regressors inherit from the AbstractRegressor. The instance methods
could wrap the sklearn methods or any other packages. The call to Learner regressors are prefixed by learner\_.
This reduces the possibility of shadowing function calls to the external packages."""

import abc
import sys
import warnings
import logging
import numpy as np
from sklearn.linear_model import SGDRegressor, HuberRegressor, LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.ensemble import ExtraTreesRegressor, BaggingRegressor
from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_validate

from learner.utilities.progress_bar import GridSearchCVProgressBar


class AbstractRegressor:

    __metaclass__ = abc.ABCMeta

    def __init__(self):  # pragma: no cover
        self.mdl = None

    @staticmethod
    def learner_fit(X, y, mdl):  # pragma: no cover
        pass

    @staticmethod
    def learner_cross_validation(X, y, mdl, kfold_params, options):  # pragma: no cover
        pass

    @staticmethod
    def learner_grid_search(X, y, mdl, kfold_params, options):  # pragma: no cover
        pass

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass


class RegressorHandler(AbstractRegressor):

    @abc.abstractmethod
    def __init__(self):
        super(AbstractRegressor, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, mdl):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_fit(X, y, mdl)
        except AttributeError:
            return StandardRegressors.learner_fit(X, y, mdl)

    @staticmethod
    def learner_cross_validation(X, y, mdl, kfold_params, options):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_cross_validation(X, y, mdl, kfold_params, options)
        except AttributeError:
            return StandardRegressors.learner_cross_validation(X, y, mdl, kfold_params, options)

    @staticmethod
    def learner_grid_search(X, y, mdl, kfold_params, options):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_grid_search(X, y, mdl, kfold_params, options)
        except AttributeError:
            return StandardRegressors.learner_grid_search(X, y, mdl, kfold_params, options)

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict(X, mdl, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardRegressors.learner_predict(X, mdl, carry_data, full_data, cols_to_carry)


class StandardRegressors(AbstractRegressor):
    """A class for all standard regressors. The standard regressors are the ones that have "fit", "predict",
    and "predict_proba" methods and a few other features"""

    def __init__(self):
        super(AbstractRegressor, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, mdl):
        """Train a regressor using the features (X) and the target y. Instantiation of the regressor object
            (sklearn's regressor) occurs here. The function return the regressor object

        :param X: the features for training
        :param y: the target column
        :param mdl: an item in the Learner models_dict
        :return: the regressor object that holds the trained model
        """
        logging.info("Fitting a %s model...", mdl["type"])
        model = getattr(sys.modules[__name__], mdl["type"])(**mdl["params"])
        model.fit(X, y)
        # if the log level is debug, we log all the attributes
        logging.debug(vars(model))
        return model

    @staticmethod
    def learner_cross_validation(X, y, mdl, kfold_params, options):
        """Perform a kfold cross validation, report the average score and return the trained model.

        :param X: the features for training
        :param y: the target column
        :param mdl: an item in the Learner models_dict
        :param kfold_params: the parameters for kfold cross validation
        :param options: other options for doing a cross_validation
        :return: the regressor object that holds the trained model
        """
        logging.info("Performing cross_validation for a %s model...", mdl["type"])

        model = getattr(sys.modules[__name__], mdl["type"])(**mdl["params"])
        kf = KFold(**kfold_params)

        options["return_estimator"] = True
        cv_results = cross_validate(model, X, y=y, cv=kf, **options)
        if options.get("return_train_score", False):
            for score_type, score_values in cv_results.items():
                # the train scores keys start with train_. If we pass a list, it will contain the name of the metric.
                # If we pass nothing, it will be train_score
                if score_type.startswith("train_"):
                    avg_train_score = np.mean(score_values)
                    logging.info(f"The {score_type}s are {score_values} with average {avg_train_score}")

        avg_test_score = 0
        test_scores = 0
        # the test scores keys start with test_. If we pass a list, it will contain the name of the metric. If we
        # pass nothing, it will be test_score
        for score_type, score_values in cv_results.items():
            if score_type.startswith("test_"):
                test_scores = score_values
                avg_test_score = np.mean(cv_results[score_type])
                logging.info(f"The {score_type}s are {test_scores} with average {avg_test_score}")

        mdl["cv_score"] = avg_test_score
        return cv_results["estimator"][np.argmax(test_scores)]

    @staticmethod
    def learner_grid_search(X, y, mdl, kfold_params, options):
        """Perform an exhaustive grid search to find the best model

        :param X: the features for training
        :param y: the target column
        :param mdl: an item in the Learner models_dict
        :param kfold_params: the parameters for kfold cross validation
        :param options: the input parameters for performing the grid_search
        :return: the best model
        """
        logging.info("Performing GridSearch for a %s model...", mdl["type"])
        model = getattr(sys.modules[__name__], mdl["type"])(**mdl["params"])
        kf = KFold(**kfold_params)

        try:
            verbose = options["verbose"]
            if verbose > 0:  # pragma: no cover
                gs = GridSearchCV(model, mdl["params"], cv=kf, **options)
            else:  # pragma: no cover
                gs = GridSearchCVProgressBar(model, mdl["params"], cv=kf, **options)
        except KeyError:
            gs = GridSearchCVProgressBar(model, mdl["params"], cv=kf, **options)

        gs.fit(X, y)

        mdl["best_params"] = gs.best_params_
        logging.info("Best parameters are: %s", mdl["best_params"])
        logging.info("Best score is %f", gs.best_score_)
        return gs.best_estimator_

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        """Make predictions using the trained model. In some situations, learner needs to save the predictions according to
        some identifiers (e.g. id_columns). In those situations, the functions also returns the data that the user has
        requested.

        :param X: the features to use for making predictions (obviously this should match with the features used for training)
        :param mdl: an item in the Learner models_dict
        :param carry_data: a flag to identify if the some selected data must be returned.
        :param full_data: the data set that contains the full data set. The selection is performed on this data set.
        :param cols_to_carry: the cols to select from the full data and return (this is usually the id_cols)
        :return: The prediction or the prediction along the selected columns

        Note: The reason for passing the full data is that the feature matrix usually does not contain id information.
        """
        logging.info("Making predictions using the %s model...", mdl["type"])
        if carry_data:
            if full_data is None:
                warnings.warn("carry_data was set true but no data was passed, will not return any data...", Warning)
            if cols_to_carry is None:
                warnings.warn("carry_data was set true but no cols_to_carry was passed, will not return any data...", Warning)
            if full_data is not None and cols_to_carry:
                return mdl["model"].predict(X), full_data[cols_to_carry]
        return mdl["model"].predict(X), None

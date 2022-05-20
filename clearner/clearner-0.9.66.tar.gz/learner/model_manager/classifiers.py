# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module includes Learner classifiers. The classifiers inherit from the AbstractClassifiers. The instance methods
could wrap the sklearn methods or any other packages. The call to Learner classifiers are prefixed by learner\_.
This reduces the possibility of shadowing function calls to the external packages."""

import abc
import sys
import warnings
import logging
import numpy as np
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier, BaggingClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.neural_network import MLPClassifier
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_validate

from learner.utilities.progress_bar import GridSearchCVProgressBar


class AbstractClassifier:

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

    @staticmethod
    def learner_predict_proba(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass


class ClassifierHandler(AbstractClassifier):

    @abc.abstractmethod
    def __init__(self):
        super(AbstractClassifier, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, mdl):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_fit(X, y, mdl)
        except AttributeError:
            return StandardClassifiers.learner_fit(X, y, mdl)

    @staticmethod
    def learner_cross_validation(X, y, mdl, kfold_params, options):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_cross_validation(X, y, mdl, kfold_params, options)
        except AttributeError:
            return StandardClassifiers.learner_cross_validation(X, y, mdl, kfold_params, options)

    @staticmethod
    def learner_grid_search(X, y, mdl, kfold_params, options):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_grid_search(X, y, mdl, kfold_params, options)
        except AttributeError:
            return StandardClassifiers.learner_grid_search(X, y, mdl, kfold_params, options)

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict(X, mdl, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardClassifiers.learner_predict(X, mdl, carry_data, full_data, cols_to_carry)

    @staticmethod
    def learner_predict_proba(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict_proba(X, mdl, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardClassifiers.learner_predict_proba(X, mdl, carry_data, full_data, cols_to_carry)


class StandardClassifiers(AbstractClassifier):
    """A class for all standard classifiers. The standard classifiers are the ones that have "fit", "predict",
    and "predict_proba" methods and a few other features"""

    def __init__(self):
        super(AbstractClassifier, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, mdl):
        """Train a classifiers using the features (X) and the target y. Instantiation of the classifier object
            (sklearn's classifier) occurs here. The function return the classifier object

        :param X: the features for training
        :param y: the target column
        :param mdl: an item in the models_dicts
        :return: the classifiers object that contains the trained model
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
        :param mdl: an item in the models_dicts
        :param kfold_params: the parameters for kfold cross validation
        :param options: other options for doing a cross_validation
        :return: the classifiers object that contains the trained model
        """
        logging.info("Performing cross_validation for a %s model...", mdl["type"])

        model = getattr(sys.modules[__name__], mdl["type"])(**mdl["params"])
        skf = StratifiedKFold(**kfold_params)

        options["return_estimator"] = True
        cv_results = cross_validate(model, X, y=y, cv=skf, **options)
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
        """Perform an exhaustive grid search to find the best model.

        :param X: the features for training
        :param y: the target column
        :param mdl: an item in the Learner models_dict
        :param kfold_params: the parameters for kfold cross validation
        :param options: the input parameters for performing the grid_search
        :return: the best model
        """
        logging.info("Performing GridSearch for a %s model...", mdl["type"])
        model = getattr(sys.modules[__name__], mdl["type"])(**mdl["params"])
        skf = StratifiedKFold(**kfold_params)
        try:
            verbose = options["verbose"]
            if verbose > 0:  # pragma: no cover
                gs = GridSearchCV(model, mdl["params"], cv=skf, **options)
            else:  # pragma: no cover
                gs = GridSearchCVProgressBar(model, mdl["params"], cv=skf, **options)
        except KeyError:
            gs = GridSearchCVProgressBar(model, mdl["params"], cv=skf, **options)

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

    @staticmethod
    def learner_predict_proba(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        """Predict the probabilities using the trained model. In some situations, learner needs to save the predictions
         according to some identifiers (e.g. id_columns). In those situations, the functions also return the data that
         the user has requested.

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
                if len(mdl["model"].classes_) == 2:
                    return mdl["model"].predict_proba(X)[:, 1], full_data[cols_to_carry]
                else:
                    return mdl["model"].predict_proba(X), full_data[cols_to_carry]
        if len(mdl["model"].classes_) == 2:
            return mdl["model"].predict_proba(X)[:, 1], None
        return mdl["model"].predict_proba(X), None

# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module to compute the prediction scores using various metrics."""

import sys
import logging
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, average_precision_score, precision_score, recall_score
from sklearn.metrics import roc_auc_score, brier_score_loss, classification_report, confusion_matrix, fbeta_score
from sklearn.metrics import hamming_loss, jaccard_similarity_score, log_loss, matthews_corrcoef, precision_recall_curve
from sklearn.metrics import precision_recall_fscore_support, zero_one_loss
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, mean_squared_log_error
from sklearn.metrics import median_absolute_error, r2_score

from learner.model_manager.scorers import root_mean_squared_error
from learner.data_worker.data_loader import get_data
from learner.configuration.supported_items import SUPPORTED_SCORE_TYPES
from learner.configuration.configuration import Configuration
from learner.data_worker.data_processor import delete_keys_from_dict


class BaseScorer:
    """Score the prediction results against target col in test data"""

    def __init__(self, conf, models_dict, processor=None):
        """Initialize a BaseScorer instance using a conf object and models_dict.

        :param conf: configuration object
        :param models_dict: learner models dictionary
        """
        self._conf = conf
        self._models_dict = models_dict
        self._processor = processor
        self._y_true = self.get_y_true()

    @property
    def conf(self):
        return self._conf

    @property
    def models_dict(self):
        return self._models_dict

    @property
    def y_true(self):
        return self._y_true

    def get_y_true(self):
        """Load the target col from the test data.

        :return y_true: target col along with the join columns
        """
        logging.info("Loading target col from the validation data...")
        y_true = get_data(self._conf.data.validation_location,
                          manifest_file=self._conf.data.manifest,
                          format=self._conf.data.validation_format,
                          sep=self._conf.data.validation_delimiter,
                          nrows=self._conf.data.validation_nrows,
                          header=self._conf.data.validation_header,
                          usecols=[self._conf.column.target_col] + self.conf.data.validation_join_cols)

        # if we need to score the log transformed values, we do the transformation here
        if self.conf.process.log_transform_target_activate and not self.conf.process.log_transform_target_score_actuals:
            from learner.data_worker.data_processor import log_transform
            y_true = log_transform(data=y_true, params=self._conf.process.log_transform_target_params, cols=[self._conf.column.target_col])
        # in case target column was label encoded, use the trained label encoder in the processor object to
        # label encode y_true
        if self._processor and self._conf.process.label_encode_target:
            self._processor.handle_label_encoding(data=y_true, cols=[self._conf.column.target_col])
        return y_true

    def scoring_handler(self, score_type, y_true, y_pred, params):
        """Construct the call to appropriate methods to score the predictions.

        :param score_type: the metric for computing the score
        :param y_true: a dataframe containing the true values
        :param y_pred: the estimated target
        :param params: additional parameters to pass to the scoring function
        :return: the computed score
        """
        # this method accepts numpy arrays and pandas dataframe but we convert np arrays or pd series to pd dataframe
        if isinstance(y_true, np.ndarray) or isinstance(y_true, pd.Series):
            y_true = pd.DataFrame(data=y_true)
        if isinstance(y_pred, np.ndarray) or isinstance(y_pred, pd.Series):
            y_pred = pd.DataFrame(data=y_pred)

        # this is number of items before removing nulls
        before_cnt = y_true.shape[0]

        # We remove any missing values. y_pred should not have any but we check it just to be sure
        with warnings.catch_warnings():
            # this operations raises a warning and we want to suppress it
            warnings.simplefilter("ignore")
            y_true = y_true[y_true.notna().any(1) & y_pred.notna().any(1)]
            y_pred = y_pred[y_true.notna().any(1) & y_pred.notna().any(1)]

        # this is number of items after removing nulls
        after_cnt = y_true.shape[0]
        removed_cnt = before_cnt - after_cnt
        if removed_cnt > 0:
            warnings.warn(f"There were {removed_cnt} missing values in the data when scoring.", UserWarning)
        # handle custom scores first
        if params and "file" in params:
            params_copy = params.copy()
            delete_keys_from_dict(params_copy, ["file", "function"])
            return params["function"](y_true, y_pred, **params_copy)
        try:
            return getattr(sys.modules[__name__], score_type+"_score")(y_true, y_pred, **params)
        except AttributeError:
            return getattr(sys.modules[__name__], score_type)(y_true, y_pred, **params)


class ClassifierScorer(BaseScorer):
    def __init__(self, conf, models_dict, processor=None):
        """Initialize a ClassifierScorer instance using a conf object and models_dict.

        :param conf: configuration object
        :param models_dict: learner models dictionary
        """
        super().__init__(conf, models_dict, processor)

        # pandas dataframe to hold the prediction for class and probabilities
        self._pred_class = None
        self._pred_proba = None
        # these will hold the column names for class and proba
        self._proba_col_names = None
        self._class_col_names = None

    @property
    def pred_class(self):
        return self._pred_class

    @property
    def pred_proba(self):
        return self._pred_proba

    def load_pred_class(self, mdl, filename):
        """Load prediction class from the prediction file.

        :param mdl: a models_dict item
        :param filename: the full path to the prediction file
        :return: None
        """
        logging.info("Loading prediction classes from the output file...")
        if self._conf.data.validation_prediction_type == "all":
            self._class_col_names = list(filter(lambda x: x.startswith('_class_'), mdl["validation_pred_cols"]))
        else:
            self._class_col_names = list(mdl["validation_pred_cols"])

        self._pred_class = get_data(filename,
                                    manifest_file=None,
                                    usecols=self._class_col_names + self.conf.data.validation_join_cols)

    def load_pred_proba(self, mdl, filename):
        """Load prediction probability from the prediction file.

        :param mdl: a models_dict item
        :param filename: the full path to the prediction file
        :return: None
        """
        logging.info("Loading prediction probabilities from the output file...")
        if self._conf.data.validation_prediction_type == "all":
            self._proba_col_names = list(filter(lambda x: x.startswith('_proba_'), mdl["validation_pred_cols"]))
        else:
            self._proba_col_names = list(mdl["validation_pred_cols"])

        self._pred_proba = get_data(filename,
                                    manifest_file=None,
                                    usecols=self._proba_col_names + self.conf.data.validation_join_cols)

    def update_true_and_pred(self, pred, col_name):
        """In situations where the order of data in the prediction dataset and test data are different, we need to
        merge these two data on some columns to ensure the score values are valid. This method handles that. If there
        are some id columns to merge these two datasets, it merges them , and updates the prediction and true values.
        It accepts the prediction dataframe and a list of column name; if score_id_cols is empty, simply return the
        prediction dataframe and y_true with only target column for scoring. If score_id_cols is not empty,
        merge the prediction dataframe and y_true dataframe on score_id_cols, then return the prediction cols and
        target column from this merged dataset to be the prediction and target values. This handles the situations in
        which the order of prediction and target datasets are different. This is typically the case when we have
        segmentation.

        :param pred: the prediction dataframe. This can have multiple columns.
        :param col_name: the name of the columns that contain prediction values/
        :return: the updated prediction dataset (updated order) and the target column (possibly with updated order)
        """
        if not self.conf.data.validation_join_cols:
            return pred[col_name], self._y_true[self._conf.column.target_col]

        df = pred.merge(self._y_true, on=self.conf.data.validation_join_cols, how="inner")

        y_true = df[self._conf.column.target_col]
        pred = df[col_name]

        return pred, y_true

    def score(self):
        """The main function to compute the scores for the predictions generated by all models.

        :return: None
        """
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            logging.info("Score the predictions for model %s", tag)
            filename = mdl["path"] + self._conf.workspace.name + \
                "_validation_" + str(tag) + str(self._conf.sep_timetag) + ".csv"

            self._pred_class = None
            self._pred_proba = None

            model_score_dict = self.get_model_score_dict(mdl, filename)
            for score_type, score in model_score_dict.items():
                logging.info("%s model's %s score = %s", tag, score_type, score)

    def get_model_score_dict(self, mdl, filename):
        """Make the call to the appropriate functions to calculate all requested scores for a model.

        :param mdl: a models_dict item
        :param filename: the full path to the prediction file
        :return: mode_score_dict that contains the score types and their corresponding values
        """
        model_score_dict = {}
        for score_type, params in self._conf.data.validation_score_types.items():

            if SUPPORTED_SCORE_TYPES[self._conf.engine][score_type] == "class":
                if self._pred_class is None:
                    self.load_pred_class(mdl, filename)
                    self._pred_class, y_true = self.update_true_and_pred(self._pred_class, self._class_col_names)

                model_score_dict[score_type] = self.scoring_handler(score_type, y_true, self._pred_class, params)

            if SUPPORTED_SCORE_TYPES[self._conf.engine][score_type] == "proba":
                if self._pred_proba is None:
                    self.load_pred_proba(mdl, filename)
                    self._pred_proba, y_true = self.update_true_and_pred(self._pred_proba, self._proba_col_names)

                model_score_dict[score_type] = self.scoring_handler(score_type, y_true, self._pred_proba, params)

        return model_score_dict


class RegressorScorer(BaseScorer):
    def __init__(self, conf: Configuration, models_dict, processor=None):
        """Initialize a RegressorScorer instance using a conf object and models_dict.

        :param conf: configuration object
        :param models_dict: learner models dictionary
        """
        super().__init__(conf, models_dict, processor)
        self._pred = None

    @property
    def pred(self):
        return self._pred

    def load_pred(self, filename):
        """Load prediction class from the prediction file

        :param filename: the full path to the prediction file
        :return: None
        """
        logging.info("Loading prediction column from the output file...")

        self._pred = get_data(filename,
                              manifest_file=None,
                              usecols=[self._conf.data.validation_column_name] + self.conf.data.validation_join_cols)

    def update_true_and_pred(self):
        """In situations where the order of data in the prediction dataset and test data are different, we need to
        merge these two data on some columns to ensure the score values are valid. This method handles that. If there
        are some id columns to merge these two datasets, it merges them , and updates the prediction and true values.

        :return: None
        """
        if not self.conf.data.validation_join_cols:
            return
        df = self._pred.merge(self._y_true, on=self.conf.data.validation_join_cols, how="inner")

        self._y_true = df[self._conf.column.target_col]
        self._pred = df[[self._conf.data.validation_column_name]]

    def score(self):
        """The main function to compute the scores for the predictions generated by all models

        :return: None
        """
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            logging.info("Score the predictions for model %s", tag)
            filename = mdl["path"] + self._conf.workspace.name + \
                "_validation_" + str(tag) + str(self._conf.sep_timetag) + ".csv"

            self._pred = None

            model_score_dict = self.get_model_score_dict(filename)
            for score_type, score in model_score_dict.items():
                logging.info("%s model's %s score = %s", tag, score_type, score)

    def get_model_score_dict(self, filename):
        """Make the call to the appropriate functions to calculate all requested scores for a model.

        :param filename: the full path to the prediction file
        :return: mode_score_dict that contains the score types and their corresponding values
        """
        model_score_dict = {}
        for score_type, params in self._conf.data.validation_score_types.items():

            if self._pred is None:
                self.load_pred(filename)
                self.update_true_and_pred()
            model_score_dict[score_type] = self.scoring_handler(score_type, self._y_true, self._pred, params)

        return model_score_dict


class DeepClassifierScorer(BaseScorer):
    """The scorer class for the image_classifier engine. In image_classifier engine, scoring the predictions happens as
    we iterate through the validation data. This class is provided with y_true and the probabilities. It then uses
    those values and the user input to compute the scores. This class also updates the "metrics" dictionary as it
     computes he scores so it could later be used to log the numbers."""
    def __init__(self, conf: Configuration, models_dict, y_true, pred_proba, metrics=dict):
        """Initialize a ImageClassifierScorer using the input parameters.

        :param conf: a conf object
        :param models_dict: the models dict. This is set to None and is only used to be passed to the parent class.
        :param y_true: a numpy array that contains the y true.
        :param pred_proba: a numpy array that contains the probabilities of the predictions for each class.
        :param metrics: a dictionary that contains the metrics for each epoch
        """
        self._y_true = y_true
        super().__init__(conf, models_dict)
        self._pred_class = self.get_pred_class(pred_proba)
        self._pred_proba = self.update_pred_proba(pred_proba)
        self.metrics = metrics

    def get_y_true(self):
        """Convert y_true to a pandas series.

        :return: a pandas series created from the y_true numpy array.
        """
        y_true = pd.Series(data=self._y_true, name="y_true")

        # in case target column was label encoded, use the trained label encoder in the processor object to
        # label encode y_true
        if self._processor and self._conf.process.label_encode_target:
            self._processor.handle_label_encoding(data=y_true, cols=[self._conf.column.target_col])

        return y_true

    def update_pred_proba(self, pred_proba):
        """Create a pandas dataframe from the pred_proba numpy array. If we are doing a binary classification (two
        columns), take a second column (the probability of class 1)

        :param pred_proba: a numpy array containing the probability of predictions.
        :return: a pandas dataframe created using the pred_proba numpy array
        """
        pred_proba = pd.DataFrame(pred_proba)
        if pred_proba.shape[1] == 2:
            return pred_proba.iloc[:, 1]
        return pred_proba

    def get_pred_class(self, pred_proba):
        """Use the probabilities to get the predicted class. The predicted class is the index that has the highest
        probability (argmax)

        :param pred_proba: a numpy array containing the probability of predictions.
        :return: a numpy array contaning the predicted class/
        """
        return np.argmax(pred_proba, 1)

    def score(self):
        """The main function to compute the scores for the predictions generated by the model. Here, we first call
        get_model_score_dict to build a dictionary that contains the score types and their corresponding score. We then
        use that dictionary to update the metrics dictionary. That dictionary is then used by other classes (callbacks)
        to print the scores.

        :return: None
        """
        model_score_dict = self.get_model_score_dict()
        for score_type, score in model_score_dict.items():
            self.metrics[score_type] = score

    def get_model_score_dict(self):
        """Make the call to the appropriate functions to calculate all requested scores for a model.

        :return: mode_score_dict that contains the score types and their corresponding values
        """
        model_score_dict = {}
        for score_type, params in self._conf.data.validation_score_types.items():

            if SUPPORTED_SCORE_TYPES[self._conf.engine][score_type] == "class":
                model_score_dict[score_type] = self.scoring_handler(score_type, self._y_true, self._pred_class, params)

            if SUPPORTED_SCORE_TYPES[self._conf.engine][score_type] == "proba":
                model_score_dict[score_type] = self.scoring_handler(score_type, self._y_true, self._pred_proba, params)

        return model_score_dict


class DeepRegressorScorer(BaseScorer):
    """The scorer class for the deep_regressor engine. In deep_regressor engine, scoring the predictions happens as
    we iterate through the validation data. This class is provided with y_true and the predictions. It then uses
    those values and the user input to compute the scores. This class also updates the "metrics" dictionary as it
    computes the scores so it could later be used to log the numbers."""
    def __init__(self, conf: Configuration, models_dict, y_true, pred, metrics=dict):
        """Initialize a DeepRegressorScorer using the input parameters.

        :param conf: a conf object
        :param models_dict: the models dict. This is set to None and is only used to be passed to the parent class.
        :param y_true: a numpy array that contains the y true.
        :param pred: a numpy array that contains the probabilities of the predictions for each class.
        :param metrics: a dictionary that contains the metrics for each epoch
        """
        self._y_true = y_true
        super().__init__(conf, models_dict)
        self._pred = self.update_pred(pred)
        self.metrics = metrics

    def get_y_true(self):
        """Convert y_true to a pandas series. This method does a few other things as well. If we had log tranformed the
        target and we need to score the actuals, it does the exponential transformation.

        :return: a pandas series created from the y_true numpy array.
        """
        y_true = pd.DataFrame(data=self._y_true, columns=["y_true"])
        # if we need to score the actual values, we do the transformation here
        if self.conf.process.log_transform_target_activate and self.conf.process.log_transform_target_score_actuals:
            from learner.data_worker.data_processor import DataProcessor
            y_true = DataProcessor.exponential_transform(y_true,
                                                         params=[{"activate": True,
                                                                  "power": self.conf.process.log_transform_target_base,
                                                                  "col": "y_true",
                                                                  "name": "y_true",
                                                                  "shift": -self.conf.process.log_transform_target_shift}],
                                                         cols=["y_true"])

        return y_true

    def update_pred(self, pred):
        """Create a pandas dataframe from the pred numpy array. This method does a few other things as well. If we had log tranformed the
        target and we need to score the actuals, it does the exponential transformation.

        :param pred: a numpy array containing the probability of predictions.
        :return: a pandas dataframe created using the pred_proba numpy array
        """
        pred = pd.DataFrame(pred, columns=["pred"])
        if self.conf.process.log_transform_target_activate and self.conf.process.log_transform_target_score_actuals:
            from learner.data_worker.data_processor import DataProcessor
            pred = DataProcessor.exponential_transform(pred,
                                                       params=[{"activate": True,
                                                                "power": self.conf.process.log_transform_target_base,
                                                                "col": "pred",
                                                                "name": "pred",
                                                                "shift": -self.conf.process.log_transform_target_shift}],
                                                       cols=["pred"])

        return pred

    def score(self):
        """The main function to compute the scores for the predictions generated by the model. Here, we first call
        get_model_score_dict to build a dictionary that contains the score types and their corresponding score. We then
        use that dictionary to update the metrics dictionary. That dictionary is then used by other classes (callbacks)
        to print the scores.

        :return: None
        """
        model_score_dict = self.get_model_score_dict()
        for score_type, score in model_score_dict.items():
            self.metrics[score_type] = score

    def get_model_score_dict(self):
        """Make the call to the appropriate functions to calculate all requested scores for a model.

        :return: mode_score_dict that contains the score types and their corresponding values
        """
        model_score_dict = {}
        for score_type, params in self._conf.data.validation_score_types.items():

            model_score_dict[score_type] = self.scoring_handler(score_type, self._y_true, self._pred, params)

        return model_score_dict

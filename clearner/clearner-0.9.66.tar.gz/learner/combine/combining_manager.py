# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for combining the predictions of multiple models and creating an ensemble model."""
import os
import logging

from scipy import stats
import pandas as pd
import numpy as np
import pickle

from learner.model_manager.scoring_manager import BaseScorer
from learner.data_worker.data_loader import get_data
from learner.configuration.configuration import Configuration
from learner.model_manager.prediction_manager import BasePredictor
from learner.model_manager.scoring_manager import RegressorScorer, ClassifierScorer
from learner.utilities.templates import PRED_PATH, SAVE_MODEL_PATH


class MeanRegressorCombiner:
    """This class handles combining the regression models. In regression models, only one column is needed for
    predictions but in classification model, multiple columns may be needed for predictions (multiclass classification).
    As such, two different classes handle these models.
    """
    def __init__(self, conf: Configuration, models_dict, sep_timetag, data_type):
        """Initialize an instance of RegressorCombiner using a conf object, models_dict, and sep_timetag.

        :param conf: an instance of the Configuration class
        :param models_dict: learner's models dictionary. This dictionary contains the information related to all models.
        :param sep_timetag: separator plus timetag or nothing (if we shouldn't use the timetag in the output files)
        :param data_type: the data type, it can be "validation" or "test"
        """
        self._conf = conf
        self._models_dict = models_dict
        self._sep_timetag = sep_timetag
        # this will hold the id_cols df if defined
        self._id_cols = None
        # this holds all the prediction data
        self._pred = pd.DataFrame()
        self.data_type = data_type
        self.dtype_sep = f"_{self.data_type}_"
        self.column_name = getattr(self._conf.data, f"{self.data_type}_column_name")
        self.add_timetag = getattr(self.conf.data, f"{self.data_type}_add_timetag")

    @property
    def conf(self):
        return self._conf

    @property
    def models_dict(self):
        return self._models_dict

    @property
    def sep_timetag(self):
        return self._sep_timetag

    @property
    def pred(self):
        return self._pred

    def combine(self):
        """Loop through each model in models_dict, load the prediction (and id) columns, and then combine the
        predictions. After than, write the predictions to disk and score them if requested.

        :return: None
        """
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            logging.info("Loading the predictions for model %s", tag)
            filename = PRED_PATH.format(
                path=mdl["path"],
                output_name=self._conf.workspace.name,
                dtype_sep=self.dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag)
            )
            if self._id_cols is None:
                self.load_id_cols(filename)

            pred = self.load_pred(tag, filename)
            self._pred = pd.concat([self._pred, pred], axis=1)

        # compute the average of all predictions
        if self.conf.combine.mean_type == "arithmetic":
            self._pred[self.column_name] = self._pred.mean(axis=1)
        # if the mean type is not arithmetic, it's geometric
        else:
            self._pred[self.column_name] = stats.gmean(self.pred, axis=1)

        combine_dict = self.get_mean_combine_dict()
        predictor = BasePredictor(None, self._conf)
        predictor.write_predictions(next(iter(combine_dict)),
                                    self._pred[self.column_name],
                                    data_type=self.data_type,
                                    data=self._id_cols,
                                    models_dict=combine_dict,
                                    add_timetag=self.add_timetag)

        # we can score the combined model if requested
        if self.data_type == "validation" and self._conf.data.validation_score_activate:
            scorer = RegressorScorer(self._conf, combine_dict)
            scorer.score()

    def load_id_cols(self, filename):
        """Load the id columns from one of the prediction files. This method should be called once because the id
        columns should be identical for all models.

        :param filename: the path to the output (prediction file)
        :return: None
        """
        if self._conf.column.id_cols:
            self._id_cols = get_data(filename,
                                     manifest_file=None,
                                     usecols=self._conf.column.id_cols)

    def load_pred(self, tag, filename):
        """Load the predictions for a single model. After the data is loaded, rename the prediction column to be the
        model tag.

        :param tag: the model tag (this is used for renaming the prediction column)
        :param filename: the path to the prediction file
        :return: a pandas dataframe containing the prediction data
        """
        logging.info("Loading prediction column from the output file...")

        pred = get_data(filename,
                        manifest_file=None,
                        usecols=[self.column_name]).rename(columns={self.column_name: tag})
        return pred

    def get_mean_combine_dict(self):
        """Construct a models_dict items for mean_combine model. The models_dict for the combined models is constructed
        here instead of configuration module because this model cannot be loaded, etc.

        :return: A models_dict with the tag "mean_combine".
        """
        combine_dict = {}
        tag = f"mean_combine"
        combine_dict[tag] = {}

        directory_path = self._conf.workspace.path + self._conf.workspace.name + "_" + tag + str(self._sep_timetag) + "/"

        if not os.path.exists(directory_path):  # pragma: no cover
            os.makedirs(directory_path)
        combine_dict[tag]["path"] = directory_path

        return combine_dict


class MeanClassifierCombiner:
    """This class handles combining the classification models. In multiclass classification models where the
    probabilities are predicted, the prediction file will contain multiple prediction columns unlike the regression
    models where only one column is needed for predictions. As such, two different classes handle the classification
    and regression models.
    """
    def __init__(self, conf: Configuration, models_dict, sep_timetag, data_type):
        """Initialize an instance of ClassifierCombiner using a conf object, models_dict, and sep_timetag.

        :param conf: an instance of the Configuration class
        :param models_dict: learner's models dictionary. This dictionary contains the information related to all models.
        :param sep_timetag: separator plus timetag or nothing (if we shouldn't use the timetag in the output files)
        :param data_type: the data type, it can be "validation" or "test"
        """
        self._conf = conf
        self._models_dict = models_dict
        self._sep_timetag = sep_timetag
        # this will hold the id_cols df if defined
        self._id_cols = None
        # pandas dataframe to hold the prediction for class and probabilities
        self._pred_class = pd.DataFrame()
        self._pred_proba = pd.DataFrame()
        # these will hold the column names for class and proba
        self._proba_col_names = None
        self._class_col_names = None
        self.validation_pred_cols = None
        self.test_pred_cols = None
        self.data_type = data_type
        self.dtype_sep = f"_{self.data_type}_"
        self.prediction_type = getattr(self._conf.data, f"{self.data_type}_prediction_type")
        self.add_timetag = getattr(self.conf.data, f"{self.data_type}_add_timetag")

    @property
    def conf(self):
        return self._conf

    @property
    def models_dict(self):
        return self._models_dict

    @property
    def sep_timetag(self):
        return self._sep_timetag

    @property
    def pred_class(self):
        return self._pred_class

    @property
    def pred_proba(self):
        return self._pred_proba

    @property
    def proba_col_names(self):
        return self._proba_col_names

    @property
    def class_col_names(self):
        return self._class_col_names

    def combine(self):
        """Depending on the prediction type (proba, class, or all), call the corresponding methods to combine the
        prediction of the models. After that, write the combined predictions to disk and score them if needed.

        :return: None
        """
        pred = pd.DataFrame()
        if self.prediction_type in ["all", "proba"]:
            self.combine_proba()
            pred = pd.concat([pred, self._pred_proba[self._proba_col_names]], axis=1)
        if self.prediction_type in ["all", "class"]:
            self.combine_class()
            pred = pd.concat([pred, self._pred_class[self._class_col_names]], axis=1)

        combine_dict = self.get_mean_combine_dict()
        predictor = BasePredictor(None, self._conf)
        predictor.write_predictions(next(iter(combine_dict)),
                                    pred,
                                    data_type=self.data_type,
                                    data=self._id_cols,
                                    models_dict=combine_dict,
                                    add_timetag=self.add_timetag)

        # we can score the combined model if requested
        if self.conf.engine in ["Classifier", "Regressor"] and self._conf.data.validation_score_activate:
            scorer = ClassifierScorer(self._conf, combine_dict)
            scorer.score()

    def combine_proba(self):
        """Loop through each model in models_dict, load the prediction (and id) columns, and then combine the
        predictions.

        :return: None
        """
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            # we need this to form the models_dict
            if getattr(self, f"{self.data_type}_pred_cols") is None:
                setattr(self, f"{self.data_type}_pred_cols", mdl[f"{self.data_type}_pred_cols"])
            filename = PRED_PATH.format(
                path=mdl["path"],
                output_name=self._conf.workspace.name,
                dtype_sep=self.dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag)
            )

            # if we haven't loaded the id columns, do it here
            if self._id_cols is None:
                self.load_id_cols(filename)

            logging.info("Loading the predictions for model %s", tag)
            pred = self.load_pred_proba(tag, mdl, filename)
            self._pred_proba = pd.concat([self._pred_proba, pred], axis=1)

        # this dictionary stores the classes (keys) and the corresponding columns for those classes. This is then used
        # to compute the averages for each class
        class_cols = {}
        for col in self._proba_col_names:
            c = col.rsplit("_")[-1]
            class_cols[c] = [col for col in self._pred_proba if col.endswith(c)]
            if self.conf.combine.mean_type == "arithmetic":
                self._pred_proba[col] = self._pred_proba[class_cols[c]].mean(axis=1)
            else:
                self._pred_proba[col] = stats.gmean(self._pred_proba[class_cols[c]], axis=1)

    def combine_class(self):
        """Loop through each model in models_dict, load the prediction (and id) columns, and then combine the
        predictions.

        :return: None
        """
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            # we need this to form the models_dict
            if getattr(self, f"{self.data_type}_pred_cols") is None:
                setattr(self, f"{self.data_type}_pred_cols", mdl[f"{self.data_type}_pred_cols"])
            logging.info("Loading the predictions for model %s", tag)
            filename = PRED_PATH.format(
                path=mdl["path"],
                output_name=self._conf.workspace.name,
                dtype_sep=self.dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag)
            )

            # if we haven't loaded the id columns, do it here
            if self._id_cols is None:
                self.load_id_cols(filename)

            pred = self.load_pred_class(tag, mdl, filename)
            self._pred_class = pd.concat([self._pred_class, pred], axis=1)

        # to determine the predicted class, we do majority vote here
        self._pred_class[self._class_col_names] = self._pred_class.mode(axis=1).iloc[:, 0].astype(int)

    def load_id_cols(self, filename):
        """Load the id columns from one of the prediction files. This method should be called once because the id
        columns should be identical for all models.

        :param filename: the path to the output (prediction file)
        :return: None
        """
        if self._conf.column.id_cols:
            self._id_cols = get_data(filename,
                                     manifest_file=None,
                                     usecols=self._conf.column.id_cols)

    def load_pred_proba(self, tag, mdl, filename):
        """Load the predictions for a single model. After the data is loaded, prepend the models tag to the name of the
        columns in the prediction file.

        :param tag: the model tag (this is used for renaming the prediction column)
        :param filename: the path to the prediction file
        :return: a pandas dataframe containing the prediction data
        """
        logging.info("Loading prediction probabilities from the output file...")

        # get the prediction column names
        if self.prediction_type == "all":
            self._proba_col_names = list(filter(lambda x: x.startswith('_proba_'), mdl[f"{self.data_type}_pred_cols"]))
        else:
            self._proba_col_names = list(mdl[f"{self.data_type}_pred_cols"])

        # load the prediction columns
        pred_proba = get_data(filename,
                              manifest_file=None,
                              usecols=self._proba_col_names)
        # rename the column name to start with the model tag
        col_rename_dict = {col_name: f"{tag}_{col_name}" for col_name in pred_proba.columns}
        pred_proba = pred_proba.rename(columns=col_rename_dict)
        return pred_proba

    def load_pred_class(self, tag, mdl, filename):
        """Load the predictions for a single model. After the data is loaded, rename the prediction column to be the
        model tag.

        :param tag: the model tag (this is used for renaming the prediction column)
        :param filename: the path to the prediction file
        :return: a pandas dataframe containing the prediction data
        """
        logging.info("Loading prediction column from the output file...")

        if self.prediction_type == "all":
            self._class_col_names = list(filter(lambda x: x.startswith('_class_'), mdl[f"{self.data_type}_pred_cols"]))
        else:
            self._class_col_names = list(mdl[f"{self.data_type}_pred_cols"])

        pred_class = get_data(filename,
                              manifest_file=None,
                              usecols=self._class_col_names)

        # rename the column name to start with the model tag
        col_rename_dict = {col_name: f"{tag}" for col_name in pred_class.columns}
        # class column name should be only one item
        self._class_col_names = self._class_col_names[0]
        pred_class = pred_class.rename(columns=col_rename_dict)
        return pred_class

    def get_mean_combine_dict(self):
        """Construct a models_dict items for mean_combine model. The models_dict for the combined models is constructed
        here instead of configuration module because this model cannot be loaded, etc.

        :return: A models_dict with the tag "mean_combine".
        """
        combine_dict = {}
        tag = "mean_combine"
        combine_dict[tag] = {}

        directory_path = self._conf.workspace.path + self._conf.workspace.name + "_" + tag + str(self._sep_timetag) + "/"

        if not os.path.exists(directory_path):  # pragma: no cover
            os.makedirs(directory_path)
        combine_dict[tag]["path"] = directory_path
        combine_dict[tag][f"{self.data_type}_pred_cols"] = getattr(self, f"{self.data_type}_pred_cols")

        return combine_dict


class TriadCombiner(BaseScorer):
    """This class implements the TriadCombiner algorithm to combine the predictions of multiple models. For more details
    about the algorithm see <link to be added after once the blog post is uploaded>. TriadCombiner is only supported for
    regression problems (both standard and deep regression). This class follows the fit-transform pattern. Either fit or
    transform is called. The "fit" method fits the weights and the "transform" method uses the weights to get the final
    predictions. Please note that the "fit" method also writes the final predictions for validation data.
    """
    def __init__(self, conf: Configuration, models_dict, sep_timetag):
        """Initialize an instance of TriadCombiner using a conf object, models_dict, and sep_timetag.

        :param conf: an instance of the Configuration class
        :param models_dict: learner's models dictionary. This dictionary contains the information related to all models.
        :param sep_timetag: separator plus timetag or nothing (if we shouldn't use the timetag in the output files)
        """
        super().__init__(conf, models_dict)
        self._sep_timetag = sep_timetag
        # these are the initial weights. We currently use 0.5 but this can potentially come from a distribution
        self.w = np.zeros(2 * self._conf.model.num_models - 2)
        self.w.fill(0.5)
        self.n_triads = self._conf.model.num_models - 1
        # this is list of initial scores for each model
        self.initial_scores = []
        self.best_initial_score = None
        self.best_final_score = None
        # the following lists would hold models and triads weights
        self.models_weights = []
        self.triad_weights = []
        # this will hold the id_cols df if defined
        self._id_cols = None
        self.data_type = None
        self.dtype_sep = None
        self.column_name = None
        self.add_timetag = None

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, value):
        self._conf = value

    @property
    def models_dict(self):
        return self._models_dict

    @property
    def sep_timetag(self):
        return self._sep_timetag

    def fit(self):
        """The "fit" method for TriadCombiner. This method first update the instance attributes to correspond to
        "validation" data_type. It then loads the predictions (on validation data) to fit the parameters. Two sets of
        parameters need to be determined: i) model weights, which multiplies each models predictions by a constant,
        ii) the triad weights. Finally, it writes the combined predictions and saves the combiner.

        :return: None
        """
        self.update_params_for_data_type(data_type="validation")
        pred, id_cols = self.load_pred_id_cols()
        # this will save all of the nodes data
        nodes = np.zeros((pred.shape[0], 2*self.conf.model.num_models - 1))
        nodes = self.get_model_weights(pred, nodes)
        self.get_triad_weights(nodes)
        self.calculate_total_improvement()
        combine_dict = self.get_triad_combine_dict()
        self.write_predictions(id_cols, nodes, combine_dict)
        self.save_combiner(combine_dict)

    def transform(self, data_type):
        """The "transform" method for TriadCombiner. The assumption here is that the model_weights and triad_weights
        are already populated. This method accepts a data_type argument. This method first update the instance
        attributes to correspond to the data_type argument. It then loads the predictions (validation or test data
        depending on the value of data_type argument. Finally, it writes the combined predictions.

        :param data_type: the data_type, it can be "validation" or "test"
        :return: None
        """
        self.update_params_for_data_type(data_type=data_type)
        pred, id_cols = self.load_pred_id_cols()
        nodes = np.zeros((pred.shape[0], 2*self.conf.model.num_models - 1))
        for i in range(self._conf.model.num_models):
            nodes[:, i] = pred[:, i] * self.models_weights[i]
        for triad in range(self.n_triads):
            nodes[:, self._conf.model.num_models + triad] = self.triad_weights[2*triad] * nodes[:, 2*triad] + self.triad_weights[2*triad+1] * nodes[:, 2*triad+1]
        combine_dict = self.get_triad_combine_dict()
        self.write_predictions(id_cols, nodes, combine_dict)

    def update_params_for_data_type(self, data_type):
        """Update the data_type related instance attributes. The reason for updating the instance attributes here rather
        than the init method is that the combiner can be used to transform both validation and test data without
        re-instantiating the combiner object.

        :param data_type: the data_type, it can be "validation" or "test"
        :return: None
        """
        self.data_type = data_type
        self.dtype_sep = f"_{data_type}_"
        self.column_name = getattr(self._conf.data, f"{data_type}_column_name")
        self.add_timetag = getattr(self.conf.data, f"{data_type}_add_timetag")

    def load_pred_id_cols(self):
        """Load the predictions and id data. This method loops through all models defined in models_dict and loads the
        predictions one by one and appends them to the pred dataframe. It also loads the id columns once because id
        columns are identical for all models. As the predictions of different models are loaded, it also scores the
        predictions to get the best initial score. This best initial score is later used to get the total improvement
        from combining the predictions of multiple models.

        :return: pred 2d numpy array and id_cols dataframe
        """
        pred = pd.DataFrame()
        self.initial_scores = []
        id_cols = None
        for tag, mdls in self._models_dict.items():
            mdl = mdls.get(0, mdls)
            logging.info("Loading the predictions for model %s", tag)
            filename = PRED_PATH.format(
                path=mdl["path"],
                output_name=self._conf.workspace.name,
                dtype_sep=self.dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag)
            )
            if id_cols is None:
                id_cols = self.load_id_cols(filename)

            single_pred = self.load_pred(tag, filename)
            self.initial_scores.append(self.scoring_handler(self.conf.combine.triad_score_type, self.y_true, single_pred, params={}))
            pred = pd.concat([pred, single_pred], axis=1)

        pred = pred.values
        self.best_initial_score = min(self.initial_scores)
        return pred, id_cols

    def load_id_cols(self, filename):
        """Load the id columns from one of the prediction files. This method should be called once because the id
        columns should be identical for all models.

        :param filename: the path to the output (prediction file)
        :return: None
        """
        if self._conf.column.id_cols:
            id_cols = get_data(filename,
                               manifest_file=None,
                               usecols=self._conf.column.id_cols)
            return id_cols

    def load_pred(self, tag, filename):
        """Load the predictions for a single model. After the data is loaded, rename the prediction column to be the
        model tag.

        :param tag: the model tag (this is used for renaming the prediction column)
        :param filename: the path to the prediction file
        :return: a pandas dataframe containing the prediction data
        """
        logging.info("Loading prediction column from the output file...")

        pred = get_data(filename,
                        manifest_file=None,
                        usecols=[self.column_name]).rename(columns={self.column_name: tag})
        return pred

    def get_model_weights(self, pred, nodes):
        """In the triad algorithms, we multiply the predictions of each model by a constant number. In this method,
        those weights are determined and the nodes array is updated with the weighted predictions.

        :param pred: a 2-d numpy array containing the predictions
        :param nodes: a 2-d numpy array to hold all the nodes data.
        :return: updated nodes data where the first layer contains the weighted predictions.
        """
        for triad_index in range(self.conf.model.num_models):
            nodes[:, triad_index], weight, s = self.single_weight_gradient_descent(0.5,
                                                                                   pred[:, triad_index],
                                                                                   self.y_true,
                                                                                   dw=self.conf.combine.triad_models_step_size,
                                                                                   max_iter=self.conf.combine.triad_models_max_iter)
            self.models_weights.append(weight)
        return nodes

    def single_weight_gradient_descent(self, w, pred, y_true, dw, max_iter):
        """Find the optimum weight to multiply the predictions of a model given the predictions and true values using
        gradient descent algorithms.

        :param w: the initial weight, typically 0.5.
        :param pred: a prediction column
        :param y_true: the true values
        :param dw: the step size for gradient descent
        :param max_iter: the maximum number of iterations before we sto[
        :return: the weithed optimum predictions, the optimum weight, and the score
        """
        counter = 1
        s_old, old_prediction = self.get_weighted_score(w, pred, y_true)
        s_new, new_prediction = self.get_weighted_score(w + dw, pred, y_true)

        if s_new < s_old:
            sign = +1
        elif s_new == s_old:
            return new_prediction, w, s_new
        else:
            sign = -1

        delta_s = dw  # dw and delta_s must positive
        while counter < max_iter:

            w += sign * delta_s
            s_new, new_prediction = self.get_weighted_score(w, pred, y_true)

            if s_new > s_old:
                w -= sign * delta_s
                break
            else:
                old_prediction = new_prediction

            s_old = s_new
            counter += 1
            if counter % 10000 == 0:
                logging.info(f"haven't converged after {counter} counts, new score is {s_new} and weight is {w}")

        return old_prediction, w, s_old

    def get_weighted_score(self, w, pred, y_true):
        """Multiply the predictions of a model by a wight and compute the score.

        :param w: the weight
        :param pred: an array of predictions
        :param y_true: an array of true values
        :return: the score the weighted predictions
        """
        pred = w * pred
        score = self.scoring_handler(self.conf.combine.triad_score_type, y_true, pred, params={})

        return score, pred

    def get_triad_weights(self, nodes):
        """This is one of the main methods for the triad algorithms. Here we run the gradient descent algorithms to
        find the optimum weight for each triad.

        :param nodes: a 2-d numpy array to hold all the nodes data
        :return: None
        """
        initial_scores = self.get_model_scores(self.conf.model.num_models, self.y_true, nodes)
        logging.info(f"Initial scores for individual models are {initial_scores}")

        for triad_index in range(self.n_triads):
            w1, w2, s = self.double_weight_gradient_descent(self.w[2 * triad_index],
                                                            self.w[2 * triad_index + 1],
                                                            nodes,
                                                            triad_index,
                                                            self.y_true,
                                                            dw=self.conf.combine.triad_triads_step_size,
                                                            max_iter=self.conf.combine.triad_triads_max_iter,
                                                            n_models=self.conf.model.num_models)
            logging.info("w1={w1:.4f} \t w2={w2:.4f} \t s={s:.6f} \t triad index = {triad_index}".
                         format(w1=w1, w2=w2, s=s, triad_index=triad_index))
            self.triad_weights.append(w1)
            self.triad_weights.append(w2)
            self.best_final_score = s

    def get_model_scores(self, num_models, y_true, pred):
        """Compute the scores of all models. This will help us get the best initial score. Please note that the score
        type is defined for the triad algorithm. The pred is a 2-d numpy array that contains all predictions.

        :param num_models: the number of models, it's used to loop over the columns of pred array
        :param y_true: the true values to use for scoring
        :param pred: an 2-d numpy array that contains all the predictions
        :return: a 1-d numpy array containing the scores for all the models
        """
        s0 = np.zeros(num_models)
        for i in range(num_models):
            s0[i] = self.scoring_handler(self.conf.combine.triad_score_type, y_true, pred[:, i], params={})
        return s0

    def double_weight_gradient_descent(self, w1, w2, pred, triad_index, y_true, dw, max_iter, n_models):
        """This method runs the gradient descent algorithms to optimize the weights for combining the predictions of
        two models in a triad geometry.

        :param w1: the initial first weight
        :param w2: the initial second weight
        :param pred: a 2-d numpy array containing all the predictions
        :param triad_index: the index of the triad, 0, 1, 2, ...
        :param y_true: the true values
        :param dw: the step size for the gradient descent algorithm
        :param max_iter: the maximum number of iterations before we stop
        :param n_models: the total number of models
        :return: the optimum weights the the corresponding score
        """
        counter = 1
        s_old, old_pred = self.get_combined_score(w1, w2, y_true, pred[:, 2 * triad_index], pred[:, 2 * triad_index + 1])
        s_new, new_pred = self.get_combined_score(w1 + dw, w2 - dw, y_true, pred[:, 2 * triad_index], pred[:, 2 * triad_index + 1])

        if s_new < s_old:
            sign = +1
        elif s_new == s_old:
            return w1, w2, s_new
        else:
            sign = -1

        delta_s = dw  # dw and delta_s must positive
        while counter < max_iter:

            w1 += sign * delta_s
            w2 -= sign * delta_s
            s_new, new_pred = self.get_combined_score(w1, w2, y_true, pred[:, 2 * triad_index], pred[:, 2 * triad_index + 1])

            if s_new > s_old:
                w1 -= sign * delta_s
                w2 += sign * delta_s
                break
            else:
                old_pred = new_pred

            counter += 1
            s_old = s_new

            if counter % 10000 == 0:
                logging.info(f"haven't converged after {counter} counts, new score is {s_new} and wights are {w1}, {w2}")

        if triad_index + n_models < pred.shape[1]:
            pred[:, triad_index + n_models] = old_pred
        return w1, w2, s_old

    def get_combined_score(self, w1, w2, y_true, pred1, pred2):
        """Use two weights to combine the predictions of two models and then compute the score of the combined models.

        :param w1: the first weight to multiply the predictions of the first model
        :param w2: the second weight to multiply the predictions of the second model
        :param y_true: the true values
        :param pred1: the predictions of the first model
        :param pred2: the predictions of the second model
        :return: the calculated score and the combined predictions
        """
        pred = w1 * pred1 + w2 * pred2
        s = self.scoring_handler(self.conf.combine.triad_score_type, y_true, pred, params={})
        return s, pred

    def calculate_total_improvement(self):
        """Use the best initial scire and the final score to compute the percentage of the improvement.

        :return: None
        """
        percentage_improvement = ((self.best_initial_score - self.best_final_score) / self.best_initial_score) * 100
        logging.info("Total improvement={:.4f}%".format(percentage_improvement))

    def write_predictions(self, id_cols, nodes, combine_dict):
        """Write the final predictions after combining all the models into disk similar to all other models.

        :param id_cols: a pandas dataframe containing the id columns
        :param nodes: a 2-d numpy array containing all the nodes data. The last column has the final predictions.
        :param combine_dict: a models dict for triad combine algorithm
        :return: None
        """
        predictor = BasePredictor(None, self._conf)
        predictor.write_predictions(next(iter(combine_dict)),
                                    pd.Series(nodes[:, -1], name=self.column_name),
                                    data_type=self.data_type,
                                    data=id_cols,
                                    models_dict=combine_dict,
                                    add_timetag=self.add_timetag)

    def save_combiner(self, combine_dict):
        """Save/pickle the combiner object so it can be loaded if needed. Please note that we only save the combiner
        object if we are training and we want to save the models.

        :param combine_dict: a models dict for triad combine algorithm
        :return: None
        """
        tag = next(iter(combine_dict))
        # save the combiner if train_models save_models are set to true
        if self.conf.model.train_models and self._conf.model.save_models:
            filename = SAVE_MODEL_PATH.format(
                path=combine_dict[tag]["path"],
                output_name=self._conf.workspace.name,
                tag=tag,
                sep_timetag=str(self.sep_timetag),
                ext=".triad")

            # we need to do this because we cannot directly pickle the deep learning models
            for tag, mdl in self.models_dict.items():
                mdl["model"] = None
            with open(filename, "wb") as pickle_file:
                pickle.dump(self, pickle_file)

    def get_triad_combine_dict(self):
        """Construct a models_dict items for tria_combine model. The models_dict for the combined models is constructed
        here instead of configuration module because this model cannot be loaded like other models.

        :return: A models_dict with the tag "triad_combine".
        """
        combine_dict = {}
        tag = "triad_combine"
        combine_dict[tag] = {}

        directory_path = self._conf.workspace.path + self._conf.workspace.name + "_" + tag + str(self._sep_timetag) + "/"

        if not os.path.exists(directory_path):  # pragma: no cover
            os.makedirs(directory_path)
        combine_dict[tag]["path"] = directory_path

        return combine_dict

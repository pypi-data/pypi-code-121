# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module that implements the predictor classes for all engines. This include base and child classes."""

import sys
import abc
import logging
import pandas as pd

from learner.data_worker.output_handler import OutputHandler, get_prediction_col_names
from learner.data_worker.data_processor import DataProcessor
from learner.model_manager.extenders import Extenders
from learner.model_manager.classifiers import ClassifierHandler
from learner.model_manager.regressors import RegressorHandler
from learner.model_manager.deep_classifiers import DeepClassifierHandler
from learner.model_manager.deep_regressors import DeepRegressorHandler
from learner.utilities.templates import PRED_FILENAME, PRED_FILENAME_SEG, PRED_FILENAME_CHUNK_SEG
from learner.model_manager.image_classifiers import ImageClassifierHandler


class BasePredictor:
    """The BasePredictor class to implement the methods that other predictor classes commonly share."""

    @abc.abstractmethod
    def __init__(self, models_dict_item, conf):
        """Initialize a BasePredictor object using a model dictionary item, a conf object, and drop_cols list.

        :param models_dict_item: an item in models_dict
        :param conf: a conf object
        """
        self._models_dict_item = models_dict_item
        self._conf = conf

    @property
    def models_dict_item(self):  # pragma: no cover
        return self._models_dict_item

    @property
    def conf(self):  # pragma: no cover
        return self._conf

    def make_predictions(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError

    def write_predictions(self, tag, prediction, data, index=None, models_dict=None, data_type="", add_timetag=True,
                          add_version=False, version_name="", version_column_name="version"):
        """Write the predictions of the models into a csv file.

        :param tag: the model tag defined by user (this is an arbitrary string)
        :param prediction: the prediction values saved in a dataframe
        :param data: the data set that should be saved along with the predictions
        :param index: the chunk index used for filename
        :param models_dict: the models_dict dictionary
        :param add_version: whether we should add the version column or not
        :param version_name: the value to use in the version column
        :param version_column_name: the name of the version column
        :return: None
        """
        logging.info("Writing the predictions...")
        output = OutputHandler(self._conf)

        # in case data is None or empty
        if isinstance(data, pd.DataFrame) and not data.empty:
            data.reset_index(drop=True, inplace=True)
        prediction.reset_index(drop=True, inplace=True)

        results = pd.concat([data, prediction], axis=1, ignore_index=False)

        dtype_sep = f"_{data_type}_"

        if index is None:
            filename = PRED_FILENAME.format(
                output_name=self._conf.workspace.name,
                dtype_sep=dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag)
            )
        else:
            filename = PRED_FILENAME_SEG.format(
                output_name=self._conf.workspace.name,
                dtype_sep=dtype_sep,
                tag=str(tag),
                sep_timetag=str(self._conf.sep_timetag),
                index=index
            )
        if models_dict is None:
            output.save_file(self._conf.model.models_dict[tag]["path"],
                             filename,
                             results,
                             add_timetag=add_timetag,
                             add_version=add_version,
                             version_name=version_name,
                             version_column_name=version_column_name)
        else:
            output.save_file(models_dict[tag]["path"],
                             filename, results,
                             add_timetag=add_timetag,
                             add_version=add_version,
                             version_name=version_name,
                             version_column_name=version_column_name)


class ClassifierPredictor(BasePredictor):
    """Handle making and writing predictions for the classifier engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize a ClassifierPredictor object by calling the super initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, column_name, data_type=None, prediction_type=None):
        """Use the test_data to make predictions.

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: predictions and data
        """
        if prediction_type == "proba":
            prediction, data = ClassifierHandler.learner_predict_proba(test_data[self._models_dict_item["train_features"]],
                                                                       self._models_dict_item,
                                                                       carry_data=True,
                                                                       full_data=test_data,
                                                                       cols_to_carry=self._conf.column.id_cols)

            prediction_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        elif prediction_type == "class":
            prediction, data = ClassifierHandler.learner_predict(test_data[self._models_dict_item["train_features"]],
                                                                 self._models_dict_item,
                                                                 carry_data=True,
                                                                 full_data=test_data,
                                                                 cols_to_carry=self._conf.column.id_cols)

            prediction_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        else:
            # get prediction classes
            class_prediction, data = ClassifierHandler.learner_predict(test_data[self._models_dict_item["train_features"]],
                                                                       self._models_dict_item,
                                                                       carry_data=True,
                                                                       full_data=test_data,
                                                                       cols_to_carry=self._conf.column.id_cols)

            class_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                       "class",
                                                       column_name)

            class_df = pd.DataFrame(class_prediction, columns=["_class_" + col for col in class_col_names])

            # get prediction probabilities
            proba_prediction, _ = ClassifierHandler.learner_predict_proba(test_data[self._models_dict_item["train_features"]],
                                                                          self._models_dict_item,
                                                                          carry_data=True,
                                                                          full_data=test_data,
                                                                          cols_to_carry=self._conf.column.id_cols)

            proba_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                       "proba",
                                                       column_name)

            proba_df = pd.DataFrame(proba_prediction, columns=["_proba_" + col for col in proba_col_names])

            # concatenate probability and class predictions
            prediction_df = pd.concat([proba_df, class_df], ignore_index=False, axis=1)

        if data_type == "validation":
            self._models_dict_item["validation_pred_cols"] = prediction_df.columns
        elif data_type == "test":
            self._models_dict_item["test_pred_cols"] = prediction_df.columns
        else:
            logging.critical("Invalid data_type. Acceptable values are: 'validation' and 'test'")
            sys.exit(1)
        return prediction_df, data


class RegressorPredictor(BasePredictor):
    """Handle making and writing predictions for the regressor engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize a RegressorPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, column_name, data_type=None, prediction_type=None):
        """Use the test_data to make predictions.

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all". This parameter is not used here.
        :return: predictions and data
        """
        prediction, data = RegressorHandler.learner_predict(test_data[self._models_dict_item["train_features"]],
                                                            self._models_dict_item,
                                                            carry_data=True,
                                                            full_data=test_data,
                                                            cols_to_carry=self._conf.column.id_cols)

        prediction_df = pd.DataFrame(prediction, columns=[column_name])

        # if we log transformed the target but need to write the actuals, we do it here
        if self.conf.process.log_transform_target_activate:
            if (data_type == "validation" and self.conf.process.log_transform_target_score_actuals) or \
               (data_type == "test" and self.conf.process.log_transform_target_predict_actuals):
                prediction_df = DataProcessor.exponential_transform(prediction_df,
                                                                    params=[{"activate": True,
                                                                             "power": self.conf.process.log_transform_target_base,
                                                                             "col": column_name,
                                                                             "name": column_name,
                                                                             "shift": -self.conf.process.log_transform_target_shift}],
                                                                    cols=[column_name])
        return prediction_df, data


class RecommenderPredictor(BasePredictor):
    """Handle making and writing predictions for the recommender engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize a RecommenderPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, data_type=None, column_name=None, prediction_type=None):
        """Use the test_data to make predictions.

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: None
        """
        # make predictions by replacing the train_col with the test_col
        self._models_dict_item["prediction_encoded"], self._models_dict_item["data"] = \
            ClassifierHandler.learner_predict(test_data[self._models_dict_item["train_features"]],
                                              self._models_dict_item,
                                              carry_data=True,
                                              full_data=test_data,
                                              cols_to_carry=self._conf.column.id_cols)

        # get the actual predictions by doing an inverse transform
        self._models_dict_item["prediction"] = self._models_dict_item["le"].inverse_transform(
            self._models_dict_item["prediction_encoded"], self._conf.column.target_col)

        if self._conf.recommender.activate:
            # sort and extend the predictions using the similarity scores
            ext = Extenders(self._models_dict_item, self._conf)
            self._models_dict_item = ext.extend(column_name=column_name)
            return self._models_dict_item["extended_prediction"], self._models_dict_item["data"]

        return pd.Series(self._models_dict_item["prediction"],
                         name=column_name), self._models_dict_item["data"]


class BaseSegmentPredictor(BasePredictor):
    def __init__(self, models_dict_item, conf):
        """Initialize a RegressorPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def write_predictions(self, tag, prediction, data, index=None, mdl=None, seg_id=None, add_timetag=True,
                          data_type="", add_version=False, version_name="", version_column_name="version"):
        """Write the predictions of the models into a csv file.

        :param tag: the model tag defined by user (this is an arbitrary string like RF1, etc)
        :param prediction: the prediction values saved in a numpy array
        :param data: the data set that should be saved along with the predictions
        :param index: the chunk index used for filename
        :param mdl: an item in the models_dict dictionary
        :param seg_id: the segment id
        :param add_timetag: whether we should add the timetag or not
        :param data_type: the data type, it could be "validation" or "test"
        :param add_version: whether we should add the version column or not
        :param version_name: the value to use in the version column
        :param version_column_name: the name of the version column
        :return: None
        """
        logging.info("Writing the predictions")

        if data_type:
            dtype_sep = f"_{data_type}_"
        else:
            dtype_sep = "_"

        output = OutputHandler(self._conf, data_type=data_type)

        # in case data is None or empty
        if isinstance(data, pd.DataFrame) and not data.empty:
            data.reset_index(drop=True, inplace=True)

        prediction.reset_index(drop=True, inplace=True)

        # save the output in csv format
        results = pd.concat([data, prediction], axis=1)

        if index is None:
            sep_index = ""
        else:
            sep_index = f"_{index}"

        filename = PRED_FILENAME_CHUNK_SEG.format(
            output_name=self._conf.workspace.name,
            dtype_sep=dtype_sep,
            tag=str(tag),
            sep_timetag=str(self._conf.sep_timetag),
            seg_id=seg_id,
            sep_index=sep_index
        )
        output.save_file(mdl["path"], filename, results, add_timetag=add_timetag,
                         add_version=add_version, version_name=version_name, version_column_name=version_column_name)


class ClassifierSegmentPredictor(BaseSegmentPredictor):
    """Handle making and writing predictions for the classifier engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize a ClassifierPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, column_name, data_type, prediction_type=None):
        """Use the test_data to make predictions.

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: predictions and data
        """
        if prediction_type == "proba":
            prediction, data = ClassifierHandler.learner_predict_proba(test_data.assign(
                **{self._conf.segmenter.train_col: test_data[self._conf.segmenter.test_col]})[self._models_dict_item["train_features"]],
                                                                       self._models_dict_item,
                                                                       carry_data=True,
                                                                       full_data=test_data,
                                                                       cols_to_carry=self._conf.column.id_cols)

            prediction_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        elif prediction_type == "class":
            prediction, data = ClassifierHandler.learner_predict(test_data[self._models_dict_item["train_features"]],
                                                                 self._models_dict_item, carry_data=True,
                                                                 full_data=test_data,
                                                                 cols_to_carry=self._conf.column.id_cols)

            prediction_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        else:
            # get prediction classes
            class_prediction, data = ClassifierHandler.learner_predict(test_data.assign(
                **{self._conf.segmenter.train_col: test_data[self._conf.segmenter.test_col]})[self._models_dict_item["train_features"]],
                                                                       self._models_dict_item,
                                                                       carry_data=True,
                                                                       full_data=test_data,
                                                                       cols_to_carry=self._conf.column.id_cols)

            class_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                       prediction_type,
                                                       column_name)

            class_df = pd.DataFrame(class_prediction, columns=["_class_" + col for col in class_col_names])

            # get prediction probabilities
            proba_prediction, _ = ClassifierHandler.learner_predict_proba(test_data.assign(
                **{self._conf.segmenter.train_col: test_data[self._conf.segmenter.test_col]})[self._models_dict_item["train_features"]],
                                                                          self._models_dict_item,
                                                                          carry_data=True,
                                                                          full_data=test_data,
                                                                          cols_to_carry=self._conf.column.id_cols)

            proba_col_names = get_prediction_col_names(self._models_dict_item["model"].classes_,
                                                       prediction_type,
                                                       column_name)

            proba_df = pd.DataFrame(proba_prediction, columns=["_proba_" + col for col in proba_col_names])

            # concatenate probability and class predictions
            prediction_df = pd.concat([proba_df, class_df], ignore_index=False, axis=1)

        if data_type == "validation":
            self._models_dict_item["validation_pred_cols"] = prediction_df.columns
        elif data_type == "test":
            self._models_dict_item["test_pred_cols"] = prediction_df.columns
        else:
            logging.critical("Invalid data_type. Acceptable values are: 'validation' and 'test'")
            sys.exit(1)
        return prediction_df, data


class RegressorSegmentPredictor(BaseSegmentPredictor):
    """Handle making and writing predictions for the regressor engine"""

    def __init__(self, models_dict_item, conf):
        """Initialize a RegressorPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, column_name, data_type=None, prediction_type=None):
        """Use the test_data to make predictions

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: predictions and data
        """
        prediction, data = RegressorHandler.learner_predict(test_data.assign(
            **{self._conf.segmenter.train_col: test_data[self._conf.segmenter.test_col]})[self._models_dict_item["train_features"]],
                                                            self._models_dict_item, carry_data=True,
                                                            full_data=test_data,
                                                            cols_to_carry=self._conf.column.id_cols)

        prediction_df = pd.DataFrame(prediction, columns=[column_name])

        # if we log transformed the target but need to write the actuals, we do it here
        if self.conf.process.log_transform_target_activate:
            if (data_type == "validation" and self.conf.process.log_transform_target_score_actuals) or \
               (data_type == "test" and self.conf.process.log_transform_target_predict_actuals):
                prediction_df = DataProcessor.exponential_transform(prediction_df,
                                                                    params=[{"activate": True,
                                                                             "power": self.conf.process.log_transform_target_base,
                                                                             "col": column_name,
                                                                             "name": column_name,
                                                                             "shift": -self.conf.process.log_transform_target_shift}],
                                                                    cols=[column_name])
        return prediction_df, data


class RecommenderSegmentPredictor(BaseSegmentPredictor):
    """Handle making and writing predictions for the recommender engine"""

    def __init__(self, models_dict_item, conf):
        """Initialize a RecommenderPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, test_data, column_name=None, prediction_type=None):
        """Use the test_data to make predictions

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: None
        """
        # make predictions by replacing the train_col with the test_col
        self._models_dict_item["prediction_encoded"], self._models_dict_item["data"] = ClassifierHandler.learner_predict(
            test_data.assign(
                **{self._conf.segmenter.train_col: test_data[self._conf.segmenter.test_col]})[self._models_dict_item["train_features"]],
            self._models_dict_item,
            carry_data=True,
            full_data=test_data,
            cols_to_carry=self._conf.column.id_cols)

        # get the actual predictions by doing an inverse transform
        self._models_dict_item["prediction"] = self._models_dict_item["le"].inverse_transform(
            self._models_dict_item["prediction_encoded"], self._conf.column.target_col)

        if self._conf.recommender.activate:
            # sort and extend the predictions using the similarity scores
            ext = Extenders(self._models_dict_item, self._conf)
            self._models_dict_item = ext.extend(column_name)
            return self._models_dict_item["extended_prediction"], self._models_dict_item["data"]

        return pd.Series(self._models_dict_item["prediction"],
                         name=column_name), self._models_dict_item["data"]


class DeepClassifierPredictor(BaseSegmentPredictor):
    """Handle making and writing predictions for the image_classifier engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize an ImageClassifierPredictor object by calling the initializer of the parent class."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, X, data, column_name, data_type=None, prediction_type=None):
        """Use the test data to make predictions. Depending on the prediction type, we call the appropriate methods
        and make necessary modifications. In the end, we return the predictions and the data that should be returned
        along with the predictions.

        :param X: the data set to use for making predictions
        :param data: a pandas dataframe that contains additional data to potentially be returned along with the predictions.
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "test". Unlike other engines, "validation" is not accepted here.
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: predictions and data
        """
        if prediction_type == "proba":
            prediction, data = DeepClassifierHandler.learner_predict_proba(X,
                                                                           self._models_dict_item,
                                                                           device=self.conf.model.device,
                                                                           carry_data=True,
                                                                           full_data=data,
                                                                           cols_to_carry=self._conf.column.id_cols)
            prediction_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)
        elif prediction_type == "class":
            prediction, data = DeepClassifierHandler.learner_predict(X,
                                                                     self._models_dict_item,
                                                                     device=self.conf.model.device,
                                                                     carry_data=True,
                                                                     full_data=data,
                                                                     cols_to_carry=self._conf.column.id_cols)
            prediction_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        else:
            # get prediction classes
            class_prediction, data = DeepClassifierHandler.learner_predict(X,
                                                                           self._models_dict_item,
                                                                           device=self.conf.model.device,
                                                                           carry_data=True,
                                                                           full_data=data,
                                                                           cols_to_carry=self._conf.column.id_cols)

            class_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                       "class",
                                                       column_name)

            class_df = pd.DataFrame(class_prediction, columns=["_class_" + col for col in class_col_names])

            # get prediction probabilities
            proba_prediction, _ = DeepClassifierHandler.learner_predict_proba(X,
                                                                              self._models_dict_item,
                                                                              device=self.conf.model.device,
                                                                              carry_data=True,
                                                                              full_data=data,
                                                                              cols_to_carry=self._conf.column.id_cols)

            proba_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                       "proba",
                                                       column_name)

            proba_df = pd.DataFrame(proba_prediction, columns=["_proba_" + col for col in proba_col_names])

            # concatenate probability and class predictions
            prediction_df = pd.concat([proba_df, class_df], ignore_index=False, axis=1)

        if data_type == "test":
            self._models_dict_item["test_pred_cols"] = prediction_df.columns
        else:
            logging.critical("Invalid data_type. Acceptable values are: 'validation' and 'test'")
            sys.exit(1)
        return prediction_df, data


class DeepRegressorPredictor(BaseSegmentPredictor):
    def __init__(self, models_dict_item, conf):
        """Initialize a DeepRegressorPredictor object by calling the parent initializer."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, X, data, column_name, data_type=None, prediction_type=None):
        """Use the test_data to make predictions.

        :param test_data: the data set to use for making predictions
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "validation" or "test"
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all". This parameter is not used here.
        :return: predictions and data
        """
        prediction, data = DeepRegressorHandler.learner_predict(X,
                                                                self._models_dict_item,
                                                                device=self.conf.model.device,
                                                                carry_data=True,
                                                                full_data=data,
                                                                cols_to_carry=self._conf.column.id_cols)

        prediction_df = pd.DataFrame(prediction, columns=[column_name])

        # if we log transformed the target but need to write the actuals, we do it here
        if self.conf.process.log_transform_target_activate:
            if (data_type == "validation" and self.conf.process.log_transform_target_score_actuals) or \
               (data_type == "test" and self.conf.process.log_transform_target_predict_actuals):
                from learner.data_worker.data_processor import DataProcessor
                prediction_df = DataProcessor.exponential_transform(prediction_df,
                                                                    params=[{"activate": True,
                                                                             "power": self.conf.process.log_transform_target_base,
                                                                             "col": column_name,
                                                                             "name": column_name,
                                                                             "shift": -self.conf.process.log_transform_target_shift}],
                                                                    cols=[column_name])

        return prediction_df, data


class ImageClassifierPredictor(BasePredictor):
    """Handle making and writing predictions for the image_classifier engine."""

    def __init__(self, models_dict_item, conf):
        """Initialize an ImageClassifierPredictor object by calling the initializer of the parent class."""

        super().__init__(models_dict_item, conf)

    def make_predictions(self, X, data, column_name, data_type=None, prediction_type=None):
        """Use the test data to make predictions. Depending on the prediction type, we call the appropriate methods
        and make necessary modifications. In the end, we return the predictions and the data that should be returned
        along with the predictions.

        :param X: the data set to use for making predictions
        :param data: a pandas dataframe that contains additional data to potentially be returned along with the predictions.
        :param column_name: the column name to use for writing the predictions
        :param data_type: the data type, can be "test". Unlike other engines, "validation" is not accepted here.
        :param prediction_type: the type of prediction for classification, can be "proba", "class", or "all"
        :return: predictions and data
        """
        if prediction_type == "proba":
            prediction, data = ImageClassifierHandler.learner_predict_proba(X,
                                                                            self._models_dict_item,
                                                                            device=self.conf.model.device,
                                                                            carry_data=True,
                                                                            full_data=data,
                                                                            cols_to_carry=self._conf.column.id_cols)
            prediction_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)
        elif prediction_type == "class":
            prediction, data = ImageClassifierHandler.learner_predict(X,
                                                                      self._models_dict_item,
                                                                      device=self.conf.model.device,
                                                                      carry_data=True,
                                                                      full_data=data,
                                                                      cols_to_carry=self._conf.column.id_cols)
            prediction_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                            prediction_type,
                                                            column_name)

            prediction_df = pd.DataFrame(prediction, columns=prediction_col_names)

        else:
            # get prediction classes
            class_prediction, data = ImageClassifierHandler.learner_predict(X,
                                                                            self._models_dict_item,
                                                                            device=self.conf.model.device,
                                                                            carry_data=True,
                                                                            full_data=data,
                                                                            cols_to_carry=self._conf.column.id_cols)

            class_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                       "class",
                                                       column_name)

            class_df = pd.DataFrame(class_prediction, columns=["_class_" + col for col in class_col_names])

            # get prediction probabilities
            proba_prediction, _ = ImageClassifierHandler.learner_predict_proba(X,
                                                                               self._models_dict_item,
                                                                               device=self.conf.model.device,
                                                                               carry_data=True,
                                                                               full_data=data,
                                                                               cols_to_carry=self._conf.column.id_cols)

            proba_col_names = get_prediction_col_names(self._models_dict_item["classes"],
                                                       "proba",
                                                       column_name)

            proba_df = pd.DataFrame(proba_prediction, columns=["_proba_" + col for col in proba_col_names])

            # concatenate probability and class predictions
            prediction_df = pd.concat([proba_df, class_df], ignore_index=False, axis=1)

        if data_type == "test":
            self._models_dict_item["test_pred_cols"] = prediction_df.columns
        else:
            logging.critical("Invalid data_type. Acceptable values are: 'validation' and 'test'")
            sys.exit(1)
        return prediction_df, data


# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the base classes for different standard engines. We typically do not instantiate these
base classes."""

import os
import sys
import logging

from learner.data_worker.data_manager import TrainDataManager, TestDataManager, ValidationDataManager
from learner.model_manager.prediction_manager import RecommenderPredictor, ClassifierPredictor, RegressorPredictor
from learner.model_manager.classifiers import ClassifierHandler
from learner.model_manager.regressors import RegressorHandler
from learner.model_manager.scoring_manager import ClassifierScorer
from learner.data_worker.data_processor import filter_data
from learner.data_worker.output_handler import OutputHandler, pickle_object
from learner.validator.input_validator import remove_subset_list
from learner.data_worker.output_handler import OutputHandler
from learner.model_manager.model_initializer import ModelInitializer
from learner.validator.output_validator import OutputValidator
from learner.model_manager.model_initializer import ModelLoader, get_pickle_dir
from learner.model_manager import scoring_manager
from learner.combine import combining_manager
from learner.utilities.timer import timeit
from learner.configuration.configuration import Configuration
from learner.analysis.analysis import Analysis
from learner.analysis.shap import Shap
from learner.combine.combining_manager import TriadCombiner


class BaseStandard(ModelInitializer, TrainDataManager):
    """The base engine class to implement methods that other standard engines most likely use."""

    def __init__(self, conf: Configuration):
        super(BaseStandard, self).__init__(conf)
        super(ModelInitializer, self).__init__(conf)

        self._drop_cols = None
        self.conf.model.nrows_score = 0
        # this will hold information about all models as opposed to a single model. This is used to combine the
        # predictions of multiple models
        self.loaded_models_dict = {}
        # the combiner object in case we need to combine the predictions
        self.combiner = None

    @property
    def drop_cols(self):  # pragma: no cover
        return self._drop_cols

    @timeit("load the model(s)")
    def load_models(self, output_path):
        """Load pickled object from path_to_pickle if full directory is provided. Otherwise, load the latest pickled
         object.

        :param output_path: directory path to the pickled object
        :return: None
        """
        logging.info("Loading saved model...")
        _, pickled_file_names, _ = get_pickle_dir(output_path, ext="sav")
        _, triad_file_name, _ = get_pickle_dir(output_path, ext="triad")
        loader = ModelLoader(self._conf)
        # this is to prevent IDEs from complaining
        sep_timetag = ""
        for file_name in pickled_file_names:
            self._conf, self.models_dict, self.processor, self.feature_engineering, sep_timetag = loader.load_model(file_name)
            tag = next(iter(self.models_dict))
            self.loaded_models_dict[tag] = self.models_dict[tag]

            self.predict()
            self.score_prediction()
        if triad_file_name:
            self.combiner = loader.load_combiner(triad_file_name[0])
        self.combine_predictions(sep_timetag, self.loaded_models_dict)

    def fit_models(self, train_data, mdl, drop_cols):
        """Call appropriate methods to fit, cross-validate, or grid-search.

        :param train_data: the training dataset
        :param mdl: an item in the models_dict
        :param drop_cols: a list of columns that should be excluded from training
        :return: None
        """
        # save the train_features in case we need to use them later
        mdl["train_features"] = train_data.drop(drop_cols, axis=1).columns

        if self._conf.model.gs_activate:  # pragma: no cover
            mdl["model"] = getattr(sys.modules[__name__], self._conf.engine + "Handler").learner_grid_search(
                train_data.drop(drop_cols, axis=1),
                train_data[self._conf.column.target_col],
                mdl,
                self._conf.model.gs_kfold_params,
                self._conf.model.gs_options)
        elif self._conf.model.cv_activate:  # pragma: no cover
            mdl["model"] = getattr(sys.modules[__name__], self._conf.engine + "Handler").learner_cross_validation(
                train_data.drop(drop_cols, axis=1),
                train_data[self._conf.column.target_col],
                mdl,
                self._conf.model.cv_kfold_params,
                self._conf.model.cv_options
            )
        else:
            mdl["model"] = getattr(sys.modules[__name__], self._conf.engine + "Handler").learner_fit(
                train_data.drop(drop_cols, axis=1),
                train_data[self._conf.column.target_col], mdl)

    @timeit("make predictions using the trained model(s)")
    def predict(self):
        """Call predict_validation if we need to score the models using validation data and call predict_test if we
        need to make predictions on test data.

        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Making predictions using validation data...")
            self.predict_validation()
        if self._conf.data.test_prediction_activate:
            logging.info("Making predictions using test data...")
            self.predict_test()

    def predict_validation(self):
        """Use the trained models to make predictions on validation data. Unlike test data, the entire validation data
        is loaded in memory when making predictions on validation data.

        :return: None
        """
        validation_manager = ValidationDataManager(self._conf, self.processor, self.feature_engineering)
        for tag, mdl in self.models_dict.items():
            predictor = getattr(sys.modules[__name__], self._conf.engine + "Predictor")(mdl, self._conf)

            prediction_df, data = predictor.make_predictions(validation_manager.data,
                                                             data_type="validation",
                                                             prediction_type=self._conf.data.validation_prediction_type,
                                                             column_name=self._conf.data.validation_column_name)

            predictor.write_predictions(tag,
                                        prediction_df,
                                        data,
                                        data_type="validation",
                                        add_timetag=self._conf.data.validation_add_timetag,
                                        add_version=self._conf.model.version_activate,
                                        version_name=self._conf.model.version_version_name,
                                        version_column_name=self._conf.model.version_column_name
                                        )

            self.handle_shap(mdl, validation_manager.data, tag)

    def predict_test(self):
        """Use the trained models to make predictions. Making predictions are performed by iterating through the
        test dataset. The test dataset can be very large and we process it in chunks.

        :return: None
        """
        test_manager = TestDataManager(self._conf, self.processor, self.feature_engineering)
        reader = test_manager.get_reader()

        num_chunks = 0
        for index, chunk in enumerate(reader):
            num_chunks += 1
            test_data = test_manager.get_reader_data(chunk)

            for tag, mdl in self.models_dict.items():
                predictor = getattr(sys.modules[__name__], self._conf.engine + "Predictor")(mdl, self._conf)

                prediction_df, data = predictor.make_predictions(test_data,
                                                                 data_type="test",
                                                                 column_name=self._conf.data.test_column_name,
                                                                 prediction_type=self._conf.data.test_prediction_type)

                predictor.write_predictions(tag,
                                            prediction_df,
                                            data,
                                            index,
                                            data_type="test",
                                            add_timetag=self._conf.data.test_add_timetag,
                                            add_version=self._conf.model.version_activate,
                                            version_name=self._conf.model.version_version_name,
                                            version_column_name=self._conf.model.version_column_name)
                self.handle_shap(mdl, test_data, tag)

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, self.models_dict)

    @timeit("validate the output")
    def validate_output(self):
        """Validate the predictions and the files created by the engine.

        :return: None
        """
        if self._conf.validation.validate and self._conf.data.test_prediction_activate:
            output_validator = OutputValidator(self.conf, self.models_dict)
            output_validator.validate()

    @timeit("compute the predictions scores")
    def score_prediction(self):
        """Score the predictions using the validation dataset. Please note that we cannot score the models using test
        data because the test data does not have the target column.

        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Computing the prediction scores...")
            scorer = getattr(scoring_manager, self._conf.engine + "Scorer")(self.conf, self.models_dict, self.processor)
            scorer.score()

    @timeit("combine the predictions scores")
    def combine_predictions(self, sep_timetag, models_dict):
        """Combine the predictions of multiple models if requested. Please note that we can combine the predictions
        made on validation or test data. Here we check what was requested by user.

        :param sep_timetag:
        :param models_dict:
        :return:
        """
        if self._conf.combine.mean_activate:
            if self._conf.data.validation_score_activate:
                logging.info("Combining the predictions of different models using 'mean' method and validation data")
                combiner = getattr(combining_manager, f"Mean{self._conf.engine}Combiner")(self.conf, models_dict,
                                                                                          sep_timetag,
                                                                                          data_type="validation")
                combiner.combine()

            if self._conf.data.test_prediction_activate:
                logging.info("Combining the predictions of different models using 'mean' method and test data")
                combiner = getattr(combining_manager, f"Mean{self._conf.engine}Combiner")(self.conf, models_dict,
                                                                                          sep_timetag,
                                                                                          data_type="test")
                combiner.combine()

        if self._conf.combine.triad_activate:
            logging.info("Combining the predictions of different models using 'triad' method and validation data")
            if self._conf.data.validation_score_activate:
                if not self.combiner:
                    # triad method is only supported for regressor engines. We should never get here with classifier
                    # engine
                    self.combiner = TriadCombiner(self.conf, models_dict, sep_timetag)
                    self.combiner.fit()
                else:
                    self.combiner.transform(data_type="validation")

            if self._conf.data.test_prediction_activate:
                logging.info("Combining the predictions of different models using 'triad' method and test data")
                if not self.combiner:
                    logging.critical("It looks like combiner is not loaded. Exiting...")
                    sys.exit(1)

                self.combiner.transform(data_type="test")

    def handle_shap(self, mdl, data, tag):
        """Instantiate appropriate objects and call the necessary methods to perform various analysis.

        :param mdl: an trained model
        :param data: a pandas dataframe. This could be validation or test datasets
        :param tag: the model tag in the models_dict
        :return: None
        """
        if self._conf.analysis.shap_activate:
            shap = Shap(mdl, self._conf, self.processor)
            shap.run_shap(data, tag)

    def handle_predictions_vs_actuals(self, models_dict):
        """Accept a models_dict, iterate through it, and call handle_predictions_vs_actuals_plot method in the
        Analysis class tp plot predictions vs actuals graph. The handle_predictions_vs_actuals_plot method will
        figure out where the prediction and actual data are located.

        :param models_dict: a models_dict. This dictionary is a complete dictionary not only one item.
        :return: None
        """
        if self._conf.analysis.predictions_vs_actuals_activate:
            logging.info("Plotting predictions vs actuals...")
            analysis = Analysis(self._conf)
            for tag, mdls in models_dict.items():
                mdl = mdls.get(0, mdls)
                analysis.handle_predictions_vs_actuals_plot(tag, mdl)

    @staticmethod
    def filter_data(data, column_name, border):
        """Filter the training data based on the value in a train_name column that matches segment border.

        :param data: the data to be filtered
        :param column_name: the name of the column to use to filter the data, this could be train_name or test_name in segmenters.
        :param border: segment border
        :return: filtered data
        """
        filtered_data = filter_data(data, column_name, border, '==')
        return filtered_data



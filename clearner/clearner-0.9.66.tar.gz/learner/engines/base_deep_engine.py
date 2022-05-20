# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the base classes for deep engines. We typically do not instantiate this base classes. We have
moved the base deep class into a separate class to make things a bit more clear"""

import logging
import os
import sys

import torch
import pandas as pd

from learner.analysis.analysis import Analysis
from learner.configuration.configuration import Configuration
from learner.data_worker.deep_tabular_data_manager import TrainDataManager, ValidationDataManager, TestDataManager
from learner.data_worker.output_handler import OutputHandler
from learner.model_manager.model_initializer import ModelInitializer, get_pickle_dir
from learner.model_manager.deep_classifiers import DeepClassifierHandler
from learner.model_manager.deep_regressors import DeepRegressorHandler
from learner.model_manager.prediction_manager import DeepClassifierPredictor, DeepRegressorPredictor
from learner.utilities.timer import timeit
from learner.validator.output_validator import OutputValidator


class BaseDeep(ModelInitializer, TrainDataManager):
    """The base class for tabular deep learning engines including DeepClassifier and DeepRegressor. This class implement
    most of the methods for these engines because they are highly similar. Please note that engine_manager does not
    instantiate this class.
    """
    def __init__(self, conf: Configuration):
        """Instantiate an object of the BaseDeep class using an instance of the Configuration class

        :param conf: an object of the Configuration class
        """
        super(BaseDeep, self).__init__(conf)
        super(ModelInitializer, self).__init__(conf)

        self.conf.model.nrows_score = 0
        # this will hold information about all models as opposed to a single model. This is used to combine the
        # predictions of multiple models
        self.loaded_models_dict = {}

    @timeit("build the model(s)")
    def run_engine(self):
        """The main method that communicates with other methods to drive the engine.

        :return: None
        """
        if self._conf.model.train_models:
            self.train_models()
            self.predict()
        else:
            logging.info("Loading saved model...")
            self.load_models(self._conf.workspace.path)

        self.validate_output()

    @timeit("train the model(s)")
    def train_models(self):
        """Loop through all the items in models_dict and call the train_models method to train each model.

        :return: None
        """
        logging.info("Building the models...")
        for tag, mdl in self.models_dict.items():
            logging.info(f"Fitting {tag} model")
            # train the model and save it into model dictionary
            # depending on the user input, either do grid_search, cross_validation, or a single fit
            self.fit_models(tag, mdl)

    def fit_models(self, tag, mdl):
        """Call appropriate methods to find the learning rate or fit the model. There are a lot of similarities
        between this method and the method in for image_classifier engines. We need to maintain that consistency.

        :param tag: the tag of the model (arbitrary tag defined by user)
        :param mdl: an items in models_dict
        :return: None
        """
        train_data_manager = TrainDataManager(self.conf, mdl)
        train_loader = train_data_manager.get_data_loader()
        validation_loader = None

        # we need this assignment because we'll need it if we want to make predictions right away
        self.processor = train_data_manager.processor
        self.feature_engineering = train_data_manager.feature_engineering
        if self._conf.data.validation_score_activate:
            validation_data_manager = ValidationDataManager(self.conf,
                                                            mdl,
                                                            processor=self.processor,
                                                            feature_engineering=self.feature_engineering)
            validation_loader = validation_data_manager.get_data_loader()

        if self._conf.model.lr_activate:
            logging.info("Finding the learning rate...")
            mdl["model"] = getattr(sys.modules[__name__], self._conf.engine + "Handler").\
                learner_find_learning_rate(tag=tag,
                                           mdl=mdl,
                                           conf=self.conf,
                                           train_loader=train_loader)
        else:
            mdl["model"] = getattr(sys.modules[__name__], self._conf.engine + "Handler").\
                learner_fit(tag=tag,
                            mdl=mdl,
                            conf=self.conf,
                            train_loader=train_loader,
                            validation_loader=validation_loader)

    @timeit("make predictions using the trained model(s)")
    def predict(self):
        """Call predict_test if we need to make predictions on test data. Scoring the validation data happens as we
        train the models.

        :return: None
        """
        if self._conf.data.test_prediction_activate:
            logging.info("Making predictions using test data...")
            self.predict_test()

    @timeit("make predictions using the trained model(s)")
    def predict_test(self):
        """Load the test data in chunks and make predictions. This method instantiates the predictor class of the
        engine and calls make_predictions method on them. To make sure, we can make predictions on the dataset of
        any sizes, we implement a nested loop here. First, we get a data reader object. We then load a chunk of data
        and pass it to the get_data_loader to obtain a data_loader object. A confusing thing here could be saving the
        output. As you can see, we use the output handler for segmentation to save the predictions and do the
        concatenation. This is because, similar to segmentation, we are using nested loops and dealing with two
        dimensional output matrices namely chunks and batches. We can think of a chunk index like segment index, and
        the batch index like the chunk index in the segmentation. We may need to update the underlying output handler
        classes in the future to remove some of the confusions.

        :return: None
        """
        test_data_manager = TestDataManager(self._conf, self.processor, self.feature_engineering)
        reader = test_data_manager.get_reader()

        num_chunks = 0
        output = OutputHandler(self._conf, data_type="test")
        for reader_index, chunk in enumerate(reader):
            chunk = test_data_manager.get_reader_data(chunk)
            num_chunks += 1
            for tag, mdl in self.models_dict.items():
                data_loader = test_data_manager.get_data_loader(chunk, mdl)
                for loader_index, (X, data) in enumerate(data_loader):
                    # data will be a dictionary ready to be converted to a dataframe
                    data = pd.DataFrame(data=data)
                    predictor = getattr(sys.modules[__name__], self._conf.engine + "Predictor")(mdl, self._conf)
                    prediction_df, data = predictor.make_predictions(X,
                                                                     data,
                                                                     data_type="test",
                                                                     column_name=self._conf.data.test_column_name,
                                                                     prediction_type=self._conf.data.test_prediction_type)

                    predictor.write_predictions(tag,
                                                prediction_df,
                                                data,
                                                seg_id=reader_index,
                                                index=loader_index,
                                                mdl=mdl,
                                                data_type="test",
                                                add_timetag=self.conf.data.test_add_timetag,
                                                add_version=self.conf.model.version_activate,
                                                version_name=self.conf.model.version_version_name,
                                                version_column_name=self.conf.model.version_column_name
                                                )
                # we stitch the chunks from dataloader together
                output.concat_chunk_csv(len(data_loader), {tag: mdl}, seg_id=reader_index)
            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output.concat_chunk_csv(num_chunks, self.models_dict)

    @timeit("load the model(s)")
    def load_models(self, output_path):
        """Load saved models from the provided path if full directory is provided. Otherwise, find and load the latest
        saved models. Here, we also make the call to the combine_predictions method.

        :param output_path: directory path to the saved models
        :return: None
        """
        _, pickled_file_names, _ = get_pickle_dir(output_path, ext="pth")
        # this is to prevent IDEs from complaining
        sep_timetag = ""
        for file_name in pickled_file_names:
            checkpoint = torch.load(file_name)
            self.models_dict = {checkpoint["tag"]: checkpoint["mdl"]}
            self.loaded_models_dict[checkpoint["tag"]] = self.models_dict[checkpoint["tag"]]
            checkpoint["conf"].sep_timetag = self.conf.sep_timetag
            # we want to use the current data parameters
            checkpoint["conf"].data = self._conf.data
            # we want to use the current combine parameters
            checkpoint["conf"].combine = self._conf.combine
            self.processor = checkpoint["processor"]
            self.feature_engineering = checkpoint["feature_engineering"]
            self._conf = checkpoint["conf"]
            self.predict()

    @timeit("validate the output")
    def validate_output(self):
        """Validate the predictions and the files created by the engine. Currently, we only validate the number of
        predictions to make sure it's consistent with the original test data.

        :return: None
        """
        if self._conf.validation.validate and self._conf.data.test_prediction_activate:
            output_validator = OutputValidator(self.conf, self.models_dict)
            output_validator.validate()

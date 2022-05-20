# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the ImageClassifier engine."""
import os
import logging
import pandas as pd
import torch

from learner.utilities.timer import timeit
from learner.configuration.configuration import Configuration
from learner.data_worker.image_data_manager import TrainDataManager, ValidationDataManager, TestDataManager
from learner.model_manager.image_classifiers import ImageClassifierHandler
from learner.model_manager.model_initializer import get_pickle_dir
from learner.model_manager.prediction_manager import ImageClassifierPredictor
from learner.data_worker.output_handler import OutputHandler


class ImageClassifier:
    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a image_classifier engine.

        :param conf: a conf object
        """
        self._conf = conf
        # we are not using model_initializer here but I do this to keep things consistent with other engines
        self.models_dict = self.conf.model.models_dict
        self.conf.model.nrows_score = 0

    @property
    def conf(self):
        return self._conf

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

    @timeit("train the model(s)")
    def train_models(self):
        """Loop through all the items in models_dict and call the train_models method to train each model. Note that,
        unlike other engines, saving the model happens during the training.

        :return: None
        """
        logging.info("Building the models...")
        for tag, mdl in self.conf.model.models_dict.items():
            logging.info(f"Fitting {tag} model")
            self.fit_models(tag, mdl)

    def fit_models(self, tag, mdl):
        """Get the train and validation (if needed) data loaders. Then, call the appropriate methods to train the
        models. Currently, we only fit the models but we'll probably implement learning rate finder soon.

        :param tag: the tag of the model (arbitrary tag defined by the user)
        :param mdl: an items in models_dict
        :return: None
        """
        train_data_manager = TrainDataManager(self.conf, mdl)
        train_loader = train_data_manager.get_data_loader()
        validation_loader = None
        if self._conf.data.validation_score_activate:
            validation_data_manager = ValidationDataManager(self.conf, mdl)
            validation_loader = validation_data_manager.get_data_loader()

        if self._conf.model.lr_activate:
            logging.info("Finding the learning rate...")
            mdl["model"] = ImageClassifierHandler.learner_find_learning_rate(tag=tag,
                                                                             mdl=mdl,
                                                                             conf=self.conf,
                                                                             train_loader=train_loader)
        else:
            mdl["model"] = ImageClassifierHandler.learner_fit(tag=tag,
                                                              mdl=mdl,
                                                              conf=self.conf,
                                                              train_loader=train_loader,
                                                              validation_loader=validation_loader)

    @timeit("load the model(s)")
    def load_models(self, output_path):
        """Load saved models from the provided path if full directory is provided. Otherwise, find and load the latest
        saved models.

        :param output_path: directory path to the saved models
        :return: None
        """
        _, pickled_file_names, _ = get_pickle_dir(output_path, ext="pth")
        for file_name in pickled_file_names:
            checkpoint = torch.load(file_name)
            self.models_dict = {checkpoint["tag"]: checkpoint["mdl"]}
            checkpoint["conf"].sep_timetag = self.conf.sep_timetag
            # we want to use the current data parameters
            checkpoint["conf"].data = self._conf.data
            # we want to use the current combine parameters
            checkpoint["conf"].combine = self._conf.combine
            self._conf = checkpoint["conf"]
            self.predict()

    @timeit("make predictions using the trained model(s)")
    def predict(self):
        """Call predict_test if we need to make predictions on test data. Unlike other engines, scoring the validation
        data happens during training.

        :return: None
        """
        if self._conf.data.test_prediction_activate:
            logging.info("Making predictions using test data...")
            self.predict_test()

    def predict_test(self):
        """Use the trained models (stored in models_dict) to make predictions. Making predictions are performed by
        iterating through the test dataset. As it happens, there are a lot of similarities between image_classifier and
        other non-deep learning engines.

        :return: None
        """
        test_data_manager = TestDataManager(self.conf, mdl=None)
        test_loader = test_data_manager.get_data_loader()

        # we probably don't need to keep track of the num_chunks because we can get it from the length of data loader
        # but I think this is fine.
        num_chunks = 0
        for index, (X, data) in enumerate(test_loader):
            # data will be a dictionary ready to be converted to a dataframe
            data = pd.DataFrame(data=data)
            num_chunks += 1

            for tag, mdl in self.models_dict.items():
                predictor = ImageClassifierPredictor(mdl, self._conf)
                prediction_df, data = predictor.make_predictions(X,
                                                                 data,
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
                                            version_column_name=self._conf.model.version_column_name
                                            )

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += X.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, self.models_dict)

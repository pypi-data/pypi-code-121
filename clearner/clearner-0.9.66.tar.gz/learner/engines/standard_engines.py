# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for standard engines. A standard engine include classifier and regressor engines."""

import logging

from learner.data_worker.data_manager import TestDataManager, ValidationDataManager
from learner.model_manager.model_initializer import ModelLoader, get_pickle_dir
from learner.model_manager import prediction_manager
from learner.data_worker.output_handler import OutputHandler, pickle_object
from learner.engines.base_standard_engine import BaseStandard
from learner.utilities.timer import timeit
from learner.configuration.configuration import Configuration
from learner.analysis.analysis import Analysis
from learner.utilities.templates import (SAVE_MODEL_PATH, FEATURE_IMPORTANCE_PATH,
                                         SAVE_MODEL_PATH_SEG, FEATURE_IMPORTANCE_PATH_SEG,
                                         LOAD_MODEL_PATH_SEG)


class StandardEngine(BaseStandard):
    """The standard engine class without support for segmentation."""

    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a standard engine.

        :param conf: a conf object
        """
        super(StandardEngine, self).__init__(conf)
        self._drop_cols = self._conf.column.drop_from_train + [self._conf.column.target_col]

    @timeit("build the model(s)")
    def run_engine(self):
        """The main function for driving the engine.

        :return: None
        """
        if self._conf.model.train_models:
            self.train_models()
            self.predict()
            self.score_prediction()
            self.combine_predictions(self.conf.sep_timetag, self.models_dict)
        else:
            self.load_models(self._conf.workspace.path)

        self.validate_output()
        self.handle_predictions_vs_actuals(self.models_dict or self.loaded_models_dict)

    @timeit("train the model(s)")
    def train_models(self):
        """Train and potentially optimize models based on the user input

        :return: None
        """
        logging.info("Building the models...")
        for tag, mdl in self.models_dict.items():
            logging.info("Fitting %s model", tag)
            # train the model and save it into model dictionary
            # depending on the user input, either do grid_search, cross_validation, or a single fit
            self.fit_models(self.data, mdl, self._drop_cols)

            # save models
            if self._conf.model.save_models:
                filename = SAVE_MODEL_PATH.format(
                    path=self._conf.model.models_dict[tag]["path"],
                    output_name=self._conf.workspace.name,
                    tag=tag,
                    sep_timetag=str(self._conf.sep_timetag),
                    ext=".sav"
                )
                pickle_object(self.conf, self._conf.model.models_dict[tag]["path"], filename, dict({tag: mdl}),
                              self.processor, self.feature_engineering)

            # handle feature importance if requested
            if self._conf.analysis.importance_activate:
                analysis = Analysis(self._conf)
                filename = FEATURE_IMPORTANCE_PATH.format(
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    sep_timetag=str(self._conf.sep_timetag)
                )
                analysis.handle_feature_importance(mdl, filename)


class StandardEngineSegment(BaseStandard):
    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a standard engine with support for segmentation.

        :param conf: a conf object
        """
        super().__init__(conf)
        self._drop_cols = self._conf.column.drop_from_train + [self._conf.column.target_col] + \
            [self._conf.segmenter.test_name] + [self._conf.segmenter.test_col]

    @timeit("build the model(s)")
    def run_engine(self):
        """The main function for driving the engine.

        :return: None
        """
        if self._conf.model.train_models:
            for seg_id, border in enumerate(self._conf.segmenter.seg_list):
                train_data = self.filter_data(self.data, self._conf.segmenter.train_name, border)
                self.train_models(seg_id, border, train_data)
                self.predict(seg_id, border)
        else:
            logging.info("Loading saved model...")
            self.load_models(self._conf.workspace.path)

        if self._conf.workspace.concat_output and self._conf.data.test_prediction_activate:
            output = OutputHandler(self._conf, data_type="test")
            output.concat_save_csv(self._conf.model.models_dict, self._conf.segmenter.seg_list,
                                   self._conf.workspace.name, self._conf.sep_timetag)

        if self._conf.workspace.concat_output and self._conf.data.validation_score_activate:
            output = OutputHandler(self._conf, data_type="validation")
            output.concat_save_csv(self._conf.model.models_dict, self._conf.segmenter.seg_list,
                                   self._conf.workspace.name, self._conf.sep_timetag)

        if self._conf.validation.validate and self._conf.data.test_prediction_activate:
            self.validate_output()

        self.handle_predictions_vs_actuals(self.models_dict or self.loaded_models_dict)
        self.score_prediction()

    @timeit("train the classification model(s)")
    def train_models(self, seg_id, seg_border, train_data):
        """Train and potentially optimize models based on the user input.

        :param seg_id: segment id
        :param seg_border: upper boundary of the segment
        :param train_data: the training data
        :return: None
        """
        logging.info("**************************************************************************")
        logging.info("Training model on segment_id: %i, segment_border: %s", seg_id, seg_border)
        logging.info("There are %i rows of data in this segment", train_data.shape[0])

        for tag, mdls in self.models_dict.items():
            mdl = mdls[seg_id]
            logging.info("Fitting %s model", tag)
            drop_cols = self._drop_cols + [self._conf.segmenter.train_name]
            self.fit_models(train_data, mdl, drop_cols)

            # save models
            if self._conf.model.save_models:
                filename = SAVE_MODEL_PATH_SEG.format(
                    path=mdl["path"],
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    seg_id=str(seg_id),
                    sep_timetag=str(self._conf.sep_timetag),
                    ext=".sav"
                )

                pickle_object(self.conf, mdl["path"], filename, dict({tag: mdl}),
                              self.processor, self.feature_engineering)

            # handle feature importance if requested
            if self._conf.analysis.importance_activate:
                analysis = Analysis(self._conf)
                filename = FEATURE_IMPORTANCE_PATH_SEG.format(
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    seg_id=str(seg_id),
                    sep_timetag=str(self._conf.sep_timetag)
                )
                analysis.handle_feature_importance(mdl, filename)

    @timeit("load the model(s)")
    def load_models(self, output_path):
        """Load pickled object from path_to_pickle if full directory is provided. Otherwise, it loads the latest pickled
         object.

        :param output_path: directory path to the pickled object
        :return: None
        """
        paths_to_pickle_dir, sample_pickle_files, prefixes = get_pickle_dir(output_path)

        loader = ModelLoader(self._conf)

        nrows_score = 0

        for path_to_pickle_dir, sample_pickle_file, prefix in zip(paths_to_pickle_dir, sample_pickle_files, prefixes):

            self._conf, self.models_dict, self.processor, self.feature_engineering, sep_timetag = loader.load_model(sample_pickle_file)

            for seg_id, seg_border in enumerate(self._conf.segmenter.seg_list):
                logging.info("**************************************************************************")
                logging.info("Making predictions for segment_id: %i, segment_border: %s", seg_id, seg_border)
                filename = LOAD_MODEL_PATH_SEG.format(
                    path=path_to_pickle_dir,
                    prefix=prefix,
                    seg_id=str(seg_id),
                    sep_timetag=str(sep_timetag),
                    ext=".sav"
                )

                self._conf, self.models_dict, self.processor, self.feature_engineering, sep_timetag = loader.load_model(filename)

                tag = next(iter(self.models_dict))
                self.loaded_models_dict[tag] = self.models_dict[tag]

                self.predict(seg_id, seg_border)

                # we need to make sure we add the number of predictions from all the segments
                nrows_score += self._conf.model.nrows_score

        # we need to assign the total number of predictions for later validation
        # we also don't want to double count if we have multiple models
        self._conf.model.nrows_score = nrows_score / len(paths_to_pickle_dir)

    @timeit("make predictions using the trained model(s)")
    def predict(self, seg_id=None, seg_border=None):
        """Call predict_validation if we need to score the models using validation data and call predict_test if we
        need to make predictions on test data.

        :param seg_id: segment id
        :param seg_border: the upper boundary of the segment
        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Making predictions using validation data")
            self.predict_validation(seg_id, seg_border)
        if self._conf.data.test_prediction_activate:
            logging.info("Making predictions using test data")
            self.predict_test(seg_id, seg_border)

    def predict_validation(self, seg_id=None, seg_border=None):
        """Use the trained models to make prediction on validation data. Unlike test data, the entire validation data
        is loaded in memory when making predictions on validation data.

        :param seg_id: segment id
        :param seg_border: the upper boundary of the segment
        :return: None
        """
        validation_manager = ValidationDataManager(self._conf, self.processor, self.feature_engineering)
        validation_data = self.filter_data(validation_manager.data, self._conf.segmenter.test_name, seg_border)
        for tag, mdls in self.models_dict.items():
            mdl = mdls.get(seg_id, mdls)

            predictor = getattr(prediction_manager, self._conf.engine + "SegmentPredictor")(mdl, self._conf)
            prediction, data = predictor.make_predictions(validation_data,
                                                          data_type="validation",
                                                          column_name=self._conf.data.validation_column_name,
                                                          prediction_type=self._conf.data.validation_prediction_type)
            predictor.write_predictions(tag,
                                        prediction,
                                        data,
                                        mdl=mdl,
                                        seg_id=seg_id,
                                        data_type="validation",
                                        add_version=self._conf.model.version_activate,
                                        version_name=self._conf.model.version_version_name,
                                        version_column_name=self._conf.model.version_column_name
                                        )

    def predict_test(self, seg_id=None, seg_border=None):
        """Use the trained models to make predictions. Making predictions are performed by iterating through the
        test dataset. The test dataset can be very large and we process it in chunks.

        :param seg_id: the seg id
        :param seg_border: the upper boundary of the seg
        :return: None
        """
        test_manager = TestDataManager(self._conf, self.processor, self.feature_engineering)
        reader, indices = test_manager.get_reader_for_segment(self._conf.segmenter.test_col, seg_border)

        num_chunks = 0
        low_limit = 0
        for index, chunk in enumerate(reader):
            num_chunks += 1
            high_limit = low_limit + chunk.shape[0]
            select_rows = indices[(indices < high_limit) & (indices >= low_limit)]
            low_limit += chunk.shape[0]
            chunk = chunk.loc[select_rows, :]

            test_data = test_manager.get_reader_data(chunk)

            for tag, mdls in self.models_dict.items():
                mdl = mdls.get(seg_id, mdls)

                predictor = getattr(prediction_manager, self._conf.engine + "SegmentPredictor")(mdl, self._conf)
                prediction, data = predictor.make_predictions(test_data,
                                                              data_type="test",
                                                              column_name=self._conf.data.test_column_name,
                                                              prediction_type=self._conf.data.test_prediction_type)
                predictor.write_predictions(tag,
                                            prediction,
                                            data,
                                            index,
                                            mdl,
                                            seg_id=seg_id,
                                            data_type="test",
                                            add_version=self._conf.model.version_activate,
                                            version_name=self._conf.model.version_version_name,
                                            version_column_name=self._conf.model.version_column_name
                                            )

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, self.models_dict, seg_id)

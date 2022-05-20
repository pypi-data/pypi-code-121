# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module to drive a recommender engine."""

import logging

from learner.data_worker.data_processor import DataProcessor, handle_label_encoding, filter_data
from learner.model_manager.similarities import Similarities
from learner.model_manager.classifiers import ClassifierHandler
from learner.data_worker.data_manager import TestDataManager, ValidationDataManager
from learner.model_manager.model_initializer import ModelLoader, get_pickle_dir
from learner.model_manager.prediction_manager import RecommenderSegmentPredictor
from learner.data_worker.output_handler import OutputHandler
from learner.data_worker.output_handler import pickle_object
from learner.engines.base_standard_engine import BaseStandard
from learner.utilities.timer import timeit
from learner.analysis.analysis import Analysis
from learner.utilities.templates import FEATURE_IMPORTANCE_PATH, FEATURE_IMPORTANCE_PATH_SEG, LOAD_MODEL_PATH_SEG


class BaseRecommender(BaseStandard):
    """The BaseRecommender class that implements the methods shared by all recommender engines."""

    def __init__(self, conf):
        super().__init__(conf)

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
            mdl["model"] = ClassifierHandler.learner_grid_search(train_data.drop(drop_cols, axis=1),
                                                                 train_data[self._conf.column.target_col],
                                                                 mdl,
                                                                 self._conf.model.gs_kfold_params,
                                                                 self._conf.model.gs_options)
        elif self._conf.model.cv_activate:  # pragma: no cover
            mdl["model"] = ClassifierHandler.learner_cross_validation(train_data.drop(drop_cols, axis=1),
                                                                      train_data[self._conf.column.target_col],
                                                                      mdl,
                                                                      self._conf.model.cv_kfold_params,
                                                                      self._conf.model.cv_options)

        else:
            mdl["model"] = ClassifierHandler.learner_fit(train_data.drop(drop_cols, axis=1),
                                                         train_data[self._conf.column.target_col],
                                                         mdl)

    def get_mlb_sim_matrix(self, train_data):
        """Compute the items that are needed for training and making predictions.

        :return: the updated training data, mlb data, mlb object, and le object
        """
        # get the min support
        min_support = RecommenderHelper.get_min_support(train_data,
                                                        self._conf.column.target_col,
                                                        self._conf.recommender.support_cutoff,
                                                        self._conf.recommender.max_num_category)
        # apply the length and support constraints to filter the data for training
        train_data = RecommenderHelper.apply_length_support_constraint(train_data,
                                                                       self._conf.column.target_col,
                                                                       self._conf.recommender.max_length,
                                                                       self._conf.recommender.min_length,
                                                                       min_support)

        # perform a multilabel binarization of the target for computing similarity scores and extension
        # note that these calculations are done here because the target will be label encoded for training
        mlb_data, mlb_obj = DataProcessor.multilabel_binarizer(train_data,
                                                               self._conf.column.target_col,
                                                               self._conf.column.id_cols)

        # compute the similarity matrix
        sim_matrix = Similarities.compute_similarities(mlb_data[mlb_obj.classes_],
                                                       self._conf.similarities.metric,
                                                       return_dataframe=True,
                                                       cols=mlb_obj.classes_)

        train_data, le = handle_label_encoding(train_data, [self._conf.column.target_col])

        return train_data, mlb_data, mlb_obj, sim_matrix, le


class Recommender(BaseRecommender):
    def __init__(self, conf):
        """Take a conf object (from the Configuration class) to run a recommender engine without support for segmentation.

        :param conf: a conf object
        """
        super().__init__(conf)
        # set the cols that must be dropped from train data
        self._drop_cols = self._conf.column.drop_from_train + [self._conf.column.target_col]

    @timeit("build the models")
    def run_engine(self):
        """The main function for driving the recommender engine

        :return: None
        """
        logging.info("Building the recommendation models...")
        if self._conf.model.train_models:
            train_data, mlb_data, mlb_obj, sim_matrix, le = self.prepare_train_get_mlb_sim_matrix()
            self.train_models(train_data, mlb_data, mlb_obj, sim_matrix, le)
            self.predict()
        else:
            logging.info("Loading saved model...")
            self.load_models(self._conf.workspace.path)

        if self._conf.validation.validate and self._conf.data.test_prediction_activate:
            self.validate_output()

    @timeit("train the recommendation model(s)")
    def train_models(self, train_data, mlb_data, mlb_obj, sim_matrix, le):
        """Train a classifier for the recommender engine.

        :param train_data: the training dataset
        :param mlb_data: the data that is obtained from MultiLabelBinarizer
        :param mlb_obj: the MultiLabelBinarizer object
        :param sim_matrix: the similarity matrix obtained from similarity calculations
        :param le: the LabelEncoder object
        :return: None
        """
        logging.info("Building the models...")

        for tag, mdl in self.models_dict.items():
            logging.info("Fitting %s model", tag)

            _, mdl["mlb_obj"], mdl["sim_matrix"], mdl["le"] = mlb_data, mlb_obj, sim_matrix, le
            # train the model and save it into model dictionary
            # depending on the user input, either do grid_search, cross_validation, or a single fit
            self.fit_models(train_data, mdl, self._drop_cols)

            # save models
            if self._conf.model.save_models:
                file_name = self._conf.model.models_dict[tag]["path"] + self._conf.workspace.name + "_" + str(tag) \
                            + str(self._conf.sep_timetag) + ".sav"

                pickle_object(self.conf, self._conf.model.models_dict[tag]["path"], file_name, dict({tag: mdl}),
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

    def prepare_train_get_mlb_sim_matrix(self):
        """Prepare the training dataset and compute the items that are needed for training and making predictions.

        :return: the updated training data, mlb data, mlb object, and le object
        """
        return self.get_mlb_sim_matrix(self.data)


class RecommenderSegment(BaseRecommender):
    def __init__(self, conf):
        """Take a conf object (from the Configuration class) to run a recommender engine with support for segmentation.

        :param conf: a conf object
        """
        super().__init__(conf)
        self._drop_cols = self._conf.column.drop_from_train + [self._conf.column.target_col] + \
            [self._conf.segmenter.test_name] + [self._conf.segmenter.test_col]

    @timeit("build the models")
    def run_engine(self):
        """The main function for driving the engine.

        :return: None
        """
        logging.info("Building the recommendation models...")
        if self._conf.model.train_models:
            for seg_id, border in enumerate(self._conf.segmenter.seg_list):
                train_data, mlb_data, mlb_obj, sim_matrix, le = self.prepare_train_get_mlb_sim_matrix(border)
                self.train_models(seg_id, border, train_data, mlb_data, mlb_obj, sim_matrix, le)

                self.predict(seg_id, border)
        else:
            logging.info("Loading saved model...")
            self.load_models(self._conf.workspace.path)

        # concatenate the output and write the results into a single file
        if self._conf.workspace.concat_output and self._conf.data.test_prediction_activate:
            output = OutputHandler(self._conf, data_type="test")
            output.concat_save_csv(self._conf.model.models_dict, self._conf.segmenter.seg_list,
                                   self._conf.workspace.name, self._conf.sep_timetag)

        if self._conf.validation.validate and self._conf.data.test_prediction_activate:
            self.validate_output()

    @timeit("train the recommendation model(s)")
    def train_models(self, seg_id, seg_border, train_data, mlb_data, mlb_obj, sim_matrix, le):
        """Train a classifier for the recommender engine.

        :param seg_id: the seg id
        :param seg_border: the upper boundary of the seg
        :param train_data: the training dataset
        :param mlb_data: the data that is obtained from MultiLabelBinarizer
        :param mlb_obj: the MultiLabelBinarizer object
        :param sim_matrix: the similarity matrix obtained from similarity calculations
        :param le: the LabelEncoder object
        :return: None
        """
        logging.info("**************************************************************************")
        logging.info("Training model on segment_id: %i, segment_border: %s", seg_id, seg_border)
        logging.info("There are %i rows of data in this segment", train_data.shape[0])

        for tag, mdls in self.models_dict.items():
            mdl = mdls.get(seg_id, mdls)
            logging.info("Fitting %s model", tag)

            _, mdl["mlb_obj"], mdl["sim_matrix"], mdl["le"] = mlb_data, mlb_obj, sim_matrix, le
            drop_cols = self._drop_cols + [self._conf.segmenter.train_name]
            # train the model and save it into model dictionary
            # depending on the user input, either do grid_search, cross_validation, or a single fit
            self.fit_models(train_data, mdl, drop_cols)

            # save models
            if self._conf.model.save_models:
                file_name = mdl["path"] + self._conf.workspace.name + "_" + str(tag) + "_" \
                            + str(seg_id) + str(self._conf.sep_timetag) + ".sav"

                pickle_object(self.conf, mdl["path"], file_name, dict({tag: mdl}),
                              self.processor, self.feature_engineering)

            # handle feature importance if requested
            if self._conf.analysis.importance_activate:
                analysis = Analysis(self._conf)
                filename = FEATURE_IMPORTANCE_PATH_SEG.format(
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    seg_id=str(seg_id),
                    sep_timetag=str(self._conf.sep_sep_timetag)
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
            logging.info("Making predictions using validation data...")
            self.predict_validation(seg_id, seg_border)
        if self._conf.data.test_prediction_activate:
            logging.info("Making predictions using test data...")
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

            predictor = RecommenderSegmentPredictor(mdl, self._conf)
            prediction, data = predictor.make_predictions(validation_data, column_name=self._conf.data.validation_column_name)
            predictor.write_predictions(tag, prediction, data, mdl, seg_id=seg_id, data_type="validation")

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
                predictor = RecommenderSegmentPredictor(mdl, self._conf)
                prediction, data = predictor.make_predictions(test_data, column_name=self._conf.data.test_column_name)
                predictor.write_predictions(tag, prediction, data, index, mdl=mdl, seg_id=seg_id, data_type="test")

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, self.models_dict, seg_id)

    def prepare_train_get_mlb_sim_matrix(self, seg_id):
        """Prepare the training dataset and compute the items that are needed for training and making predictions

        :param seg_id: the segment id
        :return: the updated training data, mlb data, mlb object, and le object
        """
        # get the train and test data for the segment. Note that the difference is in the segmenter base and
        # test names
        train_data = filter_data(self.data, self._conf.segmenter.train_name, seg_id, '==')

        return self.get_mlb_sim_matrix(train_data)


class RecommenderHelper:
    """Handle filtering the train data for recommender engine according to inputs provided by the user"""

    @staticmethod
    def get_min_support(data, col, cutoff=.20, max_num_baskets=100):
        """cutoff : the %-age cutoff in unique combinatons of service codes (sorted by decending relative counts)

        Returns the top [100*cutoff] percent of unique basket combinations.
        example:

        idx basket  count
        1   15,32   4321
        2   32      321
        3   12,32   320
        4   4,14,32 210
        5   15      184
        6   16,32   43
        7   37      32
        8   22,32   3
        9   14,32   2
        10  19      1

        get_min_basket_support(cutoff=.20) returns 321,(indended useage) meaning that only baskets with support >= 321 will be considered "valid"


        :param data: pandas dataframe (this is usually train data
        :param col: the column to perform the calculations on (this is usually target_col
        :param cutoff: the percentage of basket to keep for training. See the above explanation
        :param max_num_baskets: maximum number of basket to include
        :return: the minimum number of frequency a basket should appear to be included in train
        """
        unique_baskets = data.groupby(col)[col].count().sort_values(ascending=False)
        threshold_idx = int(len(unique_baskets) * cutoff)
        idx = min(max_num_baskets, threshold_idx)

        return unique_baskets[idx]

    @staticmethod
    def apply_length_support_constraint(data, col, max_length, min_length, min_support):
        """Filter a dataset according to the constraints set by user for recommender engine

        :param data: pandas dataframe
        :param col: the column to use for filtering. This is usually the target_col
        :param max_length: the maximum number of items that a basket can have
        :param min_length: the minimum number of items that a basket can have
        :param min_support: the minimum_support obtained from min_support method
        :return: the filtered data frame
        """

        data = data[(data[col].apply(len) <= max_length) & (data[col].apply(len) >= min_length)]
        sorted_support = data.groupby(col).size().sort_values(ascending=False).reset_index(name='count')
        sorted_support = sorted_support[col][sorted_support['count'] >= min_support]

        return data[data[col].isin(sorted_support)]

# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Process a data set such as converting specific columns to numeric values, imputing the missing values, etc.
The module provides several static methods."""

import sys
import re
import multiprocessing
from functools import partial
import warnings
import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import MultiLabelBinarizer
from nltk.tokenize.treebank import TreebankWordDetokenizer, TreebankWordTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.arlstem import ARLSTem
from nltk.stem.cistem import Cistem
from nltk.stem.isri import ISRIStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.regexp import RegexpStemmer
from nltk.stem.rslp import RSLPStemmer
from nltk.stem.snowball import SnowballStemmer

from learner.utilities.exclude import exclude
from learner.configuration.configuration import Configuration


class DataProcessor(object):
    def __init__(self, conf: Configuration, exclude_cols=None):
        """Initialize a DataProcessor object.

        :param conf: an instance of Configuration class, which holds all configuration parameters
        :param exclude_cols: a list of column to be excluded from processing.
        """
        self._conf = conf
        self._dummy_encoder = None
        self._label_encoder = None
        self._learner_fill_nan = None
        self._standard_scaler = None
        self._min_max_scaler = None
        self._mean_dict = {}
        self._exclude_cols = exclude_cols if exclude_cols else []
        self._col_to_tfidf_object = {}
        self._col_to_tfidf_object = {}

    @property
    def conf(self):
        return self._conf

    @property
    def dummy_encoder(self):
        return self._dummy_encoder

    @property
    def label_encoder(self):
        return self._label_encoder

    @property
    def learner_fill_nan(self):
        return self._learner_fill_nan

    @property
    def standard_scaler(self):
        return self._standard_scaler

    @property
    def min_max_scaler(self):
        return self._min_max_scaler

    @property
    def exclude_cols(self):
        return self._exclude_cols

    @exclude_cols.setter
    def exclude_cols(self, value):
        self._exclude_cols = value

    @property
    def mean_dict(self):
        return self._mean_dict

    @mean_dict.setter
    def mean_dict(self, value):
        self._mean_dict = value

    @staticmethod
    def handle_copy_cols(data, cols=None):
        """Accept a dictionary with column names and their corresponding names for copying and make a copy of them.
        This method is useful in situations that data processing may change a column but we may still need the original
        column without any changes.

        :param data: the data frame
        :param cols: a list of columns to be copied
        :return: None
        """
        for col, copy_name in cols.items():
            logging.info(f"Copying {col} to {copy_name}")
            data[copy_name] = data[col]

    @exclude(name="cols")
    def make_tuple(self, data, cols=None, exclude_list=None):
        """Turn a series of character strings containing (comma, pipe, caret: ",", "|", "^") separated integers into
        a tuple

        :param cols: column identified by a list of column names
        :param data: the data frame
        :param exclude_list: a list of items that should be excluded from cols (only the decorator function uses this)
        :return: a data frame with the column identified previously converted into a series of tuples
        """
        for col in cols:
            logging.info("Tuplizing column %s", col)
            if isinstance(data[col].iloc[0], tuple):
                logging.info("Column %s has already been tuplized", col)
            else:
                try:
                    # note that sorting is performed to speed up the process of extension later
                    data[col] = data[col].apply(
                        lambda x: tuple(sorted(list(map(int, re.split("[',','|','^']", x))))))
                except TypeError:
                    logging.exception("Column passed '%s' can't be tupilized.", col)
                    raise
        return data

    def handle_dummies(self, data, cols=None):
        """Convert categorical variables into dummy/indicator variables.

        :param data: pandas DataFrame
        :param cols: a list of columns to transform
        :return: an updated pandas DataFrame
        """
        if not self._dummy_encoder:
            self._dummy_encoder = LearnerDummyEncoder()
            return self._dummy_encoder.fit_transform(data, cols)
        else:
            return self._dummy_encoder.transform(data)

    @exclude(name="cols")
    def handle_to_numeric(self, data, cols=None, exclude_list=None):
        """Wrapper around pandas to_numeric method to convert selected columns to a numeric type.

        :param data: a pandas dataframe
        :param cols: the columns to be used for conversion. Learner uses the cat_cols defined by users for conversion.
        :param exclude_list: a list of items that should be excluded from cols (only the decorator function uses this)
        :return: updated data frame
        """
        # first check to see any num_cols is defined, if not issue a warning and return the data
        if cols:
            data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')
            return data
        warnings.warn("No columns were passed to convert to numeric datatype.", UserWarning)
        return data

    @exclude(name="cols")
    def handle_standard_scaler(self, data, cols=None, exclude_list=None):
        """Accept a pandas dataframe and list of columns to standardized those columns by removing the mean and scaling
        to unit variance, i.e. scaling the data so that the mean of the column is 0 and the standard deviation is 1.
        If the standard_scaler attribute is already populated, we use it to transform the data. This is usually the
        case when using the test data. If standard_scaler attribute is not populated, we first fit it to the data and
        then transform it. This is usually the case when training the models.

        :param data: a pandas dataframe
        :param cols: a list of column to use for scaling
        :param exclude_list: a list of items that should be excluded from cols (only the decorator function uses this)
        :return: the updated data
        """
        if cols:
            try:
                if not self.standard_scaler:
                    # try to do the scaling in-place
                    self._standard_scaler = StandardScaler(copy=False)
                    self._standard_scaler.fit(data[cols])
                    data[cols] = self._standard_scaler.transform(data[cols])
                else:
                    data[cols] = self._standard_scaler.transform(data[cols])
            except Exception as e:
                logging.critical(f"Unable to perform standard scaler for the selected columns. "
                                 f"The error is {str(e)}. Exiting...")
                sys.exit(1)
        return data

    @exclude(name="cols")
    def handle_min_max_scaler(self, data, cols=None, exclude_list=None):
        """Accept a pandas dataframe and list of columns to scale those columns between 0 and 1.
        If the min_max_scaler attribute is already populated, we use it to transform the data. This is usually the
        case when using the test data. If min_max_scaler attribute is not populated, we first fit it to the data and
        then transform it. This is usually the case when training the models.

        :param data: a pandas dataframe
        :param cols: a list of column to use for scaling
        :param exclude_list: a list of items that should be excluded from cols (only the decorator function uses this)
        :return: the updated data
        """
        if cols:
            try:
                if not self.min_max_scaler:
                    # try to do the scaling in-place
                    self._min_max_scaler = MinMaxScaler(copy=False)
                    self._min_max_scaler.fit(data[cols])
                    data[cols] = self._min_max_scaler.transform(data[cols])
                else:
                    data[cols] = self._min_max_scaler.transform(data[cols])
            except Exception as e:
                logging.critical(f"Unable to perform min_max scaler for the selected columns. "
                                 f"The error is {str(e)}. Exiting...")
                sys.exit(1)
        return data

    @exclude(name="cols")
    def handle_label_encoding(self, data, cols=None, exclude_list=None):
        """label encode selected columns.

        :param data: pandas dataframe
        :param cols: the columns to use for label encoding
        :param exclude_list: a list of items that should be excluded from cols (the decorator function uses this)
        :return: None
        """
        if not self._label_encoder:
            self._label_encoder = LearnerLabelEncoder()
            self._label_encoder.fit_transform(data, cols)

        else:
            self._label_encoder.transform(data, cols)

    def fill_nan(self, data, default_value, mean_cols, median_cols, mode_cols, value_cols):
        """Fill the missing values using LearnerFillNaN class. If learner_fill_nan is already populated, we only do
        transforms otherwise we do both fit and transform. Fit & transform usually happens during training and transform
        typically happens during testing.

        :param data: pandas dataframe
        :param default_value: a default number to use for filling missing value if no custom value is provided.
        :param mean_cols: a list of columns to be imputed using the mean of the training data
        :param median_cols: a list of columns to be imputed using the median of the training data
        :param mode_cols: a list of columns to be imputed using the mode of the training data
        :param value_cols: a dictionary that maps the column names with a value for imputation
        :return: None
        """
        if not self._learner_fill_nan:
            self._learner_fill_nan = LearnerFillNaN(default_value=default_value,
                                                    mean_cols=mean_cols,
                                                    median_cols=median_cols,
                                                    mode_cols=mode_cols,
                                                    value_cols=value_cols)
            self._learner_fill_nan.fit_transform(data)
        else:
            self._learner_fill_nan.transform(data)

    @staticmethod
    def drop_cols(data, cols=None, **kwargs):
        """Wrapper around pandas drop method for inplace dropping of certain columns

        :param data: pandas dataframe
        :param cols: the columns to be dropped
        :param kwargs: other arguments to pass to drop method such as errors, etc
        :return: None
        """
        if cols:
            data.drop(cols, axis=1, inplace=True, **kwargs)

    @staticmethod
    def date_cols(data, cols=None):
        """Process the date columns. First, convert each column to datetime object and then extract the requested items
        from them to create the new columns.

        :param data: pandas dataframe
        :param cols: the date columns to be processed
        :return: the updated dataframe with the new columns
        """
        if cols:
            for col, date_items in cols.items():
                data[col] = pd.to_datetime(data[col],
                                           errors='coerce',
                                           infer_datetime_format=True)
                for item in date_items:
                    data.loc[:, f"{col}_{item}"] = getattr(data[col].dt, item)

            return data

    def handle_mean(self, data):
        """Accept a dataframe and compute the mean of all columns in that dataframe and save them in a dictionary (mean_dict)
        in which the key is the column name and the value is the average value of that column.

        :param data: pandas dataframe
        :return: None
        """
        self.mean_dict = data.mean().to_dict()

    @staticmethod
    def multilabel_binarizer(data, target_col, other_cols=None):
        """Use pandas MultiLabelBinarizer to binarize a certain columns. The return value is a dataframe with the
        columns set using classes\_ instance member of MultiLabelBinarizer joined with any other columns (other_cols)
        asked by the user

        :param data: pandas dataframe
        :param target_col: the column to perform MultiLabelBinarizer on
        :param other_cols: other columns in the dataset that the return dataset should contain
        :return: pandas dataframe and performing binarization and pandas MultiLabelBinarizer object
        """
        # Note: A check needs to be done to make sure other_cols actually exists in the data set
        mlb = MultiLabelBinarizer(sparse_output=False)
        df = pd.DataFrame(mlb.fit_transform(data[target_col]), columns=mlb.classes_)
        if other_cols:
            return df.join(data[other_cols]), mlb
        return df, mlb

    def handle_lemmatize(self, data, params):
        """Accept a pandas dataframe and a list of dictionaries (params) to perform the text lemmatization on the
        selected columns. We run the text lemmatization is parallel. The method _perform_lemmatization handles the main
        operations for text lemmatizetion. Here, we loop through the list of pos.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param params: a list of dictionaries containing the information about the columns and list of "pos"
        :return: an updated dataframe with the lemmatized form of text columns
        """
        for param in params:
            for pos in param["pos"]:
                logging.info(f"Performing lemmatization for {param['name']} and pos={pos}")
                data = parrallelize_dataframe(data, partial(self._perform_lemmatization,
                                                            col=param["name"],
                                                            pos=pos))
        return data

    def _perform_lemmatization(self, data, col, pos):
        """This method handles the heavy lifting for the text lemmatization. For each row, it first tokenizes the text.
        Then, it lemmatizes each token in the text. Last, it detokenizes the tokens and returns the updated data.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param col: the name of the column to be lemmatized
        :param pos: the part of speech
        :return: an updated dataframe with the lemmatized form of text columns
        """
        tokenizer = TreebankWordTokenizer()
        detokenizer = TreebankWordDetokenizer()
        lemmatizer = WordNetLemmatizer()
        # here we tokenize the text, lemmatize it, and then detokenize it
        data[col] = data[col].apply(lambda x: detokenizer.detokenize(
            [lemmatizer.lemmatize(word, pos=pos) for word in tokenizer.tokenize(x)]
        ))
        return data

    def handle_stem(self, data, params):
        """Accept a pandas dataframe and a list of dictionaries (params) to perform the text stemming on the
        selected columns. We run the text stemming is parallel. The method _perform_stemming handles the main
        operations for text stemming. Here, we loop through the list of pos.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param params: a list of dictionaries containing the information about the columns, the type of semmer, and additional options
        :return: an updated dataframe with the stemmed form of text columns
        """
        for param in params:
            logging.info(f"Performing stemming for {param['name']}")
            data = parrallelize_dataframe(data, partial(self._perform_stemming,
                                                        col=param["name"],
                                                        type_=param["type"],
                                                        options=param["options"]))
        return data

    def _perform_stemming(self, data, col, type_, options):
        """This method handles the heavy lifting for the text stemming. For each row, it first tokenizes the text.
        Then, it stems each token in the text. Last, it detokenizes the tokens and returns the updated data.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param col: the name of the column to be stemmed
        :param type_: the type of stemmer
        :param options: additional options for the stemmer. This is required for some stemmers.
        :return: an updated dataframe with the stemmed form of text columns
        """
        tokenizer = TreebankWordTokenizer()
        detokenizer = TreebankWordDetokenizer()
        stemmer = getattr(sys.modules[__name__], type_)(**options)

        # here we tokenize the text, stem it, and then detokenize it
        data[col] = data[col].apply(lambda x: detokenizer.detokenize(
            [stemmer.stem(word) for word in tokenizer.tokenize(x)]
        ))
        return data

    def handle_count_vectorize(self, data, params):
        """Accept a pandas dataframe and a list of dictionaries (params) to perform the count vectorize operations on the
        selected columns. We fit and transform during the training and only transform during testing or validation. We
        get to know if we are training or testing based on the _col_to_count_vectorize_object dictionary. If this
        dictionary is None, that means we are training, otherwise we are testing/validating.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param params: a list of dictionaries containing the information about the column and bag_of_word operation
        :return: an updated dataframe with new columns for the term frequency matrix
        """
        # if _col_to_count_vectorize_object is None, we need to train
        if not self._col_to_tfidf_object:
            for param in params:
                count_vector = CountVectorizer(strip_accents=param["strip_accents"],
                                               lowercase=param["lowercase"],
                                               stop_words=param["stop_words"],
                                               token_pattern=param["token_pattern"],
                                               ngram_range=param["ngram_range"],
                                               analyzer=param["analyzer"],
                                               max_df=param["max_df"],
                                               min_df=param["min_df"],
                                               max_features=param["max_features"],
                                               binary=param["binary"])
                doc_array = count_vector.fit_transform(data[param["name"]])
                frequency_df = pd.DataFrame.sparse.from_spmatrix(data=doc_array, columns=count_vector.get_feature_names()).reset_index(drop=True)
                data = pd.concat([frequency_df, data], axis=1)
                # add the object to the dictionary to use it during testing
                self._col_to_tfidf_object[param["name"]] = count_vector
                # we need to drop the column because the training algorithms won't accept it
                self._conf.column.drop_cols.append(param["name"])
        else:
            for col, obj in self._col_to_tfidf_object.items():
                # use the pre-trained object to do the transform
                doc_array = obj.transform(data[col])
                frequency_df = pd.DataFrame.sparse.from_spmatrix(data=doc_array, columns=obj.get_feature_names())
                data = pd.concat([frequency_df, data], axis=1)
                self._conf.column.drop_cols.append(col)
        return data

    def handle_tfidf(self, data, params):
        """Accept a pandas dataframe and a list of dictionaries (params) to perform the
        tf-idf (term frequency - inverse document frequency)  operations on the
        selected columns. We fit and transform during the training and only transform during testing or validation. We
        get to know if we are training or testing based on the _col_to_tfidf_object dictionary. If this
        dictionary is None, that means we are training, otherwise we are testing/validating.

        :param data: a pandas dataframe, it could be train, validation, or test data
        :param params: a list of dictionaries containing the information about the column and bag_of_word operation
        :return: an updated dataframe with new columns for the term frequency matrix
        """
        # if _col_to_tfidf_object is None, we need to train
        if not self._col_to_tfidf_object:
            for param in params:
                tfidf_vector = TfidfVectorizer(strip_accents=param["strip_accents"],
                                               lowercase=param["lowercase"],
                                               stop_words=param["stop_words"],
                                               token_pattern=param["token_pattern"],
                                               ngram_range=param["ngram_range"],
                                               analyzer=param["analyzer"],
                                               max_df=param["max_df"],
                                               min_df=param["min_df"],
                                               max_features=param["max_features"],
                                               binary=param["binary"],
                                               norm=param["norm"],
                                               use_idf=param["use_idf"],
                                               smooth_idf=param["smooth_idf"],
                                               sublinear_tf=param["sublinear_tf"])
                doc_array = tfidf_vector.fit_transform(data[param["name"]])
                frequency_df = pd.DataFrame.sparse.from_spmatrix(data=doc_array, columns=tfidf_vector.get_feature_names()).reset_index(drop=True)
                data = pd.concat([frequency_df, data], axis=1)
                # add the object to the dictionary to use it during testing
                self._col_to_tfidf_object[param["name"]] = tfidf_vector
                # we need to drop the column because the training algorithms won't accept it
                self._conf.column.drop_cols.append(param["name"])
        else:
            for col, obj in self._col_to_tfidf_object.items():
                # use the pre-trained object to do the transform
                doc_array = obj.transform(data[col])
                frequency_df = pd.DataFrame.sparse.from_spmatrix(data=doc_array, columns=obj.get_feature_names())
                data = pd.concat([frequency_df, data], axis=1)
                self._conf.column.drop_cols.append(col)
        return data

    def memory_optimization(self, data):
        """Reduce memory usage by converting dtypes down to lowest bit size.

        There is a known bug existing in pandas where it will downcast float64 to float32. This should not have an
        impact at this time, but will need to be accounted for in the unit test.

        :param data: pandas dataframe
        :return: pandas dataframe with reduced bit scope for int columns.
        """
        logging.info("Memory Usage before optimization: %s", self.mem_usage(data))

        for col in data.columns:
            if str(data[col].dtypes).startswith("uint"):
                data[col] = pd.to_numeric(data[col], downcast='unsigned')
            if str(data[col].dtypes).startswith("int"):
                data[col] = pd.to_numeric(data[col], downcast='integer')
            if str(data[col].dtypes).startswith("float"):
                data[col] = pd.to_numeric(data[col], downcast='float')

        logging.info("Memory Usage after optimization: %s", self.mem_usage(data))
        if self._conf.workspace.verbose_level == "DEBUG":
            for col in data.columns:
                logging.info("%s: %s", col, data[col].dtype)

    @staticmethod
    def mem_usage(data):
        """Returns human readable MB usage of Dataframe

        :param data: pandas dataframe
        :return: Memory usage in MB
        """
        return "{:03.2f}MB".format(data.memory_usage().sum() / 1024 ** 2)

    @exclude(name="cols")
    def log_transform(self, data, params, cols=None, exclude_list=None):
        """Use the data and params to call the log_transform method in feature_engineering module. This is currently used
        for log transformation of the target column.

        :param data: a pandas dataframe
        :param params: a list of log_transform parameters coming from the conf object (see the configuration module for details)
        :param cols: a list of columns for log transformation. This is provided so that exclude_list can be applied to it.
        :param exclude_list: a list of items that should be excluded from cols (only the decorator function uses this)
        :return: updated data frame
        """
        if cols:
            from learner.feature_engineering.feature_engineering import FeatureEngineering
            data = FeatureEngineering.log_transform(data, params)
            # in case, we have NaN after the transformation, we use the DataValidator method to drop them
            from learner.validator.data_validator import DataValidator
            DataValidator.check_nulls_in_col(data, col=cols[0])
        return data

    @staticmethod
    def exponential_transform(data, params, cols=None):
        """Use the data and params to call the exponential_transform method in feature_engineering module. This is currently used
        for to transform back the log transformed target.

        :param data: a pandas dataframe
        :param params: a list of exponential_transform parameters coming from the conf object (see the configuration module for details)
        :param cols: a list of columns for log transformation. This is provided so that exclude_list can be applied to it.
        :return: updated data frame
        """
        if cols:
            from learner.feature_engineering.feature_engineering import FeatureEngineering
            data = FeatureEngineering.exponential_transform(data, params)
        return data

    def process_data(self, data):
        """The main function for data processing. Depending on the user's input the appropriate if blocks will execute.

        :return: conf, data, and segmenter objects
        """

        logging.info("Processing the data")

        if self._conf.column.copy_cols:
            self.handle_copy_cols(data, cols=self._conf.column.copy_cols)

        if self._conf.analysis.shap_activate and not self.mean_dict and self.conf.analysis.shap_use_training_mean:
            logging.info("Calculating the mean of each feature in training data to use in narratives...")
            self.handle_mean(data)

        if self._conf.process.tuplize_activate and self._conf.process.tuplize_cols:
            self.make_tuple(data, cols=self._conf.process.tuplize_cols, exclude_list=self._exclude_cols)

        if self._conf.process.to_numeric_activate and self._conf.process.to_numeric_cols:
            logging.info("Handling to_numeric...")
            data = self.handle_to_numeric(data, cols=self._conf.process.to_numeric_cols, exclude_list=self._exclude_cols)

        if self._conf.process.standard_scaler_activate and self._conf.process.standard_scaler_cols:
            logging.info("Handling standard scaling... ")
            data = self.handle_standard_scaler(data, cols=self._conf.process.standard_scaler_cols, exclude_list=self._exclude_cols)

        if self._conf.process.min_max_scaler_activate and self._conf.process.min_max_scaler_cols:
            logging.info("Handling min_max scaling... ")
            data = self.handle_min_max_scaler(data, cols=self._conf.process.min_max_scaler_cols, exclude_list=self._exclude_cols)

        if self._conf.process.date_cols_activate:
            logging.info("Handling date columns...")
            data = self.date_cols(data, self._conf.process.date_cols_params)

        if self._conf.process.fillnan_activate:
            logging.info("Filling missing values in the dataset...")
            self.fill_nan(data,
                          default_value=self._conf.process.fillnan_value,
                          mean_cols=self._conf.process.fillnan_mean_cols,
                          median_cols=self._conf.process.fillnan_median_cols,
                          mode_cols=self._conf.process.fillnan_mode_cols,
                          value_cols=self._conf.process.fillnan_value_cols)

        if self._conf.process.label_encoding_activate and self._conf.process.label_encoding_cols:
            logging.info("Label encoding selected columns...")
            self.handle_label_encoding(data, cols=self._conf.process.label_encoding_cols, exclude_list=self._exclude_cols)

        if self._conf.process.dummies_activate and self._conf.process.dummies_cols:
            logging.info("Handling to_dummies...")
            data = self.handle_dummies(data, cols=self._conf.process.dummies_cols)

        if self.conf.process.lemmatize_activate:
            logging.info("Lemmatizing the selected columns...")
            data = self.handle_lemmatize(data, params=self._conf.process.lemmatize_cols_params)

        if self.conf.process.stem_activate:
            logging.info("Stemming the selected columns...")
            data = self.handle_stem(data, params=self._conf.process.stem_cols_params)

        if self._conf.process.count_vectorize_activate:
            logging.info("Performing count vectorize operations for the selected columns...")
            data = self.handle_count_vectorize(data, params=self._conf.process.count_vectorize_cols_params)

        if self._conf.process.tfidf_activate:
            logging.info("Performing tfidf operations for the selected columns...")
            data = self.handle_tfidf(data, params=self._conf.process.tfidf_cols_params)

        if self._conf.column.drop_cols:
            logging.info("Dropping the selected columns...")
            self.drop_cols(data, self._conf.column.drop_cols)

        if self._conf.process.memory_optimization:
            logging.info("Running memory optimization...")
            self.memory_optimization(data)

        if self._conf.process.log_transform_target_activate:
            logging.info("Log transforming the target column...")
            self.log_transform(data, params=self._conf.process.log_transform_target_params, cols=[self._conf.column.target_col], exclude_list=self._exclude_cols)

        # set this so that the target is excluded when making predictions
        self._exclude_cols = [self._conf.column.target_col]

        logging.info("Successfully processed the data")
        return self._conf, data


class LearnerDummyEncoder:
    """LearnerDummyEncoder is a customized encoder that takes into consideration instances where the test data
    may include labels that are not present in the training data or the instances where the test data is missing some
    levels that were present in the training data. In such cases, LearnerDummyEncoder ensures that features in the training
    and testing datasets are identical. Note that LearnerDummyEncoder can accept categorical integer features as well as
    other types of categorical features."""

    def __init__(self):
        """Initialize a LearnerDummyEncoder by assigning the necessary instance attributes."""
        self._cols = None
        self._classes = set()
        self._all_cols = []

    @property
    def cols(self):
        return self._cols

    @property
    def classes(self):
        return self._classes

    @property
    def all_cols(self):
        return self._all_cols

    def fit(self, data, cols):
        """Generate classes (new column names after transformation) and transform data.

        :param data: pandas DataFrame
        :param cols: a list of columns for which to perform dummy encoding
        :return data: the updated DaraFrame
        """
        self._cols = cols
        data, self._classes, self._all_cols = self._get_classes(data, self._cols)
        return data

    def transform(self, data):
        """Transform the data using dummy encoding assuming the classes are already populated. Drop columns that were not
        present in the traning data and generate columns that are missing.

        :param data: pandas DataFrame
        :return data: an updated pandas DataFrame
        """
        if self._classes:
            data, classes, _ = self._get_classes(data, self._cols)

            missing_classes = list(self._classes - classes)
            missing_classes.sort(key=lambda x: self._all_cols.index(x))
            for col in missing_classes:
                data.insert(self._all_cols.index(col), col, 0)

            drop_cols = classes - self._classes
            data.drop(drop_cols, axis=1, inplace=True)

            return data

    def fit_transform(self, data, cols):
        """Call the fit method to process the data and get the updated data

        :param data: pandas DataFrame
        :param cols: a list of column to
        :return data: the updated DataFrame
        """
        return self.fit(data, cols)

    @staticmethod
    def _get_classes(data, cols):
        """Call pandas get_dummies method to convert categorical variables into dummy/indicator variables. Then
        create a set that contains the name of the new columns that were created as well as a list that contain all
        the columns.

        :param data: a pandas DataFrame
        :param cols: a list of columns to be converted into dummy variables
        :return: the updated DataFrame, a set containing the new columns, and a list of all columns
        """
        data = pd.get_dummies(data, prefix_sep='___', columns=cols, dummy_na=True)

        classes = set()
        columns = data.columns
        for col in cols:
            classes.update(columns[columns.str.contains(col + "___")])

        return data, classes, list(columns)


class LearnerLabelEncoder:
    """LearnerLabelEncoder is a customized label encoder that takes into consideration instances where the test data
    may include labels that are not present in the training data. In such case, new labels will be coded and added
    to a dictionary that includes all labels and their codes. This will maintain consistency in the way training
    and testing datasets are being encoded."""

    def __init__(self, encode_unique_classes=False):
        """Initialize LearnerLabelEncoder using a flag which determines how the new levels should be encoded/handled

        :param encode_unique_classes: if set to True, each unique class will have a unique code. If set to False
        all classes that don't exist in training data will be assigned a label of -1
        """
        self._labels_dict = dict()
        self._encode_unique_classes = encode_unique_classes

    @property
    def labels_dict(self):
        return self._labels_dict

    @property
    def encode_unique_classes(self):
        return self._encode_unique_classes

    def fit(self, data, cols):
        """Creates a dictionary of labels and their corresponding classes for a set of columns.

        :param data: data in pandas dataframe format
        :param cols: columns to be label encoded
        :return: None
        """
        for col in cols:
            try:
                classes = sorted(data[col].unique())
            except TypeError:
                # if we fail with the TypeError, we won't sort
                classes = data[col].unique()
            except Exception:
                # in we fail again, convert to string and sort. We do not expect to get here
                classes = sorted(data[col].astype(str).unique())
            self._labels_dict[col] = {class_value: label for label, class_value in enumerate(classes)}

    def transform(self, data, cols):
        """If LearnerLabelEncoder is already fit, checks if the test data has any labels that are not in training. If
        this is the case, update self._labels_dict (labels dictionary) to include the new label and its code. Then,
        perform transformation based on the values of labels_dict.

        :param data: data in pandas dataframe
        :param cols: columns to do transformation on
        :return: None
        """
        if self._labels_dict:
            for col in cols:
                test_classes = data[col].unique()
                diff = set(test_classes) - set(self._labels_dict[col].keys())
                max_label = max(self._labels_dict[col].values())
                if diff:
                    for new_class in diff:
                        if self._encode_unique_classes:
                            new_label = max(self._labels_dict[col].values()) + 1
                            self._labels_dict[col][new_class] = new_label
                        else:
                            warnings.warn(f"Label {new_class} in column {col} is not in training. Encoding this new "
                                          f"labels with {max_label + 1}...", Warning)
                            self._labels_dict[col][new_class] = max_label + 1
                data[col] = data[col].apply(lambda x: self._labels_dict[col][x])

    def fit_transform(self, data, cols):
        """Fit and transform columns using Learner LabelEncoder.

        :param data: data in pandas dataframe
        :param cols: columns to fit and transform
        :return: None
        """
        logging.info("Fitting data to Learner LabelEncoder...")
        self.fit(data, cols)
        logging.info("Transforming data using Learner LabelEncoder...")
        self.transform(data, cols)

    def inverse_transform(self, y, col):
        """Transform labels back to their original classes

        :param y: single column (pandas series or numpy array)
        :param col: column name to be transformed (used to pull the dictionary of encoded values from self._labels_dict)
        :return: a series of transformed labels
        """
        logging.info("Inverse transformation of labels in column '%s' to original values using Learner LabelEncoder...",
                     col)
        inverse_dictionary = {val: key for (key, val) in self._labels_dict[col].items()}
        y_original = pd.Series(y).map(inverse_dictionary)
        return y_original.values


class LearnerFillNaN:
    """LearnerFillNaN is a class for handling imputation of missing values in datasets. The reason for implementing a
     custom class is to be able to use the values from the training data when imputing the test data. For example, if
     the missing values were imputed using the "mean" of the training data, we'd want to use the same values when
     imputing the test data instead of using the mean of testing data.
     """

    def __init__(self, default_value, mean_cols, median_cols, mode_cols, value_cols):
        """Initialize LeanerFillNaN using the default_value for imputation and a dictionary that maps the column names
        to the value/method for imputation.

        :param default_value: a default number to use for filling missing value if no custom value is provided.
        :param mean_cols: a list of columns to be imputed using the mean of the training data
        :param median_cols: a list of columns to be imputed using the median of the training data
        :param mode_cols: a list of columns to be imputed using the mode of the training data
        :param value_cols: a dictionary that maps the column names with a value for imputation
        """
        self._mean_dict = dict()
        self._median_dict = dict()
        self._mode_dict = dict()
        self._default_value = default_value
        self._mean_cols = mean_cols
        self._median_cols = median_cols
        self._mode_cols = mode_cols
        self._value_cols = value_cols

    @property
    def mean_dict(self):
        return self._mean_dict

    @property
    def median_dict(self):
        return self._median_dict

    @property
    def mode_dict(self):
        return self._mode_dict

    @property
    def mean_cols(self):
        return self._mean_cols

    @property
    def median_cols(self):
        return self._median_cols

    @property
    def mode_cols(self):
        return self._mode_cols

    @property
    def default_value(self):
        return self._default_value

    def fit(self, data):
        """Loop through fillnan_cols to populate the fillnan_dict. fillnan_dict maps the column names to the
        corresponding numbers for imputation of the missing values. If the value in the fillnan_col dictionary is a
        string, we call the _get_fill_value_for_method to compute the mean, median, or mode.

        :param data: pandas dataframe
        :return: None
        """
        for col in self.mean_cols:
            self.mean_dict[col] = self._get_fill_value_for_method(data,
                                                                  col,
                                                                  method="mean",
                                                                  default_value=self.default_value)
        for col in self.median_cols:
            self.median_dict[col] = self._get_fill_value_for_method(data,
                                                                    col,
                                                                    method="median",
                                                                    default_value=self.default_value)
        for col in self.mode_cols:
            self.mode_dict[col] = self._get_fill_value_for_method(data,
                                                                  col,
                                                                  method="mode",
                                                                  default_value=self.default_value)

    @staticmethod
    def _get_fill_value_for_method(data, col, method, default_value):
        """Depending on the method, i.e. "mean", "median", or "mode", compute the values that should be used for
        imputation of the column. If the value cannot be calculated, use the default value and issues a warning.

        :param data: a pandas dataframe
        :param col: the name of the column in the data
        :param method: the imputation method
        :param default_value: the default value to use in case the calculations fail
        :return: the computed value or the default value
        """
        try:
            if method == "mean":
                fill_value = data[col].mean()
            elif method == "median":
                fill_value = data[col].median()
            elif method == "mode":
                fill_value = data[col].mode().iloc[0]
        except TypeError:
            warnings.warn(f"""The column '{col}' cannot be imputed by {method}. Imputing the column {col} with 
                           the {default_value}""", Warning)
            fill_value = default_value
        finally:
            return fill_value

    def transform(self, data):
        """After we fit the data or if the fillnan_dict is already populated, loop through the fillnan_dict and fill the
        missing values in each column with their corresponding values. After that, fill all other missing values with
        the default value.

        :param data: a pandas dataframe
        :return: None
        """
        # this may fail if we have SparseArray
        try:
            data.replace([-np.inf, np.inf], np.NaN, inplace=True)
        except Exception:
            pass

        for col, value in self.mean_dict.items():
            logging.info(f"Filling missing value in {col} with {value}")
            data[col].fillna(value, inplace=True)
        for col, value in self.median_dict.items():
            logging.info(f"Filling missing value in {col} with {value}")
            data[col].fillna(value, inplace=True)
        for col, value in self.mode_dict.items():
            logging.info(f"Filling missing value in {col} with {value}")
            data[col].fillna(value, inplace=True)
        for col, value in self._value_cols.items():
            logging.info(f"Filling missing value in {col} with {value}")
            data[col].fillna(value, inplace=True)
        logging.info("Filling missing values in the unspecified columns with %.2f, if any", self._default_value)
        data.fillna(self._default_value, inplace=True)

    def fit_transform(self, data):
        """Call fit and transform method. This method is typically called during training while the transform method is
        called during testing.

        :param data: a pandas dataframe
        :return: None
        """
        self.fit(data)
        self.transform(data)


def handle_label_encoding(data, cols=None):
    """label encode selected columns.

    :param data: pandas dataframe
    :param cols: the columns to use for label encoding
    :return: pandas DataFrame with encoded data and label_encoder object
    """
    label_encoder = LearnerLabelEncoder()
    if cols:
        label_encoder.fit_transform(data, cols)
        return data, label_encoder


def filter_data(data, column, value, criterion):
    """Filter a pandas DataFrame based on a criterion. Due to the internal mechanism of query method, the query may fail.
    In this situation, if the criterion is equality operation, we then catch the error and filter the data using equality
    operator.

    :param data: pandas DataFrame
    :param column: column to filter
    :param value: value used in conditional
    :param criterion: condition to check
    :return: a filtered dataframe with the original indices

    Example:

        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

        filter_data(data=df, column='a', value=2, criterion= '>=')

        output >>

        pd.DataFrame({'a': [2, 3], 'b': [5, 6]})
    """
    try:
        idx = data.query('{0} {1} {2}'.format(column, criterion, value)).index
    except Exception as e:
        # in case things go wrong in equality operator, filter using regular equality operator.
        if criterion == '==':
            logging.error("Filtering the value {value} failed. The error is {error}. Using a "
                          "different method...".format(value=value, error=str(e)))
            idx = data[data[column] == value].index
            logging.info("Successfully filtered the data")
        else:
            raise e
    return data.loc[idx]


def parrallelize_dataframe(df, func, num_cores=None):
    """Accept a dataframe and a function, break the dataframe into multiple pieces (based on the number of cores). Then
    distribute the pieces and call the function on that each piece. In the end, get the result from each processor and
    concatenate the pieces together to return it.

    :param df: a pandas dataframe
    :param func: a function to pass the dataframe to
    :param num_cores: the number of cores to use
    :return: the updated dataframe
    """
    if not num_cores:
        num_cores = multiprocessing.cpu_count()

    # this line breaks the dataframe and gives a list of dataframe pieces
    df_split = np.array_split(df, num_cores)
    with multiprocessing.Pool(num_cores) as pool:
        df = pd.concat(pool.map(func, df_split), sort=False)
    return df


def parrallelize_dataframes(df1, df2, func, num_cores=None):
    """This functions is similar to parrallelize_dataframe but it accepts two dataframe instead of one.

    :param df1: the first dataframe
    :param df1: the second dataframe
    :param func: a function to pass the dataframe to
    :param num_cores: the number of cores to use
    :return: the updated dataframes
    """
    if not num_cores:
        num_cores = multiprocessing.cpu_count()

    df1_split = np.array_split(df1, num_cores)
    df2_split = np.array_split(df2, num_cores)

    with multiprocessing.Pool(num_cores) as pool:
        df_lists = pool.starmap(func, zip(df1_split, df2_split))

        df1 = pd.concat((df[0] for df in df_lists), sort=False)
        df2 = pd.concat((df[1] for df in df_lists), sort=False)

    return df1, df2


def log_transform(data, params, cols=None):
    """Use the data and params to call the log_transform method in feature_engineering module. This is currently used
    for log transformation of the target column.

    :param data: a pandas dataframe
    :param params: a list of log_transform parameters coming from the conf object (see the configuration module for details)
    :param cols: a list of columns for log transformation. This is provided so that exclude_list can be applied to it.
    :return: updated data frame
    """
    if cols:
        from learner.feature_engineering.feature_engineering import FeatureEngineering
        data = FeatureEngineering.log_transform(data, params)
    return data


def delete_keys_from_dict(dictionary, keys):
    """Accept a dictionary and a list of keys. Delete all the keys from the dictionary.

    :param dictionary: a dictionary to be processed
    :param keys: a list of key to be removed from the dictionary
    :return: None
    """
    if not isinstance(dictionary, dict):
        logging.critical("Wrong input type. Provide a dictionary as the first argument or the 'dictionary' keyword "
                         "argument. Exiting...")
        sys.exit(1)

    if not isinstance(keys, list):
        logging.critical("Wrong input type. Provide a list as the second argument or the 'keys' keyword argument. "
                         "Exiting...")
        sys.exit(1)

    for key in keys:
        dictionary.pop(key)

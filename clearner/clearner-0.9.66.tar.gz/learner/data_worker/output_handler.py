# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Handles all operations related to saving the output and the models including pickled models"""

import sys
import os
import pickle
import warnings
import logging
import pandas as pd
import numpy as np

from learner.utilities.templates import (PRED_PATH, PRED_PATH_SEG,
                                         PRED_PATH_CHUNK, PRED_PATH_CHUNK_SEG)


class OutputHandler:
    def __init__(self, conf, data_type=""):
        self._conf = conf
        self.data_type = data_type
        if data_type:
            self.dtype_sep = f"_{data_type}_"
        else:
            self.dtype_sep = "_"

    @property
    def conf(self):
        return self._conf

    def save_file(self, directory_path, filename, dataframe, add_timetag=True, index=False, format="csv",
                  add_version=False, version_name="", version_column_name="version",
                  **kwargs):
        """Save a dataframe into the hard drive and create a timetag column if necessary. This method accepts a "format"
         argument and calls the appropriate methods to support multiple file formats.
        formats including

        :param directory_path: the path to the folder in which the file should be saved.
        :param filename: the name of the file.
        :param dataframe: the dataframe that contains the data.
        :param add_timetag: a boolean to define if a timetag should be added or not given add_timetag is true in conf object.
        :param index: a boolean to specify if the row names should be written or not
        :param format: the file format when saving the data, currently we support "csv", "parquet", and "feather"
        :param add_version: whether we should add the version column or not
        :param version_name: the value to use in the version column
        :param version_column_name: the name of the version column
        :return: None
        """
        assert isinstance(dataframe, pd.DataFrame), "ERROR: save_file only supports saving dataframes"
        if add_timetag:
            timetag = pd.Series(np.full(dataframe.shape[0], self._conf.timetag), name="timetag")
            dataframe = pd.concat((dataframe, timetag), axis=1)
        if add_version:
            dataframe[version_column_name] = version_name

        if format == "csv":
            self.save_csv(directory_path, filename, dataframe, index=index, **kwargs)
        elif format == "parquet":
            self.save_parquet(directory_path, filename, dataframe, index=index)
        elif format == "feather":
            self.save_feather(directory_path, filename, dataframe)

    def save_csv(self, directory_path, filename, dataframe, index=False, **kwargs):
        """Save a dataframe into the hard drive in the csv format.

        :param directory_path: the path to the folder in which the file should be saved.
        :param filename: the name of the file.
        :param dataframe: the dataframe that contains the data.
        :param index: a boolean to specify if the row names should be written or not
        :return: None
        """
        dataframe.to_csv(directory_path + filename, index=index, **kwargs)

    def save_parquet(self, directory_path, filename, dataframe, index=False):
        """Save a dataframe into the hard drive in the parquet format.

        :param directory_path: the path to the folder in which the file should be saved.
        :param filename: the name of the file.
        :param dataframe: the dataframe that contains the data.
        :param index: a boolean to specify if the row names should be written or not
        :return: None
        """
        try:
            dataframe.to_parquet(directory_path + filename, engine="pyarrow", index=index)
        except Exception as e:
            logging.error(f"Failed to save the data. The error is {str(e)}. Will try a different engine.")
            dataframe.to_parquet(directory_path + filename, engine="fastparquet", index=index)

    def save_feather(self, directory_path, filename, dataframe):
        """Save a dataframe into the hard drive into the feather format.

        :param directory_path: the path to the folder in which the file should be saved.
        :param filename: the name of the file.
        :param dataframe: the dataframe that contains the data.
        :return: None
        """
        # to resolve the error: feather does not support serializing a non-default index for the index;
        # you can .reset_index() to make the index into column(s)
        dataframe.reset_index(inplace=True, drop=True)
        dataframe.to_feather(directory_path + filename)

    def concat_save_csv(self, models, items, output_name, sep_timetag):
        """Read a series of csv file from the disk, concatenate them, and write the output to a csv file

        :param models: a dictionary of models that contains tag information
        :param items: a list containing the items (this is seg_list for the recommender engine)
        :param output_name: the prefix of the filenames (this is usually conf.workspace.name)
        :param sep_timetag: the sep_timetag for the model
        :return: None
        """
        logging.info("Combining the results for different segments")
        # read and concatenate the results
        for tag, mdls in models.items():
            filename = PRED_PATH.format(
                path=mdls.get(0, mdls)["path"],
                output_name=self._conf.workspace.name,
                tag=str(tag),
                sep_timetag=str(sep_timetag),
                dtype_sep=self.dtype_sep
            )
            if os.path.isfile(filename):
                warnings.warn("{0} already exist. It will be overwritten...".format(filename), Warning)
                os.remove(filename)

            for seg_id in range(len(items)):
                try:
                    item_name = PRED_PATH_SEG.format(
                        path=mdls.get(seg_id, mdls)["path"],
                        output_name=output_name,
                        dtype_sep=self.dtype_sep,
                        tag=str(tag),
                        seg_id=str(seg_id),
                        sep_timetag=str(sep_timetag)
                    )
                    df = pd.read_csv(item_name)
                    logging.info("Appending %s to %s", item_name, filename)
                    if os.path.isfile(filename) is False:
                        df.to_csv(filename, index=False)
                    else:
                        df.to_csv(filename, mode='a', header=False, index=False)
                except FileNotFoundError as e:
                    logging.error(str(e))

        if self._conf.data.test_clean_up:
            self.delete_concat_save_csv(models, items, output_name, sep_timetag)

    def concat_chunk_csv(self, num_chunks, models_dict, seg_id=None):
        """Read a series of csv file from the disk, concatenate them, and write the output to a single csv file.
        This function concatenates the predictions for different chunks and different models and produces a
        single csv file for each model.

        :param num_chunks: the number of chunks to be used for reading the file indices
        :param models_dict: an item in models_dict. The value for "path" is typically used in this class
        :param seg_id: segment id
        :return: None
        """
        logging.info("Combining the predictions for different data chunks")
        for tag, mdls in models_dict.items():
            if seg_id is None:
                filename = PRED_PATH.format(
                    path=models_dict[tag]["path"],
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    sep_timetag=str(self._conf.sep_timetag),
                    dtype_sep=self.dtype_sep
                )
            else:
                mdl = mdls.get(seg_id, mdls)
                filename = PRED_PATH_SEG.format(
                    path=mdl["path"],
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    seg_id=str(seg_id),
                    sep_timetag=str(self._conf.sep_timetag),
                    dtype_sep=self.dtype_sep
                )

            if os.path.isfile(filename):
                warnings.warn(f"{filename} already exist. It will be overwritten...", Warning)
                os.remove(filename)

            for index in range(num_chunks):
                sep_index = f"_{index}"
                if seg_id is None:
                    chunkname = PRED_PATH_CHUNK.format(
                        path=models_dict[tag]["path"],
                        output_name=self._conf.workspace.name,
                        tag=str(tag),
                        sep_timetag=str(self._conf.sep_timetag),
                        index=str(index),
                        dtype_sep=str(self.dtype_sep)
                    )
                else:
                    mdl = mdls.get(seg_id, mdls)
                    chunkname = PRED_PATH_CHUNK_SEG.format(
                        path=mdl["path"],
                        output_name=self._conf.workspace.name,
                        tag=str(tag),
                        seg_id=str(seg_id),
                        sep_timetag=str(self._conf.sep_timetag),
                        dtype_sep=self.dtype_sep,
                        sep_index=str(sep_index)
                    )

                df = pd.read_csv(chunkname)

                logging.info("Appending %s to %s", chunkname, filename)
                if os.path.isfile(filename) is False:
                    df.to_csv(filename, index=False)
                else:
                    df.to_csv(filename, mode='a', header=False, index=False)

        if self._conf.data.test_clean_up:
            self.delete_concat_chunk_csv(num_chunks, models_dict, seg_id)

    def delete_concat_save_csv(self, models, items, output_name, sep_timetag):
        """Delete a series of csv files that concat_save_csv uses to concatenate and generate a single file. This method
        should only be called after concat_save_csv is being called.

        :param models: a dictionary of models that contains tag information
        :param items: a list containing the items (this is seg_list for the recommender engine)
        :param output_name: the prefix of the filenames (this is usually conf.workspace.name)
        :param sep_timetag: the sep_timetag for the model
        :return: None
        """
        logging.info("Deleting separate prediction files for segments")
        for tag, mdls in models.items():
            for seg_id in range(len(items)):
                try:
                    filename = PRED_PATH_SEG.format(
                        path=mdls.get(seg_id, mdls)["path"],
                        output_name=output_name,
                        tag=str(tag),
                        seg_id=str(seg_id),
                        sep_timetag=str(sep_timetag),
                        dtype_sep=self.dtype_sep
                    )

                    os.remove(filename)
                    logging.info("Deleting %s", filename)
                except FileNotFoundError as e:
                    logging.error(str(e))

    def delete_concat_chunk_csv(self, num_chunks, models_dict, seg_id=None):
        """Delete a series of csv files that were generated during the iteration through the prediction dataset. This
        method should only be called after concat_chunk_csv is being called.

        :param num_chunks: the number of chunks to be used for reading the file indices
        :param models_dict: an item in models_dict. The value for "path" is typically used in this class
        :param seg_id: segment id
        :return: None
        """
        logging.info("Deleting the files generated during iteration")

        for tag, mdls in models_dict.items():
            for index in range(num_chunks):
                sep_index = f"_{index}"
                if seg_id is None:
                    chunkname = PRED_PATH_CHUNK.format(
                        path=models_dict[tag]["path"],
                        output_name=self._conf.workspace.name,
                        tag=str(tag),
                        sep_timetag=str(self._conf.sep_timetag),
                        index=str(index),
                        dtype_sep=self.dtype_sep
                    )
                else:
                    mdl = mdls.get(seg_id, mdls)
                    chunkname = PRED_PATH_CHUNK_SEG.format(
                        path=mdl["path"],
                        output_name=self._conf.workspace.name,
                        tag=str(tag),
                        seg_id=str(seg_id),
                        sep_timetag=str(self._conf.sep_timetag),
                        dtype_sep=self.dtype_sep,
                        sep_index=sep_index,
                    )
                logging.info("Deleting %s", chunkname)
                os.remove(chunkname)

    def pickle_object(self, directory_path, filename, model_object, processor, feature_engineering):
        """Pickle the fitted model to training data and configuration object.

        :param directory_path: path the directory in which the model_object resides
        :param filename: name tag used for pickled object
        :param model_object: an object containing trained models, encoder, and scale objects
        :param processor: a DataProcessor object
        :param feature_engineering: an instance of FeatureEngineering class
        :return: None
        """

        logging.info("Pickling the model...")
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        with open(filename, "wb") as pickle_file:
            pickle.dump((self.conf, model_object, processor, feature_engineering), pickle_file)


def pickle_object(conf, directory_path, filename, model_object, processor, feature_engineering):
    """Pickle the fitted model to training data and configuration object.

    :param conf: configuration file
    :param directory_path: path the directory in which the model_object resides
    :param filename: name tag used for pickled object
    :param model_object: an object containing trained models, encoder, and scale objects
    :param processor: a DataProcessor object
    :param feature_engineering: an instance of FeatureEngineering class
    :return: None
    """

    logging.info("Pickling the model...")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    with open(filename, "wb") as pickle_file:
        pickle.dump((conf, model_object, processor, feature_engineering), pickle_file)


def get_prediction_col_names(classes, prediction_type, column_name=None):
    """Take the number of classes for a model and generate a matching number of column names
    for prediction values to be appended to output data when writing predictions

    :param classes: a list of classes in the target
    :param prediction_type: type of prediction (proba, class, or all)
    :param column_name: output column name specified in the json file
    :return: a list of column names
    """
    # for binary classification return a single class
    if len(classes) == 2 or prediction_type == "class":
        return [column_name]
    else:
        return [column_name + "_" + str(c) for c in classes]

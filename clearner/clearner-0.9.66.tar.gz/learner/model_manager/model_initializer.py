# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for constructing the models_dict and loading models/objects"""

import sys
import re
import glob
import os
from datetime import datetime
import logging
import pickle


class ModelInitializer:
    """Construct the models_dict."""

    def __init__(self, conf):
        """Obtain a conf object and make a call to build_models_dict to construct models_dict."""

        self._conf = conf
        # this is silly but in the past we needed to modify the models_dict and we had a method called build_models_dict
        # I'm keeping things this way, in case we may need to implement a similar method
        self.models_dict = self._conf.model.models_dict

    @property
    def conf(self):
        return self._conf


class ModelLoader:
    """Load pickled objects based on path to .sav file"""

    def __init__(self, conf):
        """Initiate ModelLoader using a conf object"""

        self._conf = conf

    @property
    def conf(self):
        return self._conf

    def load_model(self, path_to_pickle):
        """Load a pickled object based on a file path. Learner uses the data and combine sections in the new
        configuration file after loading the pickled configuration.

        :param path_to_pickle: the path to the pickle object
        :return: a previously pickled configuration object, models_dict, processor object and sep_timetag
        """
        try:
            with open(path_to_pickle, "rb") as pickled_file:
                conf, models_dict, processor, feature_engineering = pickle.load(pickled_file)
                # we want to use the current data parameters
                conf.data = self._conf.data
                # we want to use the current combine parameters
                conf.combine = self._conf.combine
                # we want to use the current workspace parameters
                conf.workspace = self._conf.workspace
                # when we load the models, we want to use the current log_transform_target_predict_actuals
                conf.process.log_transform_target_predict_actuals = self._conf.process.log_transform_target_predict_actuals
                # we load the model, we've made 0 predictions
                conf.model.nrows_score = 0
                conf.timetag = self._conf.timetag
                sep_timetag = conf.sep_timetag
                conf.sep_timetag = self._conf.sep_timetag
                # we want to use the current connection object
                conf.connection = self._conf.connection
                logging.info("Successfully loaded pickled object")
                return conf, models_dict, processor, feature_engineering, sep_timetag
        except FileNotFoundError:
            logging.exception("Output path or name doesn't exist. Check json configuration.")
            sys.exit(1)

    def load_combiner(self, path_to_pickle):
        """Load a pickled combiner object. The combine object has a nested conf object in it. When loading the combiner
        object we replace the old conf object with the current conf object.

        :param path_to_pickle: the path to the pickle object
        :return: the loaded combiner object
        """
        with open(path_to_pickle, "rb") as pickled_file:
            combiner = pickle.load(pickled_file)
            combiner.conf = self._conf
            return combiner


def get_pickle_dir(path_to_pickle, ext="sav"):
    """Load pickled object and retrieve its directory and model prefix.
    If path_to_pickle includes a directory with a time tag, a .sav object will be retrieved that corresponds to
    that time tag, directory path to this object, and model prefix
    If path_to_pickle is just a path that doesn't include time tag, the directory to the latest pickled object
    will be retrieved.

    :param path_to_pickle: directory path to an engine output or the directory path to pickled object.
    :param ext: the file extensions to use to find the most recent models, e.g. sav, pkl, etc. Do not include "." here.
    :return: directory path to pickle, pickled object, prefix. The outputs are all lists
    """
    # retrieve pickled object that corresponds to the latest time tag
    pickled_files = []
    # save the list of prefixes
    prefixes = []
    # a list containing the directory path to pickle objects
    dir_paths_to_pickle = []

    try:
        # Check if a path has any .sav files
        if glob.glob(path_to_pickle+f'*.{ext}'):
            pickled_files.append([file for file in glob.iglob(path_to_pickle+f"*.{ext}")][-1])
            # if the folder has a timetag, the prefix will be obtained differently
            timetag = re.search(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}\-[0-9]{2}\-[0-9]{2}', path_to_pickle)
            if timetag:
                prefixes.append("_".join(os.path.basename(os.path.dirname(path_to_pickle)).split("_")[:-1]))
            else:
                prefixes.append(os.path.basename(os.path.dirname(path_to_pickle)))
            return [path_to_pickle], pickled_files, prefixes

        # Retrieve timetags from all existing directories
        timetags = []
        for folder in os.listdir(path_to_pickle):
            timetag = re.search(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}\-[0-9]{2}\-[0-9]{2}', folder)
            if timetag:
                timetags.append(timetag.group())

        # sort directories by time tag from latest to earliest
        sorted_timetags = sorted(timetags, key=lambda x: datetime.strptime(x, '%Y-%m-%d-%H-%M'),
                                 reverse=False)
        # retrieve the directory with the most recent timetag
        latest_pickled_folder = [folder_name for folder_name in os.listdir(path_to_pickle) if
                                 sorted_timetags[-1] in folder_name]

        for folder in latest_pickled_folder:
            for file in glob.iglob(path_to_pickle+folder + "/" + f"*.{ext}"):
                if file:
                    pickled_files.append(file)
                    prefixes.append("_".join(os.path.basename(os.path.basename(folder)).split("_")[:-1]))
                    dir_paths_to_pickle.append(path_to_pickle + folder + "/")
                    break
        return dir_paths_to_pickle,  pickled_files, prefixes
    except IndexError:
        # if we did not create triad but looking for it, we will get here. In that case, we don't want to raise an
        # error
        if ext == "triad":
            return [path_to_pickle], pickled_files, prefixes
        else:
            logging.error("Unable to find the folder where the saved models are stored. Please update your "
                          "configuration file and try again. Exiting...")
            sys.exit(1)

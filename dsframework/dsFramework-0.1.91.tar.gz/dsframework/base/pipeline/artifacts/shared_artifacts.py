#!/usr/bin/env python
# coding: utf-8

"""! @brief ZIDS_SharedArtifacts base class for the SharedArtifacts class."""

from typing import List, Any
import sys
import pathlib
import os
import json
import csv
import pickle
from dsframework.base.common import functions

class ZIDS_SharedArtifacts():
    """! ZIDS_SharedArtifacts is the base class for the SharedArtifacts class."""

    def __init__(self) -> None:
        """! ZIDS_SharedArtifacts initializer.
        Loads config, vocabs. and artifacts.
        """
        file_path = sys.modules[self.__class__.__module__].__file__
        curr_path = file_path[:file_path.rfind("pipeline")]
        ## Path for the framework.
        self.base_dir = curr_path
        self.load_config_json()
        self.load_vocabs()
        self.load_artifacts()

    def load_config_json(self):
        """! Loads config and sets its content to class attributes.
        It enables adding additional required settings to the config file (located here: config/config.json),
        which will be auto-loaded and be accessible via the SharedArtifacts class.
        """
        if os.path.exists(self.base_dir + 'config/config.json'):
            data = functions.load_json(self.base_dir + 'config/config.json')
            for item in data:
                setattr(self, item, data[item])

    def load_vocabs(self):
        """! Loads vocabulary from the specified path in config.json to class attributes,
        accessible via SharedArtifacts class. file can be in any format, we have the following ready to use:
        json, csv, pickle, tensorflow, key_value and key_value_int.
        To add additional formats override the function extend_load_file_type for example:

        @verbatim
        def extend_load_file_type(self, file_type, path, absolute_path, name):
            if absolute_path:
                if file_type == 'your-file-type':
                    with open(absolute_path) as json_file:
                        setattr(self, name, json.load(json_file))
        @endverbatim

        Setting the config.json file, example:
        @verbatim
        "vocabs": [{"name":"my_vocabs" ,"path": "pipeline/artifacts/vocabs/example_vocabs.json", "type": "json"}]
        @endverbatim
        """
        if hasattr(self, 'vocabs'):
            for item in self.vocabs:
                self.load_file(item)

    def load_artifacts(self):
        """! Load artifacts from the specified path in config.json to local attributes,
        accessible via SharedArtifacts class.
        Data file can be in any format, we have the following formats implemented:
        json, csv, pickle, tensorflow, key_value and key_value_int.
        To add additional formats override the function extend_load_file_type for example:
        """
        ##
        # @code{.py}
        # def extend_load_file_type(self, file_type, path, absolute_path, name):
        #     if absolute_path:
        #         if file_type == 'your-file-type':
        #             with open(absolute_path) as json_file:
        #                 setattr(self, name, json.load(json_file))
        # @endcode
        #
        # Setting the config.json file, example:
        # @verbatim
        # "artifacts": [{"name": "my_artifacts", "path": "pipeline/artifacts/models/example_models.json", "type": "json"}]
        # @endverbatim

        if hasattr(self, 'artifacts'):
            for item in self.artifacts:
                self.load_file(item)

    def load_file(self, item):
        """! Loads a file, this method is used by load_vocabs and load_artifacts methods.

        Args:
            item: (dict) with the following keys: {'name': '', 'path': '', 'type': ''}
                name: assign any name,
                path: path to data file,
                type: file format, format supported: json, csv, pickle, tensorflow, key_value and key_value_int
                    additional formats can be added by overriding extend_load_file_type method.
        """
        file_type = item['type']
        path = item['path']
        name = item['name']
        if path:
            absolute_path = self.base_dir + '/' + path
            if file_type == 'json':
                self.load_json(absolute_path, name)
            elif file_type == 'csv':
                self.load_csv(absolute_path, name)
            elif file_type == 'pickle':
                self.load_pickle(absolute_path, name)
            elif file_type == 'tensorflow':
                self.load_tensorflow(absolute_path, name)
            elif file_type == 'key_value':
                self.load_file_to_dict(absolute_path, name, str)
            elif file_type == 'key_value_int':
                self.load_file_to_dict(absolute_path, name, int)
            else:
                self.extend_load_file_type(file_type, path, absolute_path, name)

    def extend_load_file_type(self, file_type, path, absolute_path, name):
        """! Use this method to add new file types, that are currently not supported.

        Override method in the generatedProjectNameSharedArtifacts class to support new file format.
        """

        ##
        # For example:
        # @code{.py}
        # def extend_load_file_type(self, file_type, path, absolute_path, name):
        #     if absolute_path:
        #         if file_type == 'your-file-type':
        #             with open(absolute_path) as json_file:
        #                 setattr(self, name, json.load(json_file))
        # @endcode

        pass

    def load_json(self, path, name):
        """! Loads json file

        Args:
            path: Absolute path to data file.
            name: File name.
        """
        with open(path) as json_file:
            setattr(self, name, json.load(json_file))

    def load_csv(self, path, name):
        """! Loads csv file

        Args:
            path: Absolute path to data file.
            name: File name.
        """
        with open(path) as csv_file:
            setattr(self, name, functions.flatten_list(list(csv.reader(csv_file))))

    def load_pickle(self, path, name):
        """! Loads pickle file

        Args:
            path: Absolute path to data file.
            name: File name.
        """
        with open(path, 'rb') as pickle_file:
            setattr(self, name, pickle.load(pickle_file))

    def load_tensorflow(self, path, name):
        """! Loads tensorflow file.

        Important:
            This method is not implemented, please override to use its functionality.

        Args:
            path: Absolute path to data file.
            name: File name.

        Raises:
            NotImplementedError
        """
        ##
        # Implementation example:
        # @code
        # with open(path) as tensorflow_file:
        #     setattr(self, name, tf.keras.models.load_model(tensorflow_file))
        # @endcode

        raise NotImplementedError


    def load_file_to_dict(self, path, name, val_type):
        """! Loads file to dictionary.

        File structure needs to be a comma seperated key and value, one per line:

        key, value
        key, value
        .
        .
        .

        Args:
            path: Absolute path to data file.
            name: File name.
            val_type: datatype ie. str, int
        """
        dictionary = functions.load_file_to_dict(path, value_type=val_type)
        setattr(self, name, dictionary)

    ##
    # @cond
    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default

    def set(self, key, val, default=None):
        if key in self.__dict__:
            return self.__dict__.update({key: val})
        return default
    ##
    # @endcond

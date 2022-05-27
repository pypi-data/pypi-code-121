from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import ABC, abstractmethod
import numpy as np
import logging
import pickle
import os

class Dataset(ABC):
    def __init__(self, config_object):
        """Base class for implementation of datasets
        Args:
            config_object ([Configuration]): Configuration object where following attributes
                must be specified:

                - args.engine.fileExtension ([string])
        """

        super().__init__()
        self.data = []
        try:
            self.args = config_object.args
        except AttributeError:
            raise Exception("Invalid configuration object passed to {}".format(self))
        
    def index_files(self):

        """Index all files within the folder path contained in self.path. 

        If fileExtension is provided (as an option in engine_configuration.txt), 
        only files that match this file extension will be indexed.

        Raises:
            Exception: When fileExtension is not provided.

        Sets:
            self.filename_list ([list])

        """
        self.filename_list = sorted([f for f in os.listdir(self.path) if (os.path.isfile(os.path.join(self.path, f)))])
        if not len(self.filename_list)>0:
            logging.error("Data folder is empty. Either folder path is not correct, file extension is not correct or useSimulatedData flag is incorrectly set.")
        
    def set_data_path(self, path):
        """
        Set the path for the folder containing training, validation or testing files.

        Args:
            path ([string]): path for training or testing data. 
                It is provided as an option in engine_configuration.txt.

        Raises:
            Exception: When path does not point to a directory.
            Exception: When path points to an empty directory.

        Sets:
            self.path ([string])

        """
        if os.path.isdir(path):
            if not len(os.listdir(path)) == 0:
                self.path = path
            else:
                raise Exception("Data directory is empty.")
        else:
            raise Exception("path is not a directory.")

    def load_folder(self):
        """It pre-loads all the data in self.path.

        It is called when the option preLoadData==True. Use with care, 
        if the size of the data is too large, might cause memory issues.

        Raises:
            Exception: When fileExtension is not provided.

        Sets:
            self.data ([list])

        """
        for file in self.filename_list:
            if self.args.engine.fileExtension:
                if 'pkl' in self.args.engine.fileExtension:
                    with open(os.path.join(self.path, file), 'rb') as f:
                        data_ = pickle.load(f)
                        self.data.append(data_)
                if 'rawb' in self.args.engine.fileExtension:
                    data_ = np.fromfile(os.path.join(self.path, file), dtype='int8', sep="")
                    self.data.append(data_)
                if 'nii' in self.args.engine.fileExtension:
                    pass
                if 'nii.gz' in self.args.engine.fileExtension:
                    pass
            else:
                raise Exception("File extension not supported or not provided.")
        

    def load_file(self, idx):
        """It loads the file indexed by idx.

        It is called when the option preLoadData==False. 

        Args:
            idx ([int]): the index of the file to load from disk.

        Raises:
            Exception: When fileExtension is not provided.

        """

        file = self.filename_list[idx]
        if self.args.engine.fileExtension:
            if 'pkl' in self.args.engine.fileExtension:
                with open(os.path.join(self.path, file), 'rb') as f:
                    data_ = pickle.load(f)
            if 'rawb' in self.args.engine.fileExtension:
                    data_ = np.fromfile(os.path.join(self.path, file), dtype='int8', sep="")
            if 'nii' in self.args.engine.fileExtension:
                pass
            if 'nii.gz' in self.args.engine.fileExtension:
                pass
            self.data = [data_]
        else:
            raise Exception("File extension not supported or not provided.")

    def get_length(self):
        """
        It returns the length of the dataset (i.e. number of files in the dataset folder).

        Raises:
            TypeError: When self.filename_list is not initialized.

        Returns:
            (Data set length[list]): The number of files within the data directory.
        """
        try:
            return len(self.filename_list)
        except TypeError:
            logging.warn("self.filename_list not initialized")


    @abstractmethod
    def get_label(self, idx):
        """Abstract function for fetching labels and masks from the data directory.

        Need subclass to implement different logics, like Relaxometry, Reconstruction, QSM, etc.

        Args:
            idx ([int]): Index automatically provided by the DataLoader. It ranges 
                from 0 to len(self.filename_list)-1.

        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            (Label [torch.Tensor]), (Mask [torch.Tensor] - optional): The subclass implementation should 
            return the label, and, if available, a mask. For seemless integration with the 
            framework, label should have shape [N, X, Y, ...] and the mask should have 
            shape [1,X,Y, ...], where N is the number of channels (e.g. weighted images) 
            and X,Y,... are the image dimensions.
            
        """
        raise NotImplementedError("get_training_label not implemented")

    @abstractmethod
    def get_signal(self, idx):
        """Abstract function for fetching the signal from the data directory.

        Need subclass to implement different logics, like Relaxometry, Reconstruction, QSM, etc.

        Args:
            idx ([int]): Index automatically provided by the DataLoader. 
                It ranges from 0 to len(self.filename_list)-1.

        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            (Signal [torch.Tensor]): The subclass implementation should return the signal.
            For seemless integration with the framework, signal should have shape [N, X, Y, ...], 
            where N is the number of channels (e.g. weighted images) and X,Y,... are the image dimensions.

        """
        raise NotImplementedError("get_training_signal not implemented")

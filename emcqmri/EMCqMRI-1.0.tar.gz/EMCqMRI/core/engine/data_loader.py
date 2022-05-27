from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from pathlib import Path
from ..utilities import core_utilities

import numpy as np

class SampleDatabase(Dataset):
    """ Wrapper function for custom dataset subclasses.
    """
    def __init__(self, config_object, path=[]):
        self.args = config_object.args
        self.dataset = config_object.args.engine.dataset_model
        self.dataset.set_data_path(path)
        self.dataset.index_files()

    def __len__(self):
        return self.dataset.get_length()

    def __getitem__(self, idx):
        self.signal = self.dataset.get_signal(idx)
        self.label, self.mask = self.dataset.get_label(idx)
        self.filename = Path(self.dataset.filename_list[idx]).stem

        data = {}
        data['filename'] = self.filename
        data['image'] = self.signal
        if self.label is None:
            data['label'] = []
            data['mask'] = []
        else:
            data['label'] = self.label
            data['mask'] = self.mask

        return data



def create_dataloader(config_object):
    """Creates the dataloader handler

    Args:
        config_object ([Configuration]): [Object containing all backend configuration settings]
        Required config_object.args:
            - mode
            - dataset
            - trainingDataPath, validationDataPath and/or testingDataPath
            - batchSize
            - usePatches
            - useSimulatedData
            - runValidation
            
    Returns:
        [type: List]: List of DataLoader objects. If mode=='training', it returns 
                      [trainingDataloader, validationDataloader]. If mode=='testing', it returns 
                      [testingDataloader]
    """
    if config_object.args.engine.mode == 'training':
        training_path = Path(config_object.args.engine.trainingDataPath).absolute()
        validation_path = Path(config_object.args.engine.validationDataPath).absolute()

        training_database_handler = SampleDatabase(config_object, path=training_path)
        trainingDataloader = DataLoader(training_database_handler,
                                batch_size = config_object.args.engine.batchSize,
                                shuffle = config_object.args.engine.shuffleData,
                                num_workers = config_object.args.engine.numWorkers
                                )
        if config_object.args.engine.runValidation:
            validation_database_handler = SampleDatabase(config_object, path=validation_path)
            validationDataloader = DataLoader(validation_database_handler,
                                    batch_size = config_object.args.engine.batchSize,
                                    shuffle = config_object.args.engine.shuffleData,
                                    num_workers = config_object.args.engine.numWorkers
                                    )
            dataloader = trainingDataloader, validationDataloader
        else:
            dataloader = trainingDataloader

    elif config_object.args.engine.mode == 'testing':
        testing_path = Path(config_object.args.engine.testingDataPath).absolute()
        testing_database_handler = SampleDatabase(config_object, path=testing_path)
        testingDataloader = DataLoader(testing_database_handler,
                                batch_size = config_object.args.engine.batchSize,
                                shuffle = config_object.args.engine.shuffleData,
                                num_workers = config_object.args.engine.numWorkers
                                )
        dataloader = testingDataloader

    config_object.args.engine.dataloader = dataloader
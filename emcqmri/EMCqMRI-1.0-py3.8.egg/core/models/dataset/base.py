from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from core.base import base_dataset
from core.utilities import dataset_utilities
import numpy as np
import os
import pickle
import torch

class DatasetModel(base_dataset.Dataset):
    def __init__(self, config_object):
        super(DatasetModel, self).__init__(config_object)
        self.__name__ = 'Base Dataset'
        self.args = config_object.args
        self.data = []
        self.idx_control = -1

    def get_existing_data(self, idx):
        if not self.args.engine.preLoadData:
            data_ = self.data[idx - self.idx_control]
        else:
            data_ = self.data[idx]
        
        self.training_signal = torch.Tensor(data_['weighted_series']).type(torch.FloatTensor)
        self.training_signal = self.training_signal/torch.max(self.training_signal)

        if 'label' in data_:
            self.training_label = torch.Tensor(data_['label']).type(torch.FloatTensor)
        else:
            self.training_label = 0

        if 'mask' in data_:
            self.mask = torch.Tensor(data_['mask']).type(torch.FloatTensor)
        else:
            self.mask = []

        if self.training_signal.dim() > 3:
            self.training_signal = self.training_signal[...,8]

    def get_label(self, idx):
        if not self.args.engine.preLoadData:
            self.load_file(idx)
        self.get_existing_data(idx)
        return self.training_label, self.mask

    def get_signal(self, *local_args):
        return self.training_signal

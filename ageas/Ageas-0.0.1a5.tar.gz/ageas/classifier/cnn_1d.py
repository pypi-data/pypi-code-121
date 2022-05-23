#!/usr/bin/env python3
"""
This file contains classes to build CNN based classifiers

ToDo:
Implement _earlystopping

Note 1
Just in case if LazyLinear having problem
You may want to try torchlayers
# import torchlayers as tl

Note 2
If using SHAP deepLIFT based method or Cuptum,
repeated layers cannot be interpreted.
Thus, layer set loop-adding feature is removed in limited versions
which has layer set max fixed being 3, should be enough

author: jy, nkmtmsys
"""

import os
import torch
import itertools
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as func
import ageas.classifier as classifier



class Limited(nn.Module):
    """
    Defining a CNN model treating input as 1D data
    with given hyperparameters
    Layer set number limited to max == 3
    """
    def __init__(self, id, param, n_class = 2):
        # Initialization
        super().__init__()
        self.id = id
        self.model_type = 'CNN_1D_Limited'
        self.num_layers = param['num_layers']
        self.loss_func = nn.CrossEntropyLoss()
        # Layer set 1
        self.pool = nn.MaxPool1d(param['maxpool_kernel_size'])
        self.conv = nn.Conv1d(1, param['conv_kernel_num'],
                                    param['conv_kernel_size'])

        # Layer set 2
        self.pool1 = nn.MaxPool1d(param['maxpool_kernel_size'])
        self.conv1 = nn.Conv1d(param['conv_kernel_num'],
                                param['conv_kernel_num'],
                                param['conv_kernel_size'])

        # Layer set 3
        self.pool2 = nn.MaxPool1d(param['maxpool_kernel_size'])
        self.conv2 = nn.Conv1d(param['conv_kernel_num'],
                                param['conv_kernel_num'],
                                param['conv_kernel_size'])

        ### Trying to avoid Lazy module since it's under development ###
        ### But so far it's working just fine, so still using lazy module ###
        # flattenLength = int(featureNum / pow(maxpool_kernel_size, num_layers))
        # self.dense = nn.Linear(flattenLength, densed_size)
        ### -------------------------------------------------------- ###

        self.dense = nn.LazyLinear(param['densed_size'])
        self.decision = nn.Linear(param['densed_size'], n_class)
        self.optimizer = optim.SGD(self.parameters(), param['learning_rate'])

    # Overwrite the forward function in nn.Module
    def forward(self, input):
        input = self.pool(func.relu(self.conv(input)))
        if self.num_layers > 1:
            input = self.pool1(func.relu(self.conv1(input)))
        if self.num_layers > 2:
            input = self.pool2(func.relu(self.conv2(input)))
        if self.num_layers > 3:
            raise classifier.Error('CNN Model with more than 3 layer sets')
        input = torch.flatten(input, start_dim = 1)
        input = func.relu(self.dense(input))
        input = func.softmax(self.decision(input), dim = 1)
        return input


class Unlimited(nn.Module):
    """
    Defining a CNN model treating input as 1D data
    with given hyperparameters
    """
    def __init__(self, id, param, n_class = 2):
        # Initialization
        super().__init__()
        self.id = id
        self.model_type = 'CNN_1D_Unlimited'
        self.num_layers = param['num_layers']
        self.loss_func = nn.CrossEntropyLoss()
        self.conv = nn.Conv1d(1, param['conv_kernel_num'],
                                    param['conv_kernel_size'])
        self.convMore = nn.Conv1d(param['conv_kernel_num'],
                                    param['conv_kernel_num'],
                                    param['conv_kernel_size'])
        self.pool = nn.MaxPool1d(param['maxpool_kernel_size'])

        ### Trying to avoid Lazy module since it's under development ###
        ### But so far it's working just fine, so still using lazy module ###
        # flattenLength = int(featureNum / pow(maxpool_kernel_size, num_layers))
        # self.dense = nn.Linear(flattenLength, densed_size)
        ### -------------------------------------------------------- ###

        self.dense = nn.LazyLinear(param['densed_size'])
        self.decision = nn.Linear(param['densed_size'], n_class)
        self.optimizer = optim.SGD(self.parameters(), param['learning_rate'])

    # Overwrite the forward function in nn.Module
    def forward(self, input):
        input = self.pool(func.relu(self.conv(input)))
        for i in range(self.num_layers - 1):
            input = self.pool(func.relu(self.convMore(input)))
        input = torch.flatten(input, start_dim = 1)
        input = func.relu(self.dense(input))
        input = func.softmax(self.decision(input), dim = 1)
        return input



class Make(classifier.Make_Template):
    """
    Analysis the performances of CNN based approaches
    with different hyperparameters
    Find the top settings to build CNN
    """

    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        testData = classifier.reshape_tensor(dataSets.dataTest)
        testLabel = dataSets.labelTest
        num_features = len(dataSets.dataTest[0])
        for id in self.configs:
            if self.configs[id]['config']['num_layers'] < 3:
                model = Limited(id, self.configs[id]['config'])
            else:
                model = Unlimited(id, self.configs[id]['config'])
            epoch = self.configs[id]['epoch']
            batch_size = self.configs[id]['batch_size']
            self._train_torch(epoch, batch_size, model, dataSets)
            accuracy = self._evaluate_torch(model,
                                            testData,
                                            testLabel,
                                            test_split_set)
            self.models.append([model, accuracy])

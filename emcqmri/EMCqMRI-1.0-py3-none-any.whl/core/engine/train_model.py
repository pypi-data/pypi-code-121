from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.insert(0, '../')

from ..utilities import image_utilities
from ..utilities import core_utilities
from ..utilities import checkpoint_utilities
from timeit import default_timer as timer

import logging
import numpy as np

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logging.info('Setting up environment...')



class Trainer(object):
    """Performs a forward pass through a given inference model.
        Depending on the options set, it might save intermediate results and training checkpoints
        and/or display the intermediate results.

    Args:
        config_object ([type: Configuration]): [Object containing all backend configuration settings]
        Required config_object.args:
            - epochs
            - inference_model
            - dataloader
            - signal_model (if config_object.args.inference_model.__require_initial_guess__ == True)
            - numberOfPatches
            - objective_fun
            - optimizer
            - saveResults
            - saveResultsPath
            - saveCheckpoint
            - saveCheckpointPath
            - usePatchesAsBatches
    """
    def __init__(
                self, 
                device=[],
                max_epochs=[],
                train_data_loader=[],
                network=[],
                optimizer=[],
                loss_function=[],
                prepare_batch = [],
                log_training_fun = [],
                config_object = []
        ):
        self.args = config_object.args
        self.device = device
        self.max_epochs = max_epochs
        if isinstance(train_data_loader, list): # It means that validation dataset is being used.
            self.dataloader_state = core_utilities.alternateTrainingState(train_data_loader, self.args.engine.batchSize)
            state = next(self.dataloader_state)
            self.dataloader = list(state.values())[0]
            self.args.engine.state_name = list(state.keys())[0]
        else:
            self.args.engine.state_name = 'training'
            self.dataloader = train_data_loader
            
        self.network = network
        self.optimizer = optimizer
        self.loss_function = loss_function
        self.prepare_batch = prepare_batch
        self.log_training_fun = log_training_fun
        self.epoch = 0

        self.network.train()

    def run(self):
        start_time = timer()
        for ep in range(self.max_epochs):
            start_time_epoch = timer()
            logging.info('Running {}; Epoch {}'.format(self.args.engine.state_name, self.epoch))
            logging.info('*'*50)
            self.args.engine.len_dataset = len(self.dataloader)
            for sample, data in enumerate(self.dataloader):
                self.args.engine.test_sample = sample
                data_ = self.prepare_batch(data, self.device)
                processed_data, loss = self.__run__(data_)
                self.__log_error__(self.epoch+1, sample, loss)
                if self.log_training_fun:
                    self.log_training_fun(processed_data, loss, sample, ep)

            end_time_epoch = timer()
            self.__end_epoch__(processed_data, end_time_epoch - start_time_epoch)
        end_time = timer()

        print("Total training time: {} seconds for {} epochs".format(end_time - start_time, self.max_epochs))

    def __end_epoch__(self, processed_data, elapsed_time):
        if self.args.engine.state_name == 'training':
            self.epoch += 1
        if self.args.engine.saveResults:
            image_utilities.saveItermediateResults(processed_data, self.args, self.epoch)
        if self.args.engine.saveCheckpoint:
            checkpoint_utilities.save(self.args, self.epoch, self.network) 
            
        if isinstance(self.args.engine.dataloader, list):
            state = next(self.dataloader_state)
            self.dataloader = list(state.values())[0]
            self.args.engine.state_name = list(state.keys())[0]
            self.network.train() if self.args.engine.state_name == 'training' else self.network.eval()
        
        print("Time in Epoch {}: {} seconds".format(self.epoch, elapsed_time))

    def __log_error__(self, epoch, i, loss):
        logging.info("Epoch: {}, State: {}, Sample: {}/{}, Loss: {} ".format(epoch, 
                            self.args.engine.state_name, i+1, self.dataloader.__len__(), loss))

    def __run__(self, data_):
        self.optimizer.zero_grad()

        signal = data_['image']
        label = data_['label'] if len(data_['label']) else []

        estimate = self.network.forward(signal)

        loss = self.loss_function(estimate, label).mean()
        if self.args.engine.state_name == 'training':
            loss.backward()
            self.optimizer.step()
        
        processed_data = {}
        processed_data['estimated'] = estimate
        processed_data['signal'] = signal
        if label is not None:
            processed_data['label'] = label

        return processed_data, loss

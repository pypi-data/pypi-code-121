from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.insert(0, '../')

from ..utilities import image_utilities
import logging
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO)
logging.info('Setting up environment...')

class Infer(object):
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

    def __init__(self, device, validation_dataloader, network, metric, prepare_batch, compute_loss, log_training_fun, config_object):
        self.args = config_object.args
        self.device = device
        self.dataloader = validation_dataloader
        self.network = network
        self.metric = metric
        self.prepare_batch = prepare_batch
        self.compute_loss = compute_loss
        self.log_training_fun = log_training_fun

    def run(self, return_result = False):
        self.args.engine.batch_size_iter = 1
        if isinstance(self.network, nn.Module):
            self.network.eval()

        epoch = '_estimating_'
        logging.info('Running {}'.format(self.args.engine.state_name))
        logging.info('*'*50)
        self.args.engine.len_dataset = len(self.dataloader)
        for i, data in enumerate(self.dataloader):
            self.args.engine.iter = i
            data_ = self.prepare_batch(data, self.device)
            processed_data = self.__run__(data_, i)
            if self.log_training_fun:
                self.log_training_fun(processed_data, 0, 1, 1)

            if self.args.engine.saveResults:
                self.args.engine.filename = data[1][0]
                filename_ = self.args.engine.filename + 'patch_' + str(i)
                image_utilities.saveDataPickle(processed_data, self.args.engine.saveResultsPath, filename_)

        if return_result:
            return processed_data

    def __log_error__(self, i, loss):
        logging.info("Sample: {}/{}, Loss: {} ".format(i+1, self.dataloader.__len__(), loss))

    def __run__(self, data_, i):
        signal = data_[0]
        label = data_[1].unsqueeze(0) if len(data_) > 1 else None

        estimate = self.network.forward(signal)

        if self.compute_loss:
            if label is not None:
                loss = self.args.engine.objective_fun(estimate, label)
                self.__log_error__(i, loss)
            else:
                logging.error("No label provided")
        
        processed_data = {}
        processed_data['estimated'] = estimate
        processed_data['signal'] = signal
        if label is not None:
            processed_data['label'] = label

        return processed_data

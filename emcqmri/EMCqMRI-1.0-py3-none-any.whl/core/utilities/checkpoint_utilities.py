from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import torch
import logging


def save(args, epoch, model):
    """
        Save trained DL model to checkpoint.
        Inputs: args (console inputs), epoch and model

    """
    path = os.path.join(args.engine.saveCheckpointPath, args.engine.inferenceModel+'_epoch_'+ str(epoch) + '_' + args.engine.sulfixCheckpoint + '.pth')
    torch.save({'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': args.engine.optimizer.state_dict()}, path)

    logging.info('Model saved to: {}'.format(path))


def load(config_object):
    """
        Load saved DL model from checkpoint.
        Inputs: args (console inputs), epoch and model
        Outputs: DL model, optimiser checkpoint and epoch
    """
    try:
        checkpoint = torch.load(config_object.args.engine.loadCheckpointPath, map_location=config_object.args.engine.device)
        try:
            config_object.args.engine.inference_model.load_state_dict(checkpoint['model_state'])
            config_object.args.engine.optimizer.load_state_dict(checkpoint['optimizer_state'])
        except KeyError:
            try:
                config_object.args.engine.inference_model.load_state_dict(checkpoint['model_state_dict'])
                config_object.args.engine.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            except KeyError:
                logging.error('Error importing pre-trained model')

        epoch = checkpoint['epoch']

    except AssertionError:
        logging.error("Checkpoint path not specified. Please insert a valid checkpoint path")
        return -1

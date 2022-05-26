import pytorch_lightning as pl 
from typing import Union, List, Dict, Any, Optional, Tuple, cast
from astrape.utilities.dataloader_lightning import *
import inspect
from astrape.constants.astrape_constants import *
from sklearn.base import BaseEstimator

def set_default_parameters(config)->None:
    r"""Sets default parameters for astrape models.
    """
    if 'dropout_p' not in config.keys():
        config.update({'dropout_p' : DEFAULT_DROPOUT_P})
    if 'bn' not in config.keys():
        config.update({'bn' : DEFAULT_BN})
    if 'lr' not in config.keys():
        config.update({'lr' : DEFAULT_LR})
    if 'weight_decay' not in config.keys():
        config.update({'weight_decay' : DEFAULT_WEIGHT_DECAY})
    if 'optimizer_type' not in config.keys():
        config.update({'optimizer_type' : DEFAULT_OPTIMIZER_TYPE})
    if 'batch_size' not in config.keys():
        config.update({'batch_size' : DEFAULT_BATCH_SIZE})
    if 'l1_strength' not in config.keys():
        config.update({'l1_strength' : DEFAULT_L1_STRENGTH})

def initialize_model(
    model_type : "pl.LightningModule", 
    dims : int, 
    n_classes : int, 
    **config : Dict
)->Union["pl.LightningModule", "BaseEstimator"]:
    r"""Initializes Lightning model.
    """
    if BaseEstimator in inspect.getmro(model_type):
        model = model_type(**config)
    else:
        model = model_type(dims=dims, n_classes=n_classes, **config)

    return model
    
def initialize_datamodule(
    **config
)->Union["pl.LightningDataModule", Tuple]:
    r"""

    Args:

        **config (Any): Dictionary of the followings
            batch_size 
            X 
            y 
            X_test 
            y_test 
            test_size 
            random_state
    """
    data_module = DataModule(**config)
    return data_module


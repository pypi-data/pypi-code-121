import pytorch_lightning as pl 
from typing import Union, List, Dict, Any, Optional, cast
from astrape.utilities.dataloader_lightning import *
import inspect
from astrape.constants.astrape_constants import *

def set_default_parameters(config):
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
    **config : dict
) -> "pl.LightningModule":

    if "DTClassifier" in str(inspect.getmro(model_type)):
        model = model_type(**config)
    else:
        model = model_type(dims=dims, n_classes=n_classes, **config)

    return model
    
def initialize_datamodule(
    **config
) -> "pl.LightningDataModule":
    """
    config is a dictionary of the followings
        - batch_size : int, 
        - X : np.array, 
        - y : np.array,
        - X_test : Optional[np.array] = None,
        - y_test : Optional[np.array] = None,
        - test_size : float = 0.01,
        - random_state : int = 0
    
    """
    data_module = DataModule(**config)
    return data_module


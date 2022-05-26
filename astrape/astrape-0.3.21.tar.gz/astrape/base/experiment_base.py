from lib2to3.pytree import Base
from pyexpat.errors import XML_ERROR_INVALID_TOKEN
import pandas as pd
from astrape.exceptions.exceptions import *
from astrape.utilities.utils_lightning import *
from astrape.models.models_lightning import *
from astrape.base.model_base import *
import pytorch_lightning as pl
from pytorch_lightning import LightningDataModule, loggers as pl_loggers
from sklearn.model_selection import  train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
from typing import Union, List, Dict, Any, Optional, cast, overload

from sklearn.base import BaseEstimator
import pickle, os, json, sys
import inspect
import math
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import warnings
warnings.filterwarnings(action='ignore')
import shutil
from pytorch_lightning.callbacks import RichProgressBar, TQDMProgressBar

class BaseExperiment:
    r"""Parent class of ``Experiment``.

    BaseExperiment basically trains the model with a certain random state governing all random operations. When test data is not specified, the test data would also be splitted 
    differently depending on the randon state. To set a random state, you should specify the ``random_number`` argument as an input. This will set a random number generator with 
    seed being the ``random_number``. Then, the created random number generator will generate a random state. 

    All logs related to training will be logged in TensorBoard automatically. The directory for the Tensorboard depends on the type of training you do.
    When you are performing cross validation, the log directory would be {path}/{project_name}/CV/random_state-{random_state}.
    If you are doing regular fitting, the log directory would be {path}/{project_name}/FIT/random_state-{random_state}.

    Attributes:

        project_name (str): Name of the project. Directory of {path}/{project_name} will be created.

        X (np.ndarray or torch.Tensor or pd.DataFrame): Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

        y (np.ndarray or torch.Tensor or pd.DataFrame): Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

        X_train (torch.Tensor): Training data.   

        y_train (torch.Tensor): Training labels.

        X_val (np.ndarray or torch.Tensor or pd.DataFrame, optional): Validation data if explicitly exists.   

        y_val (np.ndarray or torch.Tensor or pd.DataFrame, optional): Validation labels if explicitly exists.

        X_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test data if explicitly exists.
        
        y_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test labels if explicitly exists.

        test_size (float): Test(and validation) size when splitting the data.
            
        n_classes (int): Number of classes for the classification task. Don't specify this when performing regression tasks.

        path (str): Base path for the project. Default is the current directory.

        dims (:obj:`int` or :obj:`tuple` of `int`) : Dimensions of the data. Number of samples is excluded in dims.

        project_path (:obj:`str`): Path for the project. It will be {path}/{project_name}.

        stack (list): Fitted models will be stacked here if ``stack_models`` is True.

        stack_models (bool): Whehter to stack models in each ``Experiment`` or not.

        stackflag (bool): Flag for stacking models.

        model (:obj:`LightningModel` or :obj:`BaseEstimator`): The current model of interest.

        model_metadata (str): Description of the model.

        trainer (:obj:`Trainer`) : The trainer for training the defined PyTorch-Lightning model.

        data_module (`LightningDataModule` or tuple): DataLoader or a tuple of (X_train, y_train, X_val, y_val, X_test, y_test).
   
        exp_path (str): The path of the ``Experiment``. It will be {project_path}/{FIT or CV}/random_state-{random state}.

        log_path (str): The path where the results would be logged. It will be {exp_path}/logs

        n_ckpts (int): Number of checkpoints saved.

        exp_metadata (dict): Dictionary describing the ``Experiment``. Will be saved as json file.

        random_number (int): The seed.

        rng: Random number generator.

        random_state (int): The random state that governs the ``Experiment``.

        logger (TensorBoardLogger): The logger that logs the experiment to TensorBoard. 

        fit_or_cv (str): Flag. "FIT" when training the model, "CV" when performing cross-validation.

        saved_model_types (dict): Dictionary specifying the saved model types and their frequencies.

    Note:
    
        One is expected to define and train models inside the experiment class in order to make the model being "secured" from overriding during sequence of experiments 
        e.g., defining model = MLP(**kwargs) and model = VGG(**kwargs) in the same runtime.
    """
    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_val : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]] = None,
        y_val : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]] = None,
        X_test : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]]= None,
        y_test : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]] = None,
        n_classes : Optional[int] = None,
        test_size : float = 0.01,
        stack_models : bool = True,
        random_number : int = 0,
        path : Optional[str] = None
    )->None:
        r"""
        Args:

            project_name (str): Name of the project. Directory of {path}/{project_name} will be created.

            X (np.ndarray or torch.Tensor or pd.DataFrame): Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

            y (np.ndarray or torch.Tensor or pd.DataFrame): Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

            X_val (np.ndarray or torch.Tensor or pd.DataFrame, optional): Validation data if explicitly exists.
                Default: ``None``

            y_val (np.ndarray or torch.Tensor or pd.DataFrame, optional): Validation labels if explicitly exists.
                Default: ``None``

            X_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test data if explicitly exists.
                Default: ``None``

            y_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test labels if explicitly exists.
                Default: ``None``

            n_classes (int): Number of classes for the classification task. Don't specify this when performing regression tasks.
                Default: ``None``

            test_size (float): Test(and validation) size when splitting the data.
                Default: ``1e-2``
            
            stack_models (bool): Whehter to stack models in each ``Experiment`` or not.
                Default: ``True``

            random_number (int): The seed.
                Default: ``0``

            path (str): Base path for the project. Default is the current directory.
                Default: ``'.'``
        
        Raises: 

            ValueError: When the dimension of the data is wrong. 

        Returns:

            None
        """
        self.project_name = project_name
        self.X = X
        self.y = y
        self.X_val = X_val
        self.y_val = y_val
        self.X_test = X_test
        self.y_test = y_test
        self.test_size = test_size
        self.n_classes = n_classes
        self.path = "." if path is None else path
        if self.path[-1] == "/":
            self.path = self.path[:-1]
        
        if len(X.shape) == 2:
            self.dims = X.shape[1]
        elif len(X.shape) > 2:
            self.dims = X.shape[1:]
        else:
            raise ValueError("Wrong dimension of input X.")

        self.project_path = self.path + "/" + self.project_name 
        self.stack = [] 
        self.stack_models = stack_models
        self.stackflag = stack_models
        self.model = None # Pointer for model
        self.model_metadata = None # Pointer for model_metadata.
        self.trainer = None # Pointer for trainer.
        self.data_module = None # Pointer for data_module
        self.exp_path = None
        self.log_path = None

        now = datetime.now()
        birthday = now.strftime("%b-%d-%Y-%H-%M-%S")
        self.n_ckpts = 0
        self.exp_metadata = {'date of birth of this experiemt' : birthday}
        self.random_number = random_number 
        self.rng = np.random.default_rng(random_number)
        self.random_state = int(10**6 * self.rng.random(1))
        self.logger = None # Pointer for logger.
        self.fit_or_cv = "FIT" 
        self.saved_model_types = {}
        
        self.X_train = self.y_train = None # Pointer for training data.

        self._create_folder(self.project_path)
        

    def update_log_path(self)->None:
        r"""Updates log path"""
        self.exp_path = self.project_path + "/"+ self.fit_or_cv + "/" + "random_state-{}".format(self.random_state)
        self.log_path = self.exp_path + "/logs"

    def update_exp_metadata(self)->None:
        r"""Upates exp_metadata."""
        self.exp_metadata.update({'# of checkpoints saved' : int(self.n_ckpts)})
        self.exp_metadata.update({'size of the experiment in MB' : float(os.path.getsize(self.exp_path)/10**6)})
        self.exp_metadata.update({'size of stack in MB': float(sys.getsizeof(self.stack)/10**6)})
        self.exp_metadata.update({'random state' : int(self.random_state)})
        if self.data_module:
            self.exp_metadata.update({'size of data in MB' : float(sys.getsizeof(self.X)/10**6)})
        json_name = self.exp_path +"/exp_metadata.json" 
        with open(json_name, 'w') as fout:
            json.dump(self.exp_metadata, fout)

    def set_model(
        self,
        model_type,
        **hparams : Any
    )->Union["pl.LightningModule", "BaseEstimator"]:
        r"""Method for setting a model.

        Args:

            model_type (`LightningModule` or `BaseEstimator`): The type of model. (class)

            **hparams (Any): Model hyperparameters.

        Returns:

            :obj:LightningModule or :obj:BaseEstimator: self.model
        """
        if BaseNet in inspect.getmro(model_type) or ConvNet in inspect.getmro(model_type): # astrape models
            self.model = model_type(dims=self.dims, n_classes=self.n_classes, **hparams)
            self.model_metadata = self.set_model_metadata(self.model, self.model.hparams)
        elif pl.LightningModule in inspect.getmro(model_type): # other pl.LightningModules not defined in astrape
            self.model = model_type(**hparams)
            self.model_metadata = self.set_model_metadata(self.model, self.model.hparams)
        else: # sklearn-based models
            self.model = model_type(**hparams)
            self.model_metadata = self.set_model_metadata(self.model, hparams)
        return self.model

    def get_data_module(
        self
    )->Union["pl.LightningDataModule", tuple["np.ndarray","np.ndarray","np.ndarray","np.ndarray","np.ndarray","np.ndarray"]]:
        r"""Method for getting a datamodule.

        Returns:

            `LightningDataModule` or tuple: Returns tuple when the model is sklearn-based model.
        
        """
        if self.model is None:
            raise AssertionError("Model must be defined first. Use .model(model_type, **hparams) to declare a model.")
        
        del self.data_module
        self.data_module = None
        data_module = None
        if isinstance(self.model, ConvNet):
            if len(self.X.shape) > 2:
                data_module = initialize_datamodule(
                    batch_size=self.model.hparams['batch_size'], 
                    X=self.X, 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            else: 
                raise AssertionError("Wrong dimension for vision data. You must specify the dimensions of the data, not in a flattened way.")
        elif isinstance(self.model, BaseNet):
            if self.X_val is not None and self.y_val is not None and self.X_test is not None and self.y_test is not None:
                data_module = initialize_datamodule(
                    batch_size=self.model.hparams['batch_size'], 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val.reshape((self.X_val.shape[0], -1)),
                    y_val=self.y_val,
                    X_test=self.X_test.reshape((self.X_test.shape[0], -1)),
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            
            if self.X_val is not None and self.y_val is not None and self.X_test is None and self.y_test is None:
                data_module = initialize_datamodule(
                    batch_size=self.model.hparams['batch_size'], 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val.reshape((self.X_val.shape[0], -1)),
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            
            if self.X_val is None and self.y_val is None and self.X_test is not None and self.y_test is not None:
                data_module = initialize_datamodule(
                    batch_size=self.model.hparams['batch_size'], 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test.reshape((self.X_test.shape[0], -1)),
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            if self.X_val is None and self.y_val is None and self.X_test is None and self.y_test is None:
                data_module = initialize_datamodule(
                    batch_size=self.model.hparams['batch_size'], 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )

        elif isinstance(self.model, pl.LightningModule):
            batch_size = 256 if torch.cuda.is_available() else 64
            if self.X_val is None and self.y_val is None and self.X_test is None and self.y_test is None:
                data_module = initialize_datamodule(
                    batch_size=batch_size, 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            elif self.X_val is not None and self.y_val is not None and self.X_test is None and self.y_test is None:
                data_module = initialize_datamodule(
                    batch_size=batch_size, 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val.reshape((self.X_val.shape[0], -1)),
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            
            elif self.X_val is None and self.y_val is None and self.X_test is not None and self.y_test is not None:
                data_module = initialize_datamodule(
                    batch_size=batch_size, 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test.reshape((self.X_test.shape[0], -1)),
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )

            elif self.X_val is None and self.y_val is None and self.X_test is None and self.y_test is None:
                data_module = initialize_datamodule(
                    batch_size=batch_size, 
                    X=self.X.reshape(self.X.shape[0],-1), 
                    y=self.y,
                    X_val=self.X_val,
                    y_val=self.y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
        elif isinstance(self.model, BaseEstimator):
            if self.X_test is None and self.y_test is None:  
                X_, X_test, y_, y_test = train_test_split(self.X, self.y, test_size=self.test_size, stratify=self.y)
                X_train, X_val, y_train, y_val = train_test_split(X_, y_, test_size=self.test_size, stratify=y_)
                self.X_train, self.X_val, self.X_test = X_train, X_val, X_test
                self.y_train, self.y_val, self.y_test = y_train, y_val, y_test
                data_module = (X_train, X_val, y_train, y_val, X_test, y_test)
            elif self.X_test is not None and self.y_test is not None:
                X_train, X_val, y_train, y_val = train_test_split(self.X, self.y, test_size=self.test_size, stratify=self.y)
                data_module = (X_train, X_val, y_train, y_val, X_test, y_test)
                self.X_train, self.X_val = X_train, X_val
                self.y_train, self.y_val = y_train, y_val
            else:
                raise ValueError("X_test and y_test should both be NoneType object or non-empty numpy array.")
        return data_module
    
    
    def set_trainer(self, **trainer_config)->"pl.Trainer":
        r"""Method for getting trainer for the lightning model.

        Args:
            
            **trainer_config (Any): Configurations(i.e., specification of flags) of the trainer.
        
        Returns:
            
            `pl.Trainer`: trainer
        """
        if self.model is None:
            raise AssertionError("Model must be defined first in order to set metadata. Use .model(model_type, **hparams) to declare a model.")
        self.update_log_path()
        self._create_folder(self.log_path)
        trainer_setting = trainer_config
        if self.logger:
            del self.logger
        self.logger = pl_loggers.TensorBoardLogger(save_dir=self.log_path+"/tensorboardlogs/" + self.model.__class__.__name__, name=self.model_metadata)

        if torch.cuda.is_available():
            trainer_setting.update({'gpus' : -1})
            trainer_setting.update({'accelerator' : 'gpu'})
        if 'min_epochs' not in trainer_config.keys():
            trainer_setting.update({'min_epochs' : 10})
        if 'max_epochs' not in trainer_config.keys():
            trainer_setting.update({'max_epochs' : 150})
        if 'sample_weight' in trainer_setting.keys():
            trainer_setting.pop('sample_weight')
        if 'callbacks' not in trainer_setting.keys():
            trainer_setting.update({'callbacks' : []})
        trainer = pl.Trainer(logger=self.logger, **trainer_config)
        for c in trainer.callbacks:
            if isinstance(c, TQDMProgressBar):
                trainer.callbacks.remove(c)
                trainer.callbacks.append(RichProgressBar())
        self._create_folder(self.log_path+"/tensorboardlogs/"+ self.model.__class__.__name__ + "/" + self.model_metadata)
        return trainer

    def fit(
        self,
        sample_weight : Optional[Union["np.ndarray", "torch.Tensor"]] = None,
        fit_or_cv : str = "FIT",
        **config        
    )->Union["pl.LightningModule", "BaseEstimator"]:
        r"""Method for training the model.

        Args:

            sample_weight (np.ndarray or torch.Tensor, optional): If specified, this will be the weights for each sample.
                Default: ``None``
            
            fit_or_cv (str): Flag. "FIT" if in actual training, "CV" if in cross validation.

            **config (Any): Trainer configurations.

        Returns:

            `pl.LightningModule` or `BaseEstimator`: self.model
        """

        if self.model is None:
            raise AssertionError("Model must be defined first. Use .model(model_type, **hparams) to declare a model.")
        
        self.fit_or_cv = fit_or_cv
        self.update_log_path()
        self.data_module = self.get_data_module()
        if self.logger:
            self.logger.close()
            del self.logger
            self.logger = None
        if BaseEstimator in inspect.getmro(self.model.__class__):
            return self.fit_sklearn(sample_weight=sample_weight, **config)
        elif pl.LightningModule in inspect.getmro(self.model.__class__):
            return self.fit_lightning(**config)
        else:
            raise AssertionError("Astrape doesn't support non-lightning modules.")

    def fit_sklearn(
        self,
        sample_weight : Optional["np.ndarray"] = None
    )->"BaseEstimator":
        # for consistency with the logging style of pytorch_lightning.
        self.update_log_path()
        folder_dir = self.log_path + "/tensorboardlogs/" + self.model.__class__.__name__ 
        self._create_folder(folder_dir)
        version = len(os.listdir(folder_dir)) - 1
        log_dir = folder_dir + "/" + self.model_metadata + "/" + "version_{}".format(version)
        if version >= 0:
            self._create_folder(log_dir)
        self.logger = SummaryWriter(log_dir=log_dir)
        self.model.fit(self.X_train, self.y_train, sample_weight)
        y_train_preds = self.model.predict(self.X_train)
        train_acc = (self.y_train==y_train_preds).astype(float).mean()
        y_val_preds = self.model.predict(self.X_val)
        val_acc = (self.y_val==y_val_preds).astype(float).mean()
        y_test_preds = self.model.predict(self.X_test)
        test_acc = (self.y_test==y_test_preds).astype(float).mean()
        y_train_predict_proba = self.model.predict_proba(self.X_train)
        y_val_predict_proba = self.model.predict_proba(self.X_val)
        y_test_predict_proba = self.model.predict_proba(self.X_test)
        if self.n_classes==2:
            y_train_predict_proba = y_train_predict_proba[:,1]
            y_val_predict_proba = y_val_predict_proba[:,1]
            y_test_predict_proba = y_test_predict_proba[:,1]

        train_auc = roc_auc_score(y_true=self.y_train, y_score=y_train_predict_proba)
        val_auc = roc_auc_score(y_true=self.y_val, y_score=y_val_predict_proba)   
        test_auc = roc_auc_score(y_true=self.y_test, y_score=y_test_predict_proba)
        self.logger.add_scalar('val/acc', val_acc)
        self.logger.add_scalar('train/acc', train_acc)
        self.logger.add_scalar('test/acc', test_acc)
        self.logger.add_scalar('val/auc', val_auc)
        self.logger.add_scalar('train/auc', train_auc)
        self.logger.add_scalar('test/auc', test_auc)
        if sample_weight:
            self.logger.add_scalar('sample_weight', sample_weight)
        self.logger.flush()
        self.logger.close()
        if self.stack_models:    
            self.save_to_stack()
            self.stackflag = True
        else:
            if self.stackflag == False:
                self.stack.pop()
            self.save_to_stack()
            self.stackflag = False
        self.update_exp_metadata()
        return self.model
         
    def fit_lightning(
        self,
        **trainer_config : Optional[Dict[str, Any]]
    )->"pl.LightningModule":  
        self.trainer = self.set_trainer(**trainer_config)
        self.trainer.fit(self.model, self.data_module)

        if self.stack_models:    
            self.save_to_stack()
            self.stackflag = True
        else:
            if not self.stackflag:
                self.stack.pop()
            self.save_to_stack()
            self.stackflag = False
        self.logger.save()
        self.logger.finalize("")
        self.update_exp_metadata()
        return self.model
  
    def save_ckpt(
        self,
        model : Optional[Union["pl.LightningModule", "BaseEstimator"]] = None,
        trainer : Optional["pl.Trainer"] = None,
        val_metrics : Optional[dict] = None
    )->None:
        r"""Method for saving checkpoints. The logs are saved as json file as well.
        
        Args:

            model (:obj:`LightningModule` or :obj:`BaseEstimator`, optional): If specified, will save the specified model.
                Default: ``None``

            trainer (:obj:`Trainer`, optional): If specified, will save the specified trainer.
                Default: ``None``

            val_metrics (dict, optional): If speicifed, will save the dictionary of validation performances to a json file.
                Default: ``None``

        Returns:
            
            None

        Note:

            If self.model is a variant of sklearn, we save model states as `.sav` file.
            If self.model is a LightningModule, we use ``save_checkpoint`` method from pl.Trainer class.

            ``save_checkpoint`` method from pl.Trainer class saves the followings to a `.ckpt` file.

                - 16-bit scaling factor (if using 16-bit precision training)
                - Current epoch
                - Global step
                - LightningModule’s state_dict
                - State of all optimizers
                - State of all learning rate schedulers
                - State of all callbacks (for stateful callbacks)
                - State of datamodule (for stateful datamodules)
                - The hyperparameters used for that model if passed in as hparams (Argparse.Namespace)
                - State of Loops (if using Fault-Tolerant training)

            For beginners in pytorch-lightning, below is an example code for how to save/load checkpoints.
        
        Example::

            >>> # Saving the model after fitting
                exp.save_ckpt()
                # Loading the model: 
                saved_ckpt = MLP.load_from_checkpoint(checkpoint_path=f'{ckpt_path}')
        """
        if model is None:
            model = self.model
        if trainer is None and isinstance(model, pl.LightningModule):
            trainer = self.trainer  
        self.update_log_path()
        
        if isinstance(model, BaseEstimator):
            model_metadata = self.set_model_metadata(model, model.__dict__)
            ckpt_name = model_metadata + ".sav"
        elif isinstance(model, pl.LightningModule):
            model_metadata = self.set_model_metadata(model, model.hparams)
            ckpt_name = model_metadata + ".ckpt"
        else:
            raise NotImplementedError("Astrape only supports variants of sklearn and pl.LightningModule.")
        checkpoint_path = self.log_path + "/checkpoints/" + model.__class__.__name__ + "/" + model_metadata
        self._create_folder(checkpoint_path)
        ckpt_path = checkpoint_path +"/" + ckpt_name 
        
        if isinstance(model, BaseEstimator):
            pickle.dump(model, open(ckpt_path, 'wb'))
        elif isinstance(model, pl.LightningModule):
            trainer.save_checkpoint(ckpt_path)

        metadata_dir = self.log_path + "/jsonlogs/" + model.__class__.__name__ + "/" + model_metadata
        self._create_folder(metadata_dir)
        version = len(os.listdir(metadata_dir))
        self._create_folder(metadata_dir+"/version_{}".format(version))
        tensorboard_logdir = self.logger.experiment.get_logdir()
        if model.__class__ in self.saved_model_types:
            self.saved_model_types.update({model.__class__: self.saved_model_types[model.__class__] + 1})
        else:
            self.saved_model_types.update({model.__class__: 1})
        
        self.n_ckpts += 1 
        self.log_metrics_to_json(model, tensorboard_logdir, version, val_metrics)
        self.update_exp_metadata()
    
    def save_to_stack(self)->None:
        r"""Method for stacking a model to ``stack``. If one of the ancestors of the model is ``BaseEstimator``, we only stack the model and its validation performance.
        If one of the ancestors of the model is ``LightningModule``, we stack a dictionary containing the model, its trainer, and its validation performance.

        Returns:
            
            None
        
        Raises:

            AssertionError: If there were no log informations for the specified model.
        """
        has_val_loss = False
        has_val_acc = False
        has_val_auc = False

        if isinstance(self.model, pl.LightningModule):
            logdir = self.logger.experiment.get_logdir()
        elif isinstance(self.model, BaseEstimator):
            logdir = self.logger.get_logdir()
            
        event = EventAccumulator(logdir)
        event.Reload()
        try:
            val_acc_df = pd.DataFrame(
                [(w, s, t) for w, s, t in event.Scalars('val/acc')],
             columns=['wall_time', 'step', 'val/acc']
            )
            val_acc = val_acc_df['val/acc'][val_acc_df.index[-1]]
            has_val_acc = True
        except:
            pass
        try:
            val_auc_df = pd.DataFrame(
                [(w, s, t) for w, s, t in event.Scalars('val/auc')],
             columns=['wall_time', 'step', 'val/auc']
            )
            val_auc = val_auc_df['val/auc'][val_auc_df.index[-1]]
            has_val_auc = True
        except:
            pass 
        try:    
            val_loss_df = pd.DataFrame(
                [(w, s, t) for w, s, t in event.Scalars('val/loss')],
             columns=['wall_time', 'step', 'val/loss']
            )
            
            val_loss = val_loss_df['val/loss'][val_loss_df.index[-1]]
            has_val_loss = True
        except:
            pass

        if not has_val_loss and not has_val_acc and not has_val_auc:
            raise AssertionError(f"No logged validation performances.")

        val_loss = math.inf if not has_val_loss else val_loss
        val_acc = -math.inf if not has_val_acc else val_acc
        val_auc = -math.inf if not has_val_auc else val_auc

        if isinstance(self.model, BaseEstimator):
            self.stack.append({"model" : self.model, "val_metrics": {'val/acc' : val_acc, 'val/loss' : val_loss, 'val/auc' : val_auc}})
            self.update_exp_metadata()   
        elif isinstance(self.model, pl.LightningModule):
            self.stack.append({"model" : self.model, "trainer" : self.trainer, "val_metrics": {'val/acc' : val_acc, 'val/loss' : val_loss, 'val/auc' : val_auc}})
            self.update_exp_metadata()   
        else:
            raise NotImplementedError(f"Astrape only supports sklearn-based models and pl.LightningModule.")
   
    
    def save_stack(self)->None:
        r"""Method for saving all model checkpoints in ``stack``.
        
        Returns:
            
            None
                    
        Note:
        
            ``stack`` will be flushed after saving.
        """
        for subject in self.stack:
            self.save_ckpt(**subject)
        del self.stack 
        self.stack = []

    def delete_saved_model(
        self,
        model_type : "pl.LightningModule",
        **hparams
    ):
        pseudomodel = model_type(**hparams)
        model_metadata = self.set_model_metadata(pseudomodel, hparams)
        ckpt_dir = self.log_path + '/checkpoints/' + model_type.__name__ + "/" + model_metadata
        jsonlog_dir = self.log_path + '/jsonlogs/' + model_type.__name__ + "/" + model_metadata
        tensorboard_dir = self.log_path + '/tensorboardlogs/' + model_type.__name__ + "/" + model_metadata
        if not os.path.exists(ckpt_dir) or not os.path.exists(jsonlog_dir) or not os.path.exists(tensorboard_dir):
            return None
        

        success = {ckpt_dir:0, jsonlog_dir:0, tensorboard_dir:0}
        if os.path.exists(ckpt_dir):
            shutil.rmtree(ckpt_dir)
            success.update({ckpt_dir:1})
        if os.path.exists(jsonlog_dir):
            shutil.rmtree(jsonlog_dir)
            success.update({jsonlog_dir:1})
        if os.path.exists(tensorboard_dir):
            shutil.rmtree(tensorboard_dir)
            success.update({tensorboard_dir:1})

        for key, value in success.items():
            if value == 0:
                print("There is no directory {}".format(key))
            
    def best_ckpt_thus_far(
        self, 
        val_metric : str = 'val/acc',
        mode : Optional[str] = None, 
        fetch_only_dir : bool = False
    ):
        r"""Method for returning the best saved checkpoint(or the path name of the best saved checkpoint) from the directory. The criterion is the type of the validation metric.

        Args:

            val_metric (str): The validation metric of choice. This will be the criterion in determining the "best" checkpoint. Default : 'val/loss'

            mode (str, optional): The mode of search. If left None, will set appropriate modes for search when val_metric is one of 'val/acc', 'val/loss', and 'val/auc'. Will raise error if not.
                Default: ``None``

            fetch_only_dir (bool): If True, returns the path(str) of the best checkpoint. If False, returns the best checkpoint. Default : False

        Returns: 
            
            :obj:LightningModule or None: The best checkpoint(or the path if fetch_only_dir is True) as per the validation metric you defined in the argument. Returns None if there are no saved checkpoints
        """
        try:
            jsonlogdir = self.log_path + "/jsonlogs"
        except:
            print("Nothing has been saved yet.")
            return None
        if not mode:
            if val_metric == 'val/loss':
                mode = 'min'
            elif val_metric in ['val/acc', 'val/auc']:
                mode = 'max'
            else:
                raise AssertionError("You should specify the mode if val_metric is not one of 'val/acc', 'val/loss', or 'val/auc'.")
        best_val = None
        ckpt_extension_type = None
        model_type = None
        best_model_metadata = None
        best_version = None
        for model_type_dir in os.listdir(jsonlogdir):
            for metadata in os.listdir(model_type_dir):
                for version in os.listdir(metadata):
                    for file in os.listdir(version):
                        with open(model_type_dir + "/" + version + "/" + file, "r") as json_file:
                            logs = json.load(json_file)
                            val_score = logs[val_metric] if isinstance(logs[val_metric], float) else logs[val_metric][-1]
                            if best_val is None:
                                best_val = val_score
                                best_path = file
                                model_type = logs['model_type']
                                best_model_metadata = metadata
                                best_version = version
                            elif mode == "max" and val_score > best_val:
                                best_val = val_score
                                best_path = file
                                model_type = logs['model_type']
                                best_model_metadata = metadata
                                best_version = version
                            elif mode == "min" and val_score < best_val:
                                best_val = val_score
                                best_path = file
                                model_type = logs['model_type']
                                best_model_metadata = metadata
                                best_version = version
                            info = {val_metric : best_val}
        if not fetch_only_dir:
            ckpt_path = self.log_path + '/checkpoints/' + model_type + "/" + best_model_metadata + "/" + best_version
            ckpt_name = ckpt_path + "/" + str(best_path).replace(".json", "")
            extension_candidates = [".ckpt", ".sav"]
            for extension_type in extension_candidates:
                ckpt = ckpt_name + extension_type
                if os.path.exists(ckpt):
                    ckpt_dir = ckpt
                    ckpt_extension_type = extension_type
            if ckpt_extension_type not in extension_candidates:
                raise ValueError("Wrong file extension {} for the checkpoint. It should be in {}".format(ckpt_extension_type, extension_candidates))
            if ckpt_extension_type == ".sav":
                best_ckpt = pickle.load(open(ckpt_dir, 'rb'))
            elif BaseNet in inspect.getmro(model_type) or ConvNet in inspect.getmro(model_type):
                best_ckpt = eval(model_type).load_from_checkpoint(dims=self.dims, n_classes=self.n_classes, checkpoint_path=ckpt_dir)
            elif pl.LightningModule in inspect.getmro(model_type):
                best_ckpt = eval(model_type).load_from_checkpoint(checkpoint_path=ckpt_dir)
            else:
                raise AssertionError
            return best_ckpt, info
        else:
            ckpt_path = self.log_path + '/checkpoints/' + model_type + "/" + best_model_metadata + "/" + best_version
            ckpt_name = ckpt_path + "/" +str(best_path).replace(".json", "")
            extension_candidates = [".ckpt", ".sav"]
            for extension_type in extension_candidates:
                ckpt = ckpt_name + extension_type
                if os.path.exists(ckpt):
                    ckpt_dir = ckpt
            return str(ckpt_dir), info
        
    
    
    def best_ckpt_in_stack(
        self, 
        val_metric : str = "val/acc"
    ):
        r"""Method for returning the best saved checkpoint from the stack as per the validation metric.

        Args:
            
            val_metric (str) : The validation metric of choice. This will be the criterion in determining the "best" checkpoint. Default : 'val/loss'

        Returns: 
            
            :obj:`LightningModule` or :obj:`BaseEstimator` or None: Returns the best checkpoint as per the validation metric. Returns None if there are no saved checkpoints.  
        """
        if val_metric not in ["val/loss", "val/acc", "val/auc"]:
            raise ValueError("Wrong type of val_metric. It should be one of [{}]".format(*["val/loss", "val/acc", "val/auc"]))
        if len(self.stack) == 0:
            print("Nothing is stored in stack.")
            return None
        best_val_score = None
        best_idx = None
        for idx, model_info in enumerate(self.stack):
            val_score = model_info['val_metrics'][val_metric]
            if best_val_score is None:
                best_val_score = val_score
                best_idx = idx
            elif (val_metric == "val/loss" and val_score < best_val_score):
                best_val_score = val_score
                best_idx = idx
            elif (val_metric == "val/acc" and val_score > best_val_score):
                best_val_score = val_score
                best_idx = idx
            elif (val_metric == "val/auc" and val_score > best_val_score):
                best_val_score = val_score
                best_idx = idx 
        
        best_ckpt = self.stack[best_idx]

        return best_ckpt
    
    
    def set_model_metadata(
        self,
        model: Union["pl.LightningModule", "BaseEstimator"],
        hparams : dict,
        length_limit : int = 500,
        subtract : int = 30
    )->str: 
        r"""Method for generating metadata of the experiment.
        
        Args:
            
            length_limit (int): Maximum tolerance for the length of the string. 
                Default: ``500``
            
            subtract (int): Width of the wiggle room for sanity. 
                Default: ``30``

            model (`LightningModule` or `BaseEstimator`): Class of model type. 

            hparams (dict): Model hyperparameters.

        Returns: 
        
            str: Metadata of the model.

        Note:

            Metadata of a model is a string that specifies: {model type}-{hyperparameters}
        """
        hparams_str = self._dict_to_str(hparams)
        hparams_str = "default_hyperparameters" if hparams_str == "" else hparams_str
        
        model_metadata = model.__class__.__name__ + "-" + hparams_str 

        #################################################
        # Shorten the length of model_metadata
        # when the name is too long. This is done
        # by shortening the 'hparams' part in 
        # metadata. 
        # 'hparams' part will now then
        # only contain value for each key.
        # The order for the values are as per
        # the lexicographic ordering of the keys.
        # If it is still too long, take adequate amount
        # of text from 'hparams' part.
        #################################################
        if len(model_metadata) > length_limit:
            hparams_sorted_by_key = sorted(hparams.items())
            truncated_hparams_str = ""
            for key, value in hparams_sorted_by_key:
                add_ = str(value).replace(".","d") + "-"
                truncated_hparams_str += add_
            
            new_metadata = model.__class__.__name__ + truncated_hparams_str   
            if len(new_metadata) > length_limit:
                print("The length of the metadata is too long due to long hyperparameter specs. We will take the first {} letters from the hyperparameter part.".format(length_limit-subtract))
                new_metadata = hparams_str[:length_limit-subtract] 

                model_metadata = new_metadata
        return model_metadata
   
    def get_hparams(self, model):
        r"""Gets hyperparameter or model specs.
        """
        if isinstance(model, BaseEstimator):
            return self.set_model_metadata(model, model.__dict__)
        elif isinstance(model, pl.LightningModule):
            return model.hparams
        else:
            raise AssertionError("Wrong model.")
    
    def log_metrics_to_json(
        self, 
        model : Union["pl.LightningModule", "BaseEstimator"],
        tensorboard_logdir: str,
        version : int,
        metrics_dict : Optional[dict] = None
    )->None:
        r"""Save results as a json file.

        Args:

            model (:obj:`LightningModule` or :obj:`BaseEstimator`)

            tensorboard_logdir (str): location of the TensorBoard logs.

            version (int): The version of the model. >0 when identical models are trained and logged.

            metrics_dict (dict, optional): Results to save as a json file. If None, the results in the TensorBoard will be saved.
                Default: ``None``

        Returns:

            None
        """
        log = {'model_type' : model.__class__.__name__}
        error_count = 0
        self.update_log_path()
        model_metadata = self.set_model_metadata(model, self.get_hparams(model))
        metadata_dir_ = self.log_path+'/jsonlogs/'+ model.__class__.__name__ + "/" + model_metadata
        jsonlog_dir = metadata_dir_ + "/" + 'version_{}'.format(version)
        json_logdir = jsonlog_dir + "/validation_metrics.json"

        if not metrics_dict:
            event = EventAccumulator(tensorboard_logdir)
            event.Reload()
            try:
                val_acc = event.Scalars('val/acc')
                log.update({'val/acc' : val_acc})
            except KeyError:
                error_count += 1 
            try:    
                val_loss = event.Scalars('val/loss')
                log.update({'val/loss' : val_loss})
            except KeyError:
                error_count += 1 
            try:
                val_auc = event.Scalars('val/auc')
                log.update({'val/auc' : val_auc})
            except KeyError:
                error_count += 1
                
            try:
                train_acc = event.Scalars('train/acc')
                log.update({'train/acc' : train_acc})
            except KeyError:
                error_count += 1 
            try:    
                train_loss = event.Scalars('train/loss')
                log.update({'train/loss' : train_loss})
            except KeyError:
                error_count += 1 
            try:
                train_auc = event.Scalars('train/auc')
                log.update({'train/auc' : train_auc})
            except KeyError:
                error_count += 1
        else: # save from input (metrics_dict)
            try:
                log.update({'val/acc' : metrics_dict['val/acc']})
            except KeyError:
                error_count += 1       
            try:
                log.update({'train/acc' : metrics_dict['train/acc']})
            except KeyError:
                error_count += 1
            try:
                log.update({'val/loss' : metrics_dict['val/loss']})
            except KeyError:
                error_count += 1
            try: 
                log.update({'train/loss' : metrics_dict['train/loss']})
            except KeyError:
                error_count += 1
            try:
                log.update({'val/auc' : metrics_dict['val/auc']})
            except KeyError:
                error_count += 1
            try:
                log.update({'train/auc' : metrics_dict['train/auc']})
            except KeyError:
                error_count += 1
        if error_count == 6:
            raise AssertionError("Nothing has been logged.")
        
        with open(json_logdir, 'w') as fout:
            json.dump(log, fout)


    def toggle_stack(self):
        r"""Toggles stack_models.
        """
        self.stackflag = not self.stackflag
        self.stack_models = not self.stack_models

    @staticmethod
    def _create_folder(directory : str)->str:
        r"""Creates folder. If folder already exists, does nothing."""
        os.makedirs(directory, exist_ok=True)
        return directory

    @staticmethod
    def _dict_to_str(dictionary : dict)->str:
        r"""Polishes string form of the dictionary. Applied when defining hparams and using **hparams to pass arguments."""
        out = str(dictionary).replace("{", "").replace("}","").replace(" ","-").replace(":","").replace("-","").replace("\n", "-").replace('"', "").replace(".","d").replace("'","")
        return out

    def _args_to_str(*args)->str:
        r"""Polishes string form of the args when not. Applited when passing arguments as *args"""
        out = str(args).replace(",","_")
        return out
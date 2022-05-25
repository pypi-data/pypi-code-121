from lib2to3.pytree import Base
from pyexpat.errors import XML_ERROR_INVALID_TOKEN
import pandas as pd
from astrape.exceptions.exceptions import *
from astrape.utilities.utils_lightning import *
from astrape.models.models_lightning import *
from astrape.base.model_base import *
import pytorch_lightning as pl
from pytorch_lightning import loggers as pl_loggers
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
    """
    Experiment class occupies the second highest rank in astrape hierarchy. (First is the Project class #TODO make Project class)
    Experiment class takes the following arguments :
                                                    - Data-dependent arguments: X, y, n_classes, dims, X_test, y_test, test_size
                                                    - Data-agnostic arguments: project_name, stack_models, random_state, path 

    ***************************************************************************************************************************
    Parameters:
    project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_val : Optional["np.ndarray"] = None,
        y_val : Optional["np.ndarray"] =None,
        n_classes : Optional[int] = None,
        X_test : Optional[np.ndarray] = None,
        y_test : Optional[np.ndarray] = None,
        test_size : float = 0.01,
        stack_models : bool = True,
        random_state : int = 0,
        path : Optional[str] = None
    ---------------------------------------------------------------------------------------------------------------------------
    1. project_name (str) : 
    The name of the project you are in conduct with. 
    Usually, it would be the name of the dataset or the project itself (or both). e.g., "MNIST", "ICML2022", "NeurIPS2022_LAWSCHOOL".
    
    2. X, y (np.ndarray) : 
    Data all of which conspire to training/validation/test data if (X_test, y_test) == (None, None) 
    and would be training/validation data if (X_test, y_test) != (None, None).
    X, y would be training data if (X_val, y_val, X_test, y_test) != (None, None, None, None)

    3. n_classes (Optional[int]) : 
    Number of classes in the label. 
    If not defined, it will be considered as a regression task.

    4. X_test, y_test (np.ndarray) : 
    The test dataset. If defined, parameters X and y would be divided into train/val data. 
    Else, X and y would be divided into train/val/test data and (X_test, y_test) would be
    occupied with the created test data.

    5. test_size (0 < float < 1) : 
    The portion you will take for test(validation) data from given (X,y). 
    If (X_test, y_test) == (None, None), the ratio will be (#train:#val:#test) = (1-2*test_size: test_size: test_size)
    If (X_test, y_test) != (None, None), the ratio will be (#train:#val) = (1-test_size:test_size) and #test == size(X_test)
    If (X_val, y_val) != (None, None), the ratio will be (#train:#val:#test) = (#train: #val: #test))
    
    6. stack_models (bool) : 
    Whether you will stack and save all the models defined in this class to an array or not.

    7. random_state (int) : 
    The random state in all random operations.

    8. path (Optional[str]) :
    A base path to save your experiments. If None, all data will be saved in the current path i.e. ".". 
    ---------------------------------------------------------------------------------------------------------------------------
    ***************************************************************************************************************************

    Attributes (not originated from the arguments):

    ---------------------------------------------------------------------------------------------------------------------------
    1. model_metadata (str): 
    String of model_name(or model_type) + hyperparameters of the model + random_state.

    2. stack (dict):
    Dictionary of saved models. Each model is saved only if stack_models == True.

    3. model (pl.LightningModel, nn.Module, BaseEstimator) :
    The model that you defined inside the experiment.

    4. trainer (pl.Trainer) :
    The trainer for training the defined pl.LightningModel.

    5. data_module (pl.LightningDataModule, tuple]) :
    DataLoader(or tuple comprised of (X_train, y_train, X_val, y_val, X_test, y_test)) when LightningModule(or BaseEstimator)
    is defined.

    7. exp_path (str) :
    The path of the folder that contains all the files from the Experiment.
    It would be self.project_name + "/" + self.fit_or_cv e.g.) MNIST/CV or MNIST/FIT (CV when performing cross-validation. FIT when
                                                                                      performing standard training w/ given random_state)
    8. exp_metadata (dict):
    A dictionary describing the experiment. See .update_metadata(self)
    ---------------------------------------------------------------------------------------------------------------------------
    Note:
    One is expected to define and train models inside the experiment class in order to
    make the model being "secured" from overriding during sequence of experiments 
    e.g., defining model = MLP(**kwargs) and model = VGG(**kwargs) in the same runtime.
    """
    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_val : Optional["np.ndarray"] = None,
        y_val : Optional["np.ndarray"] =None,
        n_classes : Optional[int] = None,
        X_test : Optional[np.ndarray] = None,
        y_test : Optional[np.ndarray] = None,
        test_size : float = 0.01,
        stack_models : bool = True,
        random_number : int = 0,
        path : Optional[str] = None
    ) -> None:
        ##########################################
        # Defining attributes from input arguments
        ##########################################
        self.project_name = project_name
        self.X = X
        self.y = y
        self.X_val = X_val
        self.y_val = y_val
        self.n_classes = n_classes
        self.X_test = X_test
        self.y_test = y_test
        self.test_size = test_size
        self.stack_models = stack_models
        self.random_number = random_number
        self.path = "." if path is None else path
        if self.path[-1] == "/":
            self.path = self.path[:-1]
    
        ###########################################
        # Attributes that are not originated from
        # input arguments
        ###########################################
        if len(X.shape) == 2:
            self.dims = X.shape[1]
        elif len(X.shape) > 2:
            self.dims = X.shape[1:]
        else:
            raise ValueError("Wrong dimension of input X.")
        
        self.model = None    # The model to be defined
        self.data_module = None # The data module(or dataset) to be defined
        self.trainer = None # pl.Trainer to be defined
        self.stack = []  # List[Dict] Fitted models are saved to this list of dictionaries when stack_models is True
        self.stackflag = stack_models
        self.model_metadata = None # Metadata for the experiment will be defined after the model is defined. 
        
        self.logger = None
        self.X_train = self.y_train = self.X_val = self.y_val = None
        self.fit_or_cv = "FIT"
        ###########################################
        # Create a directory with the project name
        ###########################################
        self.project_path = self.path + "/" + self.project_name 
        self._create_folder(self.project_path)
        
        self.saved_model_types = {}
        self.exp_path = None
        self.log_path = None

        self.n_ckpts = 0
        self.exp_metadata = {}
        now = datetime.now()
        self.birthday = now.strftime("%b-%d-%Y-%H-%M-%S")

        
        self.exp_metadata = {'date of birth of this experiemt' : self.birthday}

        self.rng = np.random.default_rng(random_number)
        self.random_state = int(10**6 * self.rng.random(1))


    def update_log_path(self):
        self.exp_path = self.project_path + "/"+ self.fit_or_cv + "/" + "random_state-{}".format(self.random_state)
        self.log_path = self.exp_path + "/logs"

    def update_exp_metadata(self):
        
        self.exp_metadata.update({'# of checkpoints saved' : int(self.n_ckpts)})
        self.exp_metadata.update({'size of the experiment in MB' : float(os.path.getsize(self.exp_path)/10**6)})
        self.exp_metadata.update({'size of stack in MB': float(sys.getsizeof(self.stack)/10**6)})
        self.exp_metadata.update({'random state' : int(self.random_state)})
        if self.data_module:
            self.exp_metadata.update({'size of data in MB' : float(sys.getsizeof(self.X)/10**6)})
        json_name = self.exp_path +"/exp_metadata.json" 
        with open(json_name, 'w') as fout:
            json.dump(self.exp_metadata, fout)
    # *********************************************************************        Class Methods        ********************************************************************* 
    #######################################################################  set_model (Begins) #######################################################################
   
    """
    Method for defining a model. The defined model will be saved as a class attribute.  
    """
    
    def set_model(
        self,
        model_type,
        **hparams : Any
    ):
        
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
    #######################################################################  set_model (Ends) #######################################################################

    #######################################################################  get_data_module (Begins) #######################################################################
    ################################################
    # Method for defining the data module.
    # If the model is pytorch-lightning model,
    # pl.LightningDataModule will be returned.
    # If the model is sklearn model,
    # tuple of train/val/test set will be returned.
    # TODO : Implement for standard PyTorch models.
    ################################################    
    def get_data_module(self):
        if self.model is None:
            raise AssertionError("Model must be defined first. Use .model(model_type, **hparams) to declare a model.")
        
        del self.data_module
        self.data_module = None
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
    #######################################################################  get_data_module (Ends) #######################################################################
    
    #######################################################################  set_trainer (Begins) #######################################################################
    """
    Method for getting pl.Trainer for the lightning model.

    Arguments:
            - trainer configurations : Configurations(i.e., specification of flags) of the trainer.
        Returns:
            self.trainer (pl.Trainer)

    """
   
    def set_trainer(self, **trainer_config):
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

    #######################################################################  fit (Begins) #######################################################################
    """
    Method for training. If self.model is a BaseEstimator, we use the fit function that takes sample_weights and 
    show_plots as an argument. Else, we use the fit function that takes pl.Trainer as an argument.

    ** Just in case for hasty act that we might do during the experiment, the model you trained at the last is saved to self.stack even if stack_models is False. ** 

    fit-1. For sklearn models including variants having BaseEstimator as their ancestor. e.g., xgboost, thundersvm, etc.

        Arguments: 
            - sample_weight (np.ndarray): Array of weights that are assigned to individual samples. If not provided, then each sample is given unit weight. 
            - show_plots (bool): Whether to show various plots concerning the experiment or not. Default value is False for time's sake.
        Returns:
            self.model (BaseEstimator)

    fit-2. For LightningModules having pl.LightningModule as their ancestor. 

        Arguments:
            - trainer configurations : Configurations(i.e., specification of flags) of the trainer.
        Returns:
            self.model (pl.LightningModule)

    Returns : self.model
    """
    
    ###########################################################
    ## fit-1
    def fit(
        self,
        sample_weight : Optional["np.ndarray"] = None,
        fit_or_cv : str = "FIT",
        **config : Any        
    ):
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
            raise AssertionError("v.0.0.0 doesn't support non-lightning modules.")

    def fit_sklearn(
        self,
        sample_weight : Optional["np.ndarray"] = None
    ):
        # for consistency with the logging style of pytorch_lightning.
        folder_dir = self.log_path + "/tensorboardlogs/" + self.model.__class__.__name__ 
        version = len(os.listdir(folder_dir))
        log_dir = folder_dir + "/" + self.model_metadata + "/" + "version_{}".format(version)
        self.logger = SummaryWriter(log_dir=log_dir)
        self.model.fit(self.X_train, self.y_train, sample_weight)
        y_train_preds = self.model.predict(self.X_train)
        train_acc = (self.y_train==y_train_preds).astype(float).mean()
        y_val_preds = self.model.predict(self.X_val)
        val_acc = (self.y_val==y_val_preds).astype(float).mean()
        y_test_preds = self.model.predict(self.X_test)
        test_acc = (self.y_test==y_test_preds).astype(float).mean()
        y_train_predict_proba = self.model.predict_proba(self.X_train)
        train_auc = roc_auc_score(y_true=self.y_train, y_score=y_train_predict_proba)
        y_val_predict_proba = self.model.predict_proba(self.X_val)
        val_auc = roc_auc_score(y_true=self.y_val, y_score=y_val_predict_proba)
        y_test_predict_proba = self.model.predict_proba(self.X_test)
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
         
    ## fit-2
    def fit_lightning(
        self,
        **trainer_config : Optional[Dict[str, Any]]
    ):  
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
    #######################################################################  fit (Ends)  #######################################################################
    
    #######################################################################  save_ckpt (Begins)  ####################################################################### 
    """
    Method for saving checkpoints. The logs are saved as json file as well. If self.model is a variant of sklearn, we save model states as .sav file.
    If self.model is a LightningModule, we use 'save_checkpoint' method from pl.Trainer class.

    'save_checkpoint' method from pl.Trainer class saves the followings to a .ckpt file.

        -16-bit scaling factor (if using 16-bit precision training)
        -Current epoch
        -Global step
        -LightningModule’s state_dict
        -State of all optimizers
        -State of all learning rate schedulers
        -State of all callbacks (for stateful callbacks)
        -State of datamodule (for stateful datamodules)
        -The hyperparameters used for that model if passed in as hparams (Argparse.Namespace)
        -State of Loops (if using Fault-Tolerant training)

    For beginners in pytorch-lightning, below is an example code for how to save/load checkpoints.
                                '''
                                Example code:
                                        # Saving the model after fitting
                                        model = MyLightningModule(hparams)
                                        trainer.fit(model)
                                        trainer.save_checkpoint("example.ckpt")
                                        # To load the model: 
                                        new_model = 
                                            MyLightningModule.load_from_checkpoint(checkpoint_path="example.ckpt")
                                ''' 

    Returns : None
    """
    def save_ckpt(
        self,
        model : Optional[Union["pl.LightningModule", "BaseEstimator"]] = None,
        trainer : Optional["pl.Trainer"] = None,
        val_metrics : Optional[dict] = None
    )-> None:

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
            raise NotImplementedError("Astrape v 0.0.0 only supports variants of sklearn and pl.LightningModule.")
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
    
    #######################################################################  save_ckpt (Ends)  ####################################################################### 

    #######################################################################  save_to_stack (Begins)  ####################################################################### 
    """
    Method for stacking a model to self.stack.
    If one of the ancestors of self.model is BaseEstimator, we only stack self.model.
    If one of the ancestors of self.model is pl.LightningModule, we stack a dictionary containing self.model and self.trainer.

    Returns: None 
    """
    def save_to_stack(self) -> None:
        
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
            raise AssertionError("Did not log anything.")

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
            raise NotImplementedError("Astrape only supports variants of sklearn and pl.LightningModule.")
   
    #######################################################################  save_to_stack (Ends)  #######################################################################

    #######################################################################  save_stack (Begins)  ####################################################################### 
    """
    Method for saving all model checkpoints in self.stack.
    self.stack is flushed after saving.  

    Returns: None
    """
    def save_stack(self) -> None:
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
            
        
    #######################################################################  best_ckpt_thus_far (Begins)  ####################################################################### 
    """
    Method for returning the best saved checkpoint(or the path name of the best saved checkpoint) from the directory. The criterion is the type of the validation metric.

    Arguments:
        - val_metric (str) : The validation metric of choice. This will be the criterion in determining the "best" checkpoint. Default : 'val/loss'
        - fetch_only_dir (bool) : If True, returns the path(str) of the best checkpoint. If False, returns the best checkpoint. Default : False

    Returns: 
        - None if there are no saved checkpoints
        - The best checkpoint(or the path if fetch_only_dir is True) as per the validation metric you defined in the argument. 
    """
    def best_ckpt_thus_far(self, val_metric : str = "val/acc", fetch_only_dir : bool = False):
        try:
            jsonlogdir = self.log_path + "/jsonlogs"
        except:
            print("Nothing has been saved yet.")
            return None
        mode = "min" if val_metric == "val/loss" else "max"
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
        
    #######################################################################  best_ckpt_thus_far (Ends)  ####################################################################### 


    #######################################################################  best_ckpt_in_stack (Begins)  ####################################################################### 
    """
    Method for returning the best saved checkpoint from the stack. The criterion is the type of the validation metric.

    Arguments:
        - val_metric (str) : The validation metric of choice. This will be the criterion in determining the "best" checkpoint. Default : 'val/loss'

    Returns: 
        - None if there are no saved checkpoints
        - The best checkpoint as per the validation metric you defined in the argument. 
    """
    def best_ckpt_in_stack(
        self, 
        val_metric : str = "val/acc"
    ):
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
    #######################################################################  best_model_in_stack (Ends)  ####################################################################### 

    #######################################################################  set_model_metadata (Begins)  #######################################################################
    """
    Method for generating metadata of the experiment.
    'self.model_metadata' is defined. 'self.model_metadata' would be the name of tensorboard event file.

    self.model_metadata is a string that specifies metadata for the model as follows :
    {name of the model}-{hyperparameters}-{self.random_state}
    
    Arguments:
        - hparams (dict): Hyperparameters
        - length_limit (int): Maximum tolerance for the length of the string. Default: 245
        - subtract (int): Width of the wiggle room for sanity. Default: 30

    Returns: model metadata (str)
    """
    def set_model_metadata(
        self,
        model,
        hparams : dict,
        length_limit : int = 245,
        subtract : int = 30
    ) -> str: 
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
    #######################################################################  set_model_metadata (Ends)  #######################################################################
    
    def get_hparams(self, model):
        if isinstance(model, BaseEstimator):
            return self.set_model_metadata(model, model.__dict__)
        elif isinstance(model, pl.LightningModule):
            return model.hparams
        else:
            raise AssertionError("Wrong model.")
    
    def log_metrics_to_json(
        self, 
        model,
        tensorboard_logdir: str,
        version : int,
        metrics_dict : Optional[dict] = None
    ) -> None:
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
        self.stackflag = not self.stackflag
        if self.stackflag:
            ("Switched to start stacking models...")
        else:
            ("Switched to stop stacking models...")
#   ******************************************************************* Static Methods *******************************************************************
      
    @staticmethod
    def _create_folder(directory : str) -> str:
        os.makedirs(directory, exist_ok=True)
        return directory

    @staticmethod
    def _dict_to_str(dictionary : dict) -> str:
        out = str(dictionary).replace("{", "").replace("}","").replace(" ","-").replace(":","").replace("-","").replace("\n", "-").replace('"', "").replace(".","d").replace("'","")
        return out
    #######################################################################  set_trainer (Ends) #######################################################################

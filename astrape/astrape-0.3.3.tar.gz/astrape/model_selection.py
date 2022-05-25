from itertools import product
from overrides import overrides

import pytorch_lightning as pl
from sklearn.base import BaseEstimator
from sklearn.model_selection import StratifiedKFold, train_test_split

from typing import Union, List, Dict, Any, Optional
from astrape.utilities.utils_lightning import *
from astrape.base.experiment_base import BaseExperiment
from astrape.constants.astrape_constants import *
from astrape.exceptions.exceptions import *

"""
This is a child class of BaseExperiment that performs stratified K-fold cross validation when 
the type of the model (e.g., MLP, UNet) and its candidates of hyperparameters are given. 
"""
class CrossValidation(BaseExperiment):

    def __init__(
        self,
        project_name : str,
        dims : int,
        X,
        y,
        n_classes : int,
        X_test,
        y_test,
        test_size : float,
        stack_models : bool,
        path : str,
        model_type : Union["BaseEstimator", "pl.LightningModule"],
        parameters : Dict[str, List[Any]],
        trainer_config : Optional[Dict],
        val_metric: str ='val/acc',
        cv : int = 5,
        search_type : str = 'random',
        n_random_search : Optional[int] = None,
        random_number : int = DEFAULT_RANDOM_SEED_NUMBER
    ):

        """
        parameters : Dict[str, List[Any]]   dictionary of each key being a hyperparameter(including optimizer_type), and each value being a list of candidates of such key
            example for 'parameters': 
                                           { 
                                               "n_layer_1": {
                                                # Choose from pre-defined values
                                                "values": [32, 64, 128, 256, 512]
                                                },
                                                "n_layer_2": {
                                                # Choose from pre-defined values
                                                "values": [32, 64, 128, 256, 512, 1024]
                                                },
                                                "lr": {
                                                    # log uniform distribution between exp(min) and exp(max)
                                                    "distribution": "log_scale_uniform",
                                                    "min": -9.21,   # exp(-9.21) = 1e-4
                                                    "max": -4.61    # exp(-4.61) = 1e-2
                                                }
                                            }
        trainer_config : dict    dictionary of trainer configurations
        val_metric :  str     'val/acc' or 'val/loss'
        
        """
        self.rng = np.random.default_rng(random_number)
        self.seed_num = int(10**6 * self.rng.random(1))
        
        super().__init__(
            project_name=project_name,
            X=X,
            y=y,
            n_classes=n_classes,
            X_test=X_test,
            y_test=y_test,
            test_size=test_size,
            stack_models=stack_models,
            random_number=self.seed_num,
            path=path
        )
        self.model_type = model_type
        self.trainer_config = trainer_config if trainer_config else {'max_epochs':2}
        self.search_type = search_type
        self.parameters = parameters
        self.val_metric = val_metric
        self.cv = cv
        self.dims = dims

        if 'batch_size' not in self.parameters.keys():
            self.parameters.update({'batch_size' : {'values' : [DEFAULT_BATCH_SIZE]}})
        self.jsonlog_dir = None
        self.ckpt_dir = None
        self.mode = 'max' if val_metric == 'val/acc' else 'min'
        self.best_val_score = None
        self.n_random_search = 5 if not n_random_search else n_random_search

    def get_cv_indices(self):
        skf = StratifiedKFold(n_splits=self.cv, random_state=self.random_state, shuffle=True)
        cv_indices = []
        for train_idx, val_idx in skf.split(self.X, self.y):
            cv_indices.append((train_idx, val_idx))

        return cv_indices


    def get_hparam_info(self):
        hparam_info = {}
        for hparam_name, hparam_config in self.parameters.items():
            if 'values' in hparam_config.keys():
                value_list = list(hparam_config.values())[0]
                hparam_info.update({hparam_name : value_list})
                
            elif 'distribution' in hparam_config.keys():
                value_info = {hparam_config['distribution'] : (hparam_config['min'], hparam_config['max'])}
                hparam_info.update({hparam_name : value_info})
            else:
                raise ValueError("The scheme of the values for the hyperparameters should either be 'values' or 'distribution'.")

        return hparam_info

    def get_hparams_dict_list(self):
        hparams_dict_list = []
        hparam_info = self.get_hparam_info()
        if self.search_type == 'random':
            for _ in range(self.n_random_search):
                hparams_dict = {}
                for hparam_name, value_info in hparam_info.items():
                    if isinstance(value_info, list):
                        idx = np.random.randint(low=0, high=len(value_info))
                        hparam_value = value_info[idx]
                    else: # distribution
                        for key, item in value_info.items():
                            dist_type = key
                            dist_config = item
                        if dist_type == 'uniform':
                            hparam_value = np.random.uniform(*dist_config)
                        elif dist_type == 'log_scale_uniform':
                            power = np.random.uniform(*dist_config)
                            hparam_value = 10 ** power
                    hparams_dict.update({hparam_name : hparam_value})
                hparams_dict_list.append(hparams_dict)
        elif self.search_type == 'grid':
            grid_dict = {}
            hparams_dict = {}
            for hparam_name, value_info in hparam_info.items():
                if isinstance(value_info, dict): # pick one random sample from the RV
                    for key, item in value_info.items():
                        dist_type = key
                        dist_config = item
                    if dist_type == 'uniform':
                        hparam_value = np.random.uniform(*dist_config)
                    elif dist_type == 'log_scale_uniform':
                        power = np.random.uniform(*dist_config)
                        hparam_value = 10 ** power
                    hparams_dict.update({hparam_name : hparam_value})
                else: # grid list
                    grid_dict.update({hparam_name : value_info}) 
            grid_hparam_names, grid_hparam_values = zip(*grid_dict.items())
            for bundle in product(*grid_hparam_values):
                hparams_dict = {}
                grid_sample = dict(zip(grid_hparam_names, bundle))
                hparams_dict.update(grid_sample)
                hparams_dict_list.append(hparams_dict)
        return hparams_dict_list

    def get_data_module_ms(
        self,
        X : "np.ndarray",
        y : "np.ndarray",
        batch_size : int,
        X_val : Optional["np.ndarray"] = None,
        y_val : Optional["np.ndarray"] = None,
        X_test : Optional["np.ndarray"] = None,
        y_test : Optional["np.ndarray"] = None,
        test_size : float = 0.01
    ):  
        if BaseEstimator in inspect.getmro(self.model_type):
            if (X_val or y_val) and not (X_val and y_val):
                raise ValueError("X_val and y_val should have the same # of samples.")
            if (X_test or y_test) and not (X_test and y_test):
                raise ValueError("X_test and y_test should have the same # of samples.")
            elif X_val and y_val and X_test and y_test:
                data_module = (X, X_val, y, y_val, X_test, y_test)
            elif X_test and y_test:
                X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, random_state=self.random_state, stratify=y)
                data_module = (X_train, X_val, y_train, y_val, X_test, y_test)
            elif X_val and y_val:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=self.random_state, stratify=y)
                X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, random_state=self.random_state, stratify=y)
                data_module = (X_train, X_val, y_train, y_val, X_test, y_test)
            elif X_val and y_val:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=self.random_state, stratify=y)
                data_module = (X_train, X_val, y_train, y_val, X_test, y_test)

        elif pl.LightningModule in inspect.getmro(self.model_type):
            data_module = initialize_datamodule(
                batch_size=batch_size, 
                X=X, 
                y=y,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
                test_size=test_size,
                random_state=self.random_state
            )

        return data_module

    def search(self):
        self.fit_or_cv = "CV"
        self.update_log_path()
        cv_indices = self.get_cv_indices()

        best_val_score = None
        best_hparams = None
        hparams_dict_list = self.get_hparams_dict_list()
        for hparam_idx, hparams_dict in enumerate(hparams_dict_list):
            print("Stratified {}-Fold validation with {} set of hyperparameters. Total {} runs will be conducted.".format(self.cv, len(hparams_dict_list), self.cv*len(hparams_dict_list)))
            val_score_per_run = []
            for cv_idx, (train_idx, val_idx) in enumerate(cv_indices):
                print("trying {}/{} set of hyperparameters.".format(hparam_idx+1, len(hparams_dict_list)))
                print("running {}/{} folds.".format(cv_idx+1, self.cv))
                X_train, X_val = self.X[train_idx], self.X[val_idx]
                y_train, y_val = self.y[train_idx], self.y[val_idx]
                self.model = self.set_model(
                            model_type=self.model_type,
                            **hparams_dict
                        )
                self.jsonlog_dir = self.log_path + "/logs/jsonlogs/" + self.model_metadata
                self.ckpt_dir = self.log_path + "/logs/checkpoints/" + self.model_metadata
                
                if isinstance(self.model, pl.LightningModule):
                    ckpt_extension = ".ckpt"
                elif isinstance(self.model, BaseEstimator):
                    ckpt_extension = ".sav"
                self.ckpt_dir = self.ckpt_dir + ckpt_extension

                self.data_module = self.get_data_module_ms(
                    X=X_train,
                    y=y_train,
                    batch_size=hparams_dict['batch_size'],
                    X_val=X_val,
                    y_val=y_val,
                    X_test=self.X_test,
                    y_test=self.y_test,
                    test_size=self.test_size
                )
                
                self.trainer = self.set_trainer(**(self.trainer_config))
            
                self.fit(fit_or_cv="CV",**self.trainer_config)
                self.save_ckpt()
                val_score = self.trainer.validate(self.model, self.data_module)[0][self.val_metric]
                val_score_per_run.append(val_score)

            val_score_per_run = np.array(val_score_per_run)
            avg_val_score_in_run = val_score_per_run.mean()
            
            if not best_val_score:
                best_val_score = avg_val_score_in_run
                best_hparams = hparams_dict
            else:
                if avg_val_score_in_run < best_val_score and self.mode == "min":
                    best_val_score = avg_val_score_in_run
                    best_hparams = hparams_dict   
                elif avg_val_score_in_run > best_val_score and self.mode == "max":
                    best_val_score = avg_val_score_in_run
                    best_hparams = hparams_dict
                    
        self.best_model_structure = self.best_ckpt_thus_far(val_metric=self.val_metric)[0]
        
        self.best_hparams = best_hparams
        self.best_val_score = best_val_score
        info = {
            'best_hparams' : self.best_hparams,
            self.val_metric : self.best_val_score
        }
        self.fit_or_cv = "FIT"
        return self.best_model_structure, info                    

from lib2to3.pytree import Base
from pyexpat.errors import XML_ERROR_INVALID_TOKEN

import pytorch_lightning as pl
import numpy as np
from sklearn.base import BaseEstimator

from astrape.base.experiment_base import BaseExperiment
from astrape.utilities.utils_lightning import *
from astrape.exceptions.exceptions import *
from astrape.model_selection import CrossValidation
from astrape.constants.astrape_constants import *

from typing import Union, List, Dict, Any, Optional, cast, overload

import warnings
warnings.filterwarnings(action='ignore')

class Experiment(BaseExperiment):
    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        n_classes : Optional[int] = None,
        X_test : Optional[np.ndarray] = None,
        y_test : Optional[np.ndarray] = None,
        test_size : float = 0.01,
        stack_models : bool = True,
        random_number : int = 0,
        path : Optional[str] = None
    ) -> None:
       
        super().__init__(
            project_name=project_name,
            X=X,
            y=y,
            n_classes=n_classes,
            X_test=X_test,
            y_test=y_test,
            test_size=test_size,
            stack_models=stack_models,
            random_number=random_number,
            path=path
        )
    #######################################################################  cross_validation (Begins)  ####################################################################### 
    def cross_validation(
        self,
        model_type : Union["BaseEstimator", "pl.LightningModule"],
        parameters : Dict[str, List[Any]],
        search_type : str = "random",
        val_metric : str = 'val/acc',
        trainer_config : Optional[Dict] = None,
        n_random_search : Optional[int] = None,
        cv : int = 5,
        random_number : int = DEFAULT_RANDOM_SEED_NUMBER 
    ):
        self.fit_or_cv = "CV"
        self.update_log_path()
        best_model_structure, info = CrossValidation(
            project_name=self.project_name,
            dims=self.dims,
            X=self.X,
            y=self.y,
            n_classes=self.n_classes,
            X_test=self.X_test,
            y_test=self.y_test,
            test_size=self.test_size,
            stack_models=self.stack_models,
            path=self.path,
            model_type=model_type,
            parameters=parameters,
            trainer_config=trainer_config,
            val_metric=val_metric,
            cv=cv,
            search_type=search_type,
            n_random_search=n_random_search,
            random_number=random_number
        ).search()
        self.fit_or_cv = "FIT"
        return best_model_structure, info
        
    
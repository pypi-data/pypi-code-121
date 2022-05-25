import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class MLFlowClient(dbclient):
    #TODO pagination logic
    def get_experiments_list(self):
        """ 
        Returns an array of json objects for experiments. 
        """
        # fetch all experiments
        expList = self.get("/mlflow/experiments/list", version='2.0').get('experiments', [])
        return expList
    #TODO pagination logic
    def get_registered_models(self):
        """ 
        Returns an array of json objects for registered models. 
        """
        # fetch all registered models
        modList = self.get("/preview/mlflow/registered-models/list", version='2.0').get('registered_models', [])
        return modList


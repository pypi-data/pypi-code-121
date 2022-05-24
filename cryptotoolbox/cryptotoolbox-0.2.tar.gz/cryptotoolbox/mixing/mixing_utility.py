
import numpy as np

from cryptotoolbox.mixing import linear_model_wrapper
from cryptotoolbox.mixing import lasso_model_wrapper
from cryptotoolbox.mixing import lgbm_model_wrapper
from cryptotoolbox.mixing import xgb_model_wrapper
from cryptotoolbox.mixing import standard_mean_model_wrapper
from cryptotoolbox.mixing import deterministic_sharpe_optim_model_wrapper
from cryptotoolbox.mixing import to_weighted_mean_model_wrapper
from cryptotoolbox.mixing import max_occurence_model_wrapper
from cryptotoolbox.mixing import erc_allocation_model_wrapper
from cryptotoolbox.mixing import mvp_allocation_model_wrapper
from cryptotoolbox.mixing import mvp_uc_allocation_model_wrapper
from cryptotoolbox.mixing import ivp_allocation_model_wrapper
from cryptotoolbox.mixing import hrp_allocation_model_wrapper

from abc import ABC, abstractmethod


def instantiate_model(method, idios=None):
    if method == 'standard':
        return linear_model_wrapper.LinearModel()
    if method == 'lasso':
        return lasso_model_wrapper.LassoModel()
#        alpha = 0.1
#        self.model = Lasso(alpha=alpha, fit_intercept=False, max_iter=5000)
    if method == 'lgbm':
        return lgbm_model_wrapper.LGBMModel()
    if method == 'xgb':
        return xgb_model_wrapper.XGBModel()
    if method == 'standard_mean':
        return standard_mean_model_wrapper.MeanModel()
    if method == 'to_weighted_mean':
        return to_weighted_mean_model_wrapper.WeightedMeanModel()
    if method == 'deterministic_sharpe_optim':
        return deterministic_sharpe_optim_model_wrapper.DeterministicSharpeOptimModel()
    if method == 'max_occurence':
        return max_occurence_model_wrapper.MaxOccurenceModel()
    if method == 'erc_allocation_model':
        return erc_allocation_model_wrapper.ERC_Allocation_Model()
    if method == 'mvp_allocation_model':
        return mvp_allocation_model_wrapper.MVP_Allocation_Model()
    if method == 'mvp_uc_allocation_model':
        return mvp_uc_allocation_model_wrapper.MVP_uc_Allocation_Model()
    if method == 'ivp_allocation_model':
        return ivp_allocation_model_wrapper.IVP_Allocation_Model()
    if method == 'hrp_allocation_model':
        return hrp_allocation_model_wrapper.HRP_Allocation_Model()



def report_best_scores(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")

class AbstractForecasterWrapper(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def calibrate(self, X, y):#, method = 'standard'):
        pass

    @abstractmethod
    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        pass

    @abstractmethod
    def predict(self, X_test):#, method = 'standard'):
        pass

    @abstractmethod
    def get_features_importance(self, features_names):#, method = 'standard'):
        pass

################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import pandas as pd
import numpy as np
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from collections import namedtuple
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.base import BaseEstimator
from autoai_ts_libs.srom.estimators.time_series.models.base import SROMTimeSeriesForecaster
from autoai_ts_libs.srom.estimators.time_series.models.T2RForecaster import T2RForecaster
from sklearn.base import clone
from sklearn.utils.validation import check_array
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.utils.score import Score
from typing import List

class MT2RForecaster(BaseEstimator, SROMTimeSeriesForecaster):
    """
    Trend-to-Residual Multi-Step Multi-Variate Singal Predictor.
    Parameters
    ----------
        target_columns : (list of int) index of target cols .
        trend : (string, default = Linear) Trend model to be used. It can be Linear, Difference. 
        residual : (string, default = Linear) Residual model to be used. It can be Linear.     
        lookback_win : (int or string, default = auto) Look-back window for the model.
        prediction_win : (int, optional, default = 12) Look-ahead window for the model.
        n_jobs : (int, optional, default = -1) no of jobs.
    """

    def __init__(
        self,
        time_column=-1,
        feature_columns=[0],
        target_columns=[0],
        trend="Linear",
        residual="Linear",
        lookback_win="auto",
        prediction_win=12,
        n_jobs=-1,
    ):
        self.time_column = time_column
        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.trained_models = []
        self.trend = trend
        self.residual = residual
        if lookback_win == "auto" or isinstance(lookback_win,int):
            self.lookback_window = lookback_win
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0086E'))
        self.prediction_win = prediction_win
        self.base_model = T2RForecaster(
            trend=self.trend,
            residual=self.residual,
            lookback_win=self.lookback_window,
            prediction_win=self.prediction_win,
        )
        self.target_columns = target_columns

        if n_jobs == -1:
            n_jobs = cpu_count() -1
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = min(len(target_columns), n_jobs)

    def _adjust_indices(self, target_columns: List[int]=[], feature_columns: List[int]=[]):
        """Adjusts feature and target columns as specified by calling the _adjust_indices function 
        (if available) for all the steps in the pipeline. This is intended to be used on
        non-exogenous pipelines so that only the required columns are needed in calls to fit/predict.
        Args:
            target_columns (List[int], optional): New target columns to use. Defaults to [].
            feature_columns (List[int], optional): New feature columns to use. Defaults to [].
        """
        if self.is_exogenous_pipeline_:
            raise RuntimeError("Should not call adjust_indices on an exogenous pipeline")

        self.target_columns = target_columns
        self.feature_columns = feature_columns


    def __setstate__(self, state):
        super().__setstate__(state)
        if not hasattr(self, "feature_columns"):
            self.feature_columns = None
        if not hasattr(self, "time_column"):
            self.time_column = -1
    
    def _check_meta_data(self):
       if not set(self.target_columns).issubset(set(self.feature_columns)):
            raise Exception(
                "1 or more `target_col_index` are not present in `feature_col_index`"
            )

    @property
    def lookback_win(self):
        """
        """
        return self.lookback_window

    @property
    def lookback_window(self):
        """
        """
        if not hasattr(self,"lookback_window_"):
           self.lookback_window_ = 'auto'
           self.is_auto_lookback_win_ = True 

        if self.is_auto_lookback_win_:
            if len(self.trained_models) > 0 :
                lookback_win = []
                for model in self.trained_models:
                    lookback_win.append(model.i_lookback_win)
                return max(lookback_win)
            else:
                return self.lookback_window_
        elif isinstance(self.lookback_window_,int):
            return self.lookback_window_
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0086E'))

    @lookback_window.setter
    def lookback_window(self,lookback_win):
        """
        """
        if lookback_win == "auto":
            self.is_auto_lookback_win_ = True
        else:
            self.is_auto_lookback_win_ = False    
        self.lookback_window_ = lookback_win
            
    def name(self):
        return "MT2RForecaster"

    def _get_exogenous_cols(self):
        """"""
        exogenous_cols = []
        for fc in self.feature_columns:
            if not fc in self.target_columns:
                exogenous_cols.append(fc)
        return exogenous_cols

    def _fit_single_model(self, X, idx, i):
        _x = X[:, i]
        model_i = self.trained_models[idx]
        model_i.fit(_x)
        return model_i

    def _parallel_fit(self, X, y=None):
        """
        Utility to parallelize the code.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []
        self.trained_models = Parallel(n_jobs=self.n_jobs)(
            delayed(self._fit_single_model)(X, idx, [item] + exogenous_cols)
            for idx, item in enumerate(self.target_columns)
        )

    def _sequential_fit(self, X, y=None):
        """
        Utility to run code sequentially.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns !=None:
            exogenous_cols = self._get_exogenous_cols()
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []

        for idx, i in enumerate(self.target_columns):
            cols = [i] + exogenous_cols
            _x = X[:, cols]
            self.trained_models[idx].fit(_x)
    
    def fit(self, X, y=None):
        """
        Fit the model.
        Parameters
        ----------
            X : (numpy array) input data.
        
        """
        
        # first time we create an empty model for each variable
        
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            self._check_meta_data()
            exogenous_cols = self._get_exogenous_cols()
            feature_columns = (
                list(range(0, len(exogenous_cols) + 1)) if len(exogenous_cols) > 0 else [0]
            )
            if len(self.trained_models) == 0:
                for i, col in enumerate(self.target_columns):
                    self.trained_models.append(
                        T2RForecaster(
                            trend=self.trend,
                            target_columns=[0],
                            feature_columns=feature_columns,
                            residual=self.residual,
                            lookback_win=self.lookback_win,
                            prediction_win=self.prediction_win,
                        )
                    )
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            for idx, _ in enumerate(self.target_columns):
                self.trained_models.append(clone(self.base_model))
                
        
        if self.n_jobs > 1:
            self._parallel_fit(X)
        else:
            self._sequential_fit(X)
        return self

    def _sequential_predict(self, X=None, future_exogenous=None):
        """
        This function is for predicting future.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
            pred_args = {"future_exogenous":future_exogenous}
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []
            pred_args = {}

        for idx, i in enumerate(self.target_columns):
            # When X is none don't pass any input.
            if X is None:
                pred = self.trained_models[idx].predict(**pred_args)

            else:
                cols = [i] + exogenous_cols
                try:
                    pred = self.trained_models[idx].predict(X=X[:, cols], **pred_args)
                except Exception as e:
                    raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0055E'))
            if len(self.trained_models) > 1:
                reshaped = pred.reshape(-1, 1)
                if idx == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = pred
        return result.flatten().reshape(-1, len(self.trained_models))

    def _predict(self, X, idx, index, future_exogenous=None):
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            pred_args = {"future_exogenous":future_exogenous}
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            pred_args = {}

        # When X is none don't pass any input.
        if X is None:
            pred = self.trained_models[idx].predict(**pred_args)
        else:
            pred = self.trained_models[idx].predict(X=X[:, index], **pred_args)

        return pred

    def _parallel_predict(self, X=None, future_exogenous=None):
        """
        Utility to parallelize the code.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
            pred_args = {"future_exogenous":future_exogenous}
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []
            pred_args = {}
        
        ret_preds = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict)(X, idx, [item] + exogenous_cols, **pred_args)
            for idx, item in enumerate(self.target_columns)
        )

        for i, row in enumerate(ret_preds):
            if len(self.trained_models) > 1:
                reshaped = row.reshape(-1, 1)
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = row
        return result.flatten().reshape(-1, len(self.trained_models))

    def predict(self, X=None, future_exogenous=None, prediction_type=None):
        """
        This is to predict.
        Parameters
        ----------
            X : (numpy array) input data. It can be none as well.
            prediction_type : It can be sliding_window or forecast. Default is forecast.
        Returns
        -------
            numpy array.
        """
        if X is not None:
            X = check_array(X, dtype=np.float64, force_all_finite=False, ensure_2d=False, ensure_min_samples=0)
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        if prediction_type is not None:
            if prediction_type.lower() == Score.PREDICT_SLIDING_WINDOW:
                if self.prediction_win == 1:
                    return self.predict_sliding_window(X)
                elif self.prediction_win > 1:
                    return self.predict_multi_step_sliding_window(X,self.prediction_win)
                else:
                    raise Exception(Messages.get_message(prediction_type, message_id='AUTOAITSLIBS0046E'))
            elif prediction_type.lower() != Score.PREDICT_FORECAST:
                raise Exception(Messages.get_message(prediction_type, message_id='AUTOAITSLIBS0046E'))
        
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
            pred_args = {"future_exogenous":future_exogenous}
            is_exo = True
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []
            pred_args = {}
            is_exo = False
        
        if isinstance(X, pd.DataFrame):
            X = np.array(X)
        if self.n_jobs > 1:
            return self._parallel_predict(X, **pred_args)
        else:
            return self._sequential_predict(X, **pred_args)

    #def _predict_single_model(self, X, idx, i):
    #    return self.trained_models[idx].predict_sliding_window(X[:, i])

    def _predict_single_model(self, X, idx, i):
        return self.trained_models[idx].predict_sliding_window(
            X[:, i].reshape(-1, len(i))
        )

    def _parallel_predict_sliding_window(self, X):
        """
        utility to parallelize the code.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []            
        
        self.ret_ans = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_single_model)(X, idx, [item] + exogenous_cols)
            for idx, item in enumerate(self.target_columns)
        )

        return pd.DataFrame(self.ret_ans).T.values

    def predict_sliding_window(self, X):
        """
        This method is for single step prediction.
        Parameters
        ----------
            X : (numpy array) input data.
        Returns
        -------
            numpy array.
        """
        y = self._parallel_predict_sliding_window(X)
        return y.reshape(-1, len(self.trained_models))

    def _predict_single_multi_step_model(self, X, idx, i, prediction_win):
        return self.trained_models[idx].predict_multi_step_sliding_window(
            X[:, i], prediction_win
        )

    def _parallel_predict_multi_step_sliding_window(self, X, prediction_win):
        """
        internal function for predict.
        """
        ### Backward compatibility 1258
        ###
        ### Code with exogenous support
        if self.feature_columns!=None:
            exogenous_cols = self._get_exogenous_cols()
        else:
        ### Backward compatibility 1258
        ###
        ### Code prior to exogenous support
            exogenous_cols = []            

        self.ret_ans = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_single_multi_step_model)(
                X, idx, [item] + exogenous_cols, prediction_win
            )
            for idx, item in enumerate(self.target_columns)
        )

        ret_ans = np.empty(
            [self.ret_ans[0].shape[0], prediction_win * len(self.trained_models)]
        )
        for dim_i in range(len(self.ret_ans)):
            for row_i in range(self.ret_ans[0].shape[0]):
                for col_i in range(prediction_win):
                    ret_ans[
                        row_i, col_i * len(self.trained_models) + dim_i
                    ] = self.ret_ans[dim_i][row_i, col_i]
        return ret_ans

    def predict_multi_step_sliding_window(self, X, prediction_win):
        """
        This method is for multi step prediction.
        Parameters
        ----------
            X : (numpy array) input data.
            prediction_win : (int, default=12) look ahead to be used for prediction.
        Returns
        -------
            numpy array.
        """
        y = self._parallel_predict_multi_step_sliding_window(X, prediction_win)
        return y.reshape(-1, len(self.trained_models))

    def predict_proba(self, X=None):
        """
        Prediction probability.
        Parameters
        ----------
            X : numpy array.
        Returns
        -------
            y : numpy array
        """
        if self.n_jobs > 1:
            return self._parallel_predict_proba(X)
        else:
            return self._sequential_predict_proba(X)

    def _sequential_predict_proba(self, X=None):
        """
        Helper function for predict_proba.
        """
        for idx, i in enumerate(self.target_columns):
            # When X is none don't pass any input.
            if X is None:
                pred = self.trained_models[idx].predict_interval()
            else:
                pred = self.trained_models[idx].predict_interval(X[:, i])
            # reshape by column and append by column.
            reshaped = pred.reshape(-1, 1, 2)
            if len(self.trained_models) > 1:
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = reshaped
        return result

    def _predict_proba(self, X, idx, index):
        # When X is none don't pass any input.
        if X is None:
            pred = self.trained_models[idx].predict_interval()
        else:
            pred = self.trained_models[idx].predict_interval(X[:, index])

        return pred

    def _parallel_predict_proba(self, X=None):
        """
        Helper function for predict_proba.
        """

        ret_preds = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_proba)(X, idx, item)
            for idx, item in enumerate(self.target_columns)
        )

        for i, row in enumerate(ret_preds):
            reshaped = row.reshape(-1, 1, 2)
            if len(self.trained_models) > 1:
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = reshaped
        return result

    @property
    def is_exogenous_pipeline_(self):
        """"""
        if self.feature_columns!=None:
            if (len(self.feature_columns) != len(self.target_columns) and set(self.target_columns).issubset(set(self.feature_columns))):
                return True
            else:
                return False
        return False

    @property
    def is_future_exogenous_pipeline_(self):
        """"""
        return self.is_exogenous_pipeline_

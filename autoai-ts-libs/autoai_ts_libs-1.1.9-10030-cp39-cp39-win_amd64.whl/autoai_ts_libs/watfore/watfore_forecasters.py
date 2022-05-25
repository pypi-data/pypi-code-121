# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2020, 2022, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************
"""
@author: Syed Yousaf Shah (syshah@us.ibm.com)
Updated : Dec 1, 2021 for backward compatibility
Updated : Sep 12, 2021 for exogenous
TS LIB client file
This is a wrapper that wraps forecasting algorithms in fit/transform fashion implementing autoai_api.
"""
import logging
import pickle

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_array, check_is_fitted

from autoai_ts_libs.watfore.watfore_utils import WatForeUtils
import autoai_ts_libs.utils.imputer_helper as imputer_helper

from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.utils.score import Score

logger = logging.getLogger(__name__)
logger.setLevel('WARNING')

try:
    #from tspy import TSContext
    import autoai_ts_libs.deps.tspy as tspy
    from autoai_ts_libs.watfore.watfore_utils import WatForeUtils
    import autoai_ts_libs.utils.watfore as wf

except Exception as e:
    print("Exception importing tspy")

EXOGENOUS_MODELS = {'arimax', 'arimax_palr', 'arimax_rsar', 'arimax_rar', 'arimax_dmlr'}
class WatForeForecaster(BaseEstimator):

    """
    Forecaster using WatFore library. This class is an estimator for watfore forecasting models exposing
    watfore forecasters/prediction algorithms via fit/transform methods
      Parameters
      ----------
      algorithm : str, default='hw'
        For ease of use algorithm can be chosen from watfore.Forecasters.*, e.g., watfore.Forecasters.arima
        Algorithm that is used to initialize the prediction model. Currently supported are 'hw' i.e. holtwinters,
          'arima','bats', autoforecaster i.e., BATS model with Box-Conx transformation. Algorithm specific parameters
          also need to be specified.
        Additive and multiplicative variants of the Holt-Winters Seasonal forecasting method. This implementation of
        the Holt-Winter algorithm variants assumes that the data it receives satisfy the above conditions.
        Any pre-processing the data needs in order to satisfy the above assumptions should take place prior to model
        updates and calls for prediction. This approach was followed in order to allow any type of pre-processing
        (for example for filling missing values) on the data, independent of the H-W core calculations.
        Implementation of BATS (Box-Cox transform, ARMA errors, Trend, and Seasonal components) Algorithms
        Reference: Alysha M De Livera, Rob J Hyndman and Ralph D Snyder, "Forecasting time series with complex seasonal
        patterns using exponential smoothing," Journal of the American Statistical Association (2011) 106(496), 1513-1527.
        If algorithm = autoforecaster, This trains all models and to keep running statistics on their forecasting
        errors as updates are requested. The error statistics are used to continually update the selection
        of the best model, which is used to do the forecasts in the super class. The algorithm becomes initialized as
        soon as the first algorithm becomes initialized so as to allow forecasts as soon as possible. It continues to
        rate new algorithms as they become initialized and/or subsequent updates are applied.
      use_full_error_history : boolean, default=True
        (ARIMA and HoltWinters (hw) ONLY) Trains arima model using full
        error history from the data. If False, then only the last errorHorizonLength updates will be considered in the
        values returned. The resulting instance:
        1. does not force a model if suitable orders and/or coefficients can not be found. This can result in a model
        which can not be initialized.
        2.picks the required amount of training data automatically.
        3.finds the AR order automatically.
        4. finds the MA order automatically.
        5.finds the difference order automatically.
      error_horizon_length : int, default=1
        (ARIMA ONLY) This parameter is used only when algroithm='arima' or watfore.Forecasters.arima, this is error horizon for
        error in arima model.
      force_model : boolean, default=False
        (ARIMA ONLY) If True, then force the selection of a model based on the given orders, regardless of suitability. If False,
        then the model may never become initialized if suitable coefficients for the training data can not be identified.
      min_training_data : int, default =-1
        (ARIMA ONLY) The amount of training data to use to learn the coefficients. May be non-positive, in which case the minimum
        amount of training data will be determined by the pMax and qMax values.
      p_min : int, default = 0
        (ARIMA ONLY) Minimum AR order to be selected during training. Must be 0 or larger.
      p_max : int, default = -1
        (ARIMA ONLY) Maximum AR order to be selected during training. If less than 0, then the maximum supported order will be used,
         otherwise, must be at least as large as pMin.
      q_min : int, default = 0
        (ARIMA ONLY) Minimum AR order to be selected during training. Must be 0 or larger.
      q_max : int, default = 0
        (ARIMA ONLY) Maximum MA order to be selected during training. If less than 0, then the maximum supported order will be used,
         otherwise, must be at least as large as qMin.
      algorithm_type : str, default="additive"
        (HoltWinters(hw) ONLY, i.e. when algorithm=watfore.Forecasters.hw or algorithm='hw')
        "additive" provides implementation of the additive variant of the Holt-Winters Seasonal forecasting method.
        The additive variant has the seasonal and trend/slope components enter the forecasting function in an
        additive manner (see ref. 1), as in
        See http://books.google.com/books?id=GSyzox8Lu9YC&source=gbs_navlinks_s for more information.
        y(t+h) = L(t) + t*H(t) + S(t+h)
        where
        t = latest time for which the model has been updated
        h = number of steps ahead for which a forecast is desired
        L(t) = is the level estimate at time t
        H(t) = is the slope at time t
        S(t+h) = is the seasonal component at time t + h.
        "multiplicative", provides implementation of the multiplicative variant of the Holt-Winters Seasonal forecasting
        method. The multiplicative variant has the seasonal and trend/slope components enter the forecasting function
        in a multiplicative manner (see ref. 1, Brockwell, pp. 329).
        y(t+h) = (L(t) + t* H(t)) * S(t+h)
      samples_per_season : int, default =2
       (hw ONLY)
       Season length, or if compute_seasonality is True, then the maximum season to allow. If used as a maximum season,
       then identification of the season length (and thus forecasting) can not happen until samples_per_season
       * initial_training_seasons of data are provided.
      initial_training_seasons : int , default =2
       (hw ONLY) Number of seasons to use in training. Must be greater than 1.
      compute_seasonality : boolean, default= False
        (hw ONLY) If true then automatically compute seasonality.
      error_history_length : int, default=1
        (hw ONLY)
      training_sample_size : int,
        (BATS(bats) ONLY, i.e. when algorithm=watfore.Forecasters.bats or algorithm='bats')
        training sample size, recommended #samples = 2*maximum_cycle_length
      box_cox_transform : boolean, default=False
       (BATS(bats) ONLY, i.e. when algorithm=watfore.Forecasters.bats or algorithm='bats')
       Only estimate Box-Cox parameter if True; otherwise, ignore Box-Cox transform
      ts_icol_loc : array [int], default= -1
        This parameter tells the forecasting model the absolute location of the timestamp column. For specifying
         time stamp location put value in array e.g., [0] if 0th column is time stamp. The array is to support
         multiple timestamps in future. If ts_icol_loc = -1 that means no timestamp is provided and all data is
         time series. With ts_icol_loc=-1, the model will assume all the data is ordered and equally sampled.
      target_column_indices : array [int], default= -1
        This parameter tells the forecasting model the absolute location of the target column(s) that need to be
        used for training model(s). While fiting the specified column(s) are used for training and are predicted
        subsequently in the predict function. Default is -1 which will assume all columns except timestamp
        are targets.
      feature_column_indices : array [int], default= -1
        This parameter tells the forecasting model the absolute location of the feature column(s) that need to be used
        for training model(s) with exogenous variable support. If target_column_indices = -1 that means there is no
        exogenous variable that is used to train model for target specified by target_column_indices.

      """


    def __init__(self, algorithm='hw', algorithm_type="additive", ts_icol_loc=-1, prediction_horizon=1,
                 log_transformed=True, lookback_win=1, target_column_indices=-1, feature_column_indices = -1, debug=False,
                 difference_all_data = True, disable_difference = False, diff_eta=True,  **kwargs):

        self.difference_all_data = difference_all_data
        self.disable_difference = disable_difference
        self.diff_eta = diff_eta

        self.ts_icol_loc = ts_icol_loc
        self.target_column_indices = target_column_indices
        self.feature_column_indices = []
        self.feature_column_indices = feature_column_indices
        #Assumption is exogenous Column = feature Columns - target_columns.

        self.exog_column_indices = -1#
        self.last_exogenous_values = None # store last values of exogenous to be used for predict(None)
        self._timestamps = None
        self.prediction_horizon = prediction_horizon
        #self.algorithm = 'hw'
        self._totalsamples = None # total samples used to train models
        self.lookback_win = lookback_win
        #if 'debug' in kwargs:
         #   self.debug = kwargs['debug']
        self.debug = debug
        self.model=[]
        self.model_dumps = [] #only used when pickle.dump is called to stor models befor pickle
        # This is to keep actual model untouched at predict time,
        # Any updates will be done to this not orignally trained model
        self.model_update_predict = None
        # Compatible for both python 3.8 and 3.9
        self.log_transformed = kwargs['log_transform'] if 'log_transform' in kwargs else log_transformed
        self.compute_periodicity = True
        self.model_description = None
        self.model_family = 'statistical'
        self.model_name = 'hw'
        self.model_id = None # st for statistical
        self.n_targets_ = -1
        self.n_features_ = -1 # set to -1 by default
        self.is_exogenous_pipeline_ = False# default to false
        if -1 != self.feature_column_indices and -1 != self.target_column_indices:
            self.exog_column_indices = list(set(feature_column_indices) - set(target_column_indices))
            if len(self.exog_column_indices) > 0:
                self.n_features_ = len(self.exog_column_indices)

        #self.MAX_INIT_SEASONS = 2

        if algorithm != 'None' and algorithm is not None:
            self.algorithm = algorithm
            self.model_name = algorithm

        if self.algorithm.lower() in EXOGENOUS_MODELS:
            self.is_exogenous_pipeline_ = True
        self.algorithm_type = algorithm_type

        #self.wfts_context = None #wfts_context #context if already open.

        #self.wt_forecasters= self.wfts_context.forecasters
        #print(kwargs)
        self.all_args = kwargs

        #self.all_args['algorithm'] = self.algorithm
        self.all_args['algorithm'] = self.algorithm
        self.all_args['algorithm_type'] = self.algorithm_type

        ###SOME DEFAULTS
        #self.all_args['min_training_data'] = 0.999999 # Use all of samples for training
        #self.all_args['training_sample_size'] = 0.999999 # Use all of samples for training

        #print(ts_icol_loc)

    def get_model_params(self):
        return self.all_args

    def is_prediction_valid(self,true_value, predicted_value):
        limit = 90
        smape_error = 95
        smape_error = WatForeUtils.adjusted_smape(true_value,predicted_value)
        if smape_error < limit:
            return  True
        else:
            return False

    def initialize_hw_multiplicative(self,model_col,vals_df_array):

        model_initialized = False
        ###########################################################
        itr = 0
        init_sizes = [0.99, 0.90, 0.80, 0.70, 0.50,0.40,0.30]
        valid_predictions = False
        while (not model_initialized) and itr < len(init_sizes):
            hw_min_train_size = init_sizes[itr]
            itr = itr + 1
            try:
                #print("HW multiplicative MIN TRAINING ====== ",hw_min_train_size)
                self.all_args['min_training_data'] = hw_min_train_size
                self.model[model_col] = self._getModel(**self.all_args)
                self.model[model_col].update_model(self._timestamps, vals_df_array[model_col].tolist())
                model_initialized = self.model[model_col].is_initialized()
                valid_predictions = False
                # check valid predicitons
                if model_initialized:
                    prediction = self.model[model_col].forecast_at(self.get_last_updated())
                    if self.debug:
                        print('Predictions == ', prediction, 'Last value==', vals_df_array[model_col][-1],
                              'min_training_data', hw_min_train_size)
                    # not exactly true value but just to get estimate of predictions
                    valid_predictions = self.is_prediction_valid(vals_df_array[model_col][-1], prediction)
                # both has to be true to declare model as initialized
                # print ("MODEL TRAINIGN STATUS=========",hw_min_train_size)
            except  BaseException as e:
                # er = str(e)
                # raise (Exception(er))
                logger.warning("Failed to train/update Model.", e)

            #print('BEFORE model_initialized', model_initialized, 'valid_predictions',valid_predictions)
            model_initialized = model_initialized and valid_predictions
            #print('After model_initialized', model_initialized)

        #print('check model_initialized', model_initialized)
        if not model_initialized:
            self.model[model_col].reset_model()
            logger.warning("Failed to train/update HW Multiplicative Model.")

    def name(self):
        return "WatForeForecaster"


    def get_train_size(self):
        for m in self.model:
            if m.is_initialized:
                #print(self._totalsamples)
                self._totalsamples = m.last_time_updated + 1 # Assuming start training at ts=0 # This won't work for real ts
                #print('getting from model',self._totalsamples)
                #return m.last_time_updated
        #return self.model[0].last_time_updated # this can be used instead to get state directly from model, model index has to be checked!!!
        #print('getting from Ts')
        return self._totalsamples # starts training at ts=0 unless ts specified

    def get_last_updated(self, inmodle_array= None):
        last_updated = -1
        #print(self.model_name)
        #########Special case for exogenous till we make m.last_time_updated available via java models##################
        if self.model_name in EXOGENOUS_MODELS:
            if 0 < len(self._timestamps):
                last_updated =self._timestamps[-1]
            return last_updated

        ################################################################################################################
        if inmodle_array is not None:
            for m in inmodle_array:
                if m.is_initialized:
                    # Assuming start training at ts=0 # This would assume multiple time series were update at same time
                    last_updated = m.last_time_updated
                    #print('predict model last updated ', last_updated)
        else:
            for m in self.model:
                if m.is_initialized:
                    last_updated = m.last_time_updated  # Assuming start training at ts=0 # This would assume multiple time series were update at same time

        return last_updated  # starts training at ts=0 unless ts specified

    # Timestamps/sample interval during traing of model
    def get_train_interval(self):
        interval = -1
        #########Special case for exogenous till we make m.last_time_updated available via java models##################
        if self.model_name in EXOGENOUS_MODELS:
            if 1 < len(self._timestamps):
                interval = self._timestamps[-1] - self._timestamps[-2]

            return interval
        ################################################################################################################
        for m in self.model:
            if m.is_initialized:
                interval = m.average_interval  # Assuming start training at ts=0 # This won't work for real ts

        return interval


    # overloaded function to set model's custom parameters
    def set_params(self, **params):
        # self.set_params(params)
        self.all_args = params
        # print(self.all_args)
        return self

    def _getModel(self, **kw_args):
        """
        Returns model for respective algorithm.
        """

        # print('Forecaster called with ', algorithm,kw_args)
        algorithm = kw_args['algorithm']

        ##Exogenous model params###########################
        ##self, difference_all_data=False, disable_difference=False, diff_eta=False
        difference_all_data = self.difference_all_data
        disable_difference = self.disable_difference
        diff_eta = self.diff_eta

        if 'difference_all_data' in kw_args.keys():
            difference_all_data = kw_args['difference_all_data']
        if 'disable_difference' in kw_args.keys():
            disable_difference = kw_args['disable_difference']
        if 'diff_eta' in kw_args.keys():
            diff_eta = kw_args['diff_eta']
        ###Exogenous varaibles###############################
        if 'arimax' == algorithm.lower():
            #parse the parameters
            return tspy.forecasters.arimax(disable_difference= disable_difference,
                                                          difference_all_data=difference_all_data, diff_eta=diff_eta)
        if 'arimax_palr' == algorithm.lower():
            # parse the parameters
            return tspy.forecasters.arimax_palr(disable_difference= disable_difference,
                                                          difference_all_data=difference_all_data, diff_eta=diff_eta)
        # if 'arimax_rsr' == algorithm.lower():
        #     # parse the parameters
        #     return tspy.forecasters.arimax_rsr(disable_difference= disable_difference,
        #                                                   difference_all_data=difference_all_data, diff_eta=diff_eta)
        if 'arimax_rsar' == algorithm.lower():
            # parse the parameters
            return tspy.forecasters.arimax_rsar(disable_difference= disable_difference,
                                                          difference_all_data=difference_all_data, diff_eta=diff_eta)
        if 'arimax_rar' == algorithm.lower():
            return tspy.forecasters.arimax_rar(disable_difference= disable_difference,
                                                          difference_all_data=difference_all_data, diff_eta=diff_eta)
        if 'arimax_dmlr' == algorithm.lower():
            return tspy.forecasters.arimax_dmlr(disable_difference= disable_difference,
                                                          difference_all_data=difference_all_data, diff_eta=diff_eta)

        ######################################################
        # print(type(algorithm))
        if 'hw' == algorithm.lower():
            alg_args = {}
            # GOES IN FULL automatic mode finds samples per seaons and init seasons from data and initializes model
            if 'min_training_data' in kw_args.keys():
                #print ('==============',kw_args['min_training_data'] )
                number_of_samples = kw_args['min_training_data']

                if number_of_samples < 1 and kw_args['min_training_data'] >=0.99:
                    number_of_samples = self._totalsamples
                if number_of_samples < 1 and kw_args['min_training_data'] <0.99:
                    number_of_samples = int(self._totalsamples*number_of_samples)

                #cap samples used for init
                number_of_samples = min(number_of_samples, 1000000) #1Milion
                ###########SET DESCRIPTIONS ETC####
                if ('algorithm_type' not in kw_args.keys()) or not kw_args["algorithm_type"]:
                    alg_args['algorithm_type'] = 'additive' # Default is additive
                else:
                    alg_args['algorithm_type'] = kw_args['algorithm_type']

                alg_args['number_of_samples'] = number_of_samples
                alg_args['min_training_data'] = kw_args['min_training_data']
                alg_args['is_season_length'] = False

                if '_' not in self.algorithm or '_' not in self.model_name:  # Daub gives back the same object if not checked it will keep appending
                    # self.algorithm = self.algorithm + '_' + alg_args['algorithm_type']  # can't do this
                    self.model_name = self.algorithm + '_' + alg_args['algorithm_type']  # avoid duplicate concatenation

                self.model_id = WatForeForecaster.get_model_id(algorithm, **alg_args)
                self.model_description = self.algorithm + '_' + str(alg_args)

                ###########################################
                #print('New COnstructor ALL ARGS:',alg_args)
                #print('New COnstructor modelid:', self.model_id)
                return tspy.forecasters.hws(is_season_length=alg_args['is_season_length'],
                                                         number_of_samples= int(alg_args['number_of_samples']),
                                                         algorithm_type=alg_args['algorithm_type'])


            # required params

            alg_params = ['samples_per_season', 'initial_training_seasons', 'algorithm_type', 'compute_seasonality'
                , 'error_history_length', 'use_full_error_history']
            for par in alg_params:
                if par in kw_args and kw_args[par] is not None:
                    # print(kw_args[par])
                    # print(par)
                    # print(kw_args[par])
                    if par == 'samples_per_season' or par == 'error_history_length':
                        # print(self.all_args)
                        # print(kw_args[par])
                        if kw_args[par] < 1 and self._totalsamples is not None:
                            # if par == 'samples_per_season' and kw_args[par] > 0.5:
                            if kw_args[par] > 0.5:
                                kw_args[par] = 0.5  # atleast 2 seasons needed i.e., init seasons
                            #alg_args[par] = int(kw_args[par] * self._totalsamples)  # parameters from range
                            alg_args[par] = int(round(kw_args[par] * self._totalsamples, 14))
                            if alg_args[par] <= 0:
                                alg_args[par] = 2

                            # self.all_args[par] = alg_args[par]
                            # print (self.all_args[par])
                        else:
                            alg_args[par] = kw_args[par]

                    else:
                        alg_args[par] = kw_args[par]

                    # self.all_args[par] = alg_args[par]#when fit is called again&again kw_args[par]>1 would force to else block

            if 'samples_per_season' not in alg_args:
                if self._totalsamples is not None:
                    alg_args['samples_per_season'] = int(self._totalsamples * 0.25)
                else:
                    alg_args['samples_per_season'] = 2
                self.all_args['samples_per_season'] = alg_args['samples_per_season']

            if 'initial_training_seasons' not in alg_args:
                if self._totalsamples is not None and alg_args['samples_per_season'] is not None:
                    alg_args['initial_training_seasons'] = int(self._totalsamples / int(alg_args['samples_per_season']))
                else:
                    alg_args[
                        'initial_training_seasons'] = 2  # int(self._totalsamples/int(alg_args['samples_per_season']))#2
                self.all_args['initial_training_seasons'] = alg_args['initial_training_seasons']

            # samples_per_season, initial_training_seasons, algorithm_type="additive", compute_seasonality=None,
            # error_history_length=1, use_full_error_history=True

            if 'algorithm_type' not in alg_args:  # Default is additive
                alg_args['algorithm_type'] = 'additive'
            if '_' not in self.algorithm or '_' not in self.model_name:  # Daub gives back the same object if not checked it will keep appending
                # self.algorithm = self.algorithm + '_' + alg_args['algorithm_type']  # can't do this
                self.model_name = self.algorithm + '_' + alg_args['algorithm_type']  # avoid duplicate concat

            self.model_id = WatForeForecaster.get_model_id(algorithm,**alg_args)
            self.model_description = self.algorithm + '_' + str(alg_args)
            #print('Non Automatic Mode==',alg_args)
            #print('MODEL ID', self.model_id)
            return tspy.forecasters.hws(**alg_args)  #

        if 'arima' == algorithm.lower():  #

            alg_args = {}
            # error_horizon_length=1, use_full_error_history=True, force_model=False, min_training_data=-1, p_min=0,
            # p_max=-1, d=-1, q_min=0, q_max=-1

            #################################SET DEFAULTS################
            if 'min_training_data' not in kw_args.keys():
                kw_args[
                    'min_training_data'] = 0.999999  # self._totalsamples-->not good for multiple calls to fit) # Use all of samples for training
            ################################################################
            # optional params
            alg_params = ['error_horizon_length', 'use_full_error_history', 'force_model', 'min_training_data'
                , 'p_min', 'p_max', 'd', 'q_min', 'q_max']

            for par in alg_params:
                if par in kw_args and kw_args[par] is not None:
                    if par == 'error_horizon_length' or par == 'min_training_data':
                        if kw_args[par] < 1 and self._totalsamples is not None:
                            #alg_args[par] = int(kw_args[par] * self._totalsamples)  # parameters from range
                            alg_args[par] = int(round(kw_args[par] * self._totalsamples, 14)) # to convert 7.99999.. to 8
                            if alg_args[par] <= 0:
                                if par == 'min_training_data':
                                    alg_args[par] = -1 # -1 is allowed for Arima
                                else:
                                    alg_args[par] = 2
                            # self.all_args[par] = alg_args[par]#when fit is called again&again kw_args[par]>1 would force to else block
                            # print('error history length ',self.all_args[par])
                        else:
                            alg_args[par] = kw_args[par]
                    else:
                        alg_args[par] = kw_args[par]
            # print('ARIMA ARGS',alg_args)
            self.model_id = WatForeForecaster.get_model_id(algorithm,**alg_args)
            self.model_description = self.algorithm + '_' + str(alg_args)
            return tspy.forecasters.arima(**alg_args)  #

        if 'arma' == algorithm.lower():  #

            alg_args = {}
            # error_horizon_length=1, use_full_error_history=True, force_model=False, min_training_data=-1, p_min=0,
            # p_max=-1, d=-1, q_min=0, q_max=-1
            if 'min_training_data' not in kw_args.keys():
                kw_args[
                    'min_training_data'] = 0.999999  # self._totalsamples-->not good for multiple calls to fit) # Use all of samples for training
            # optional params
            alg_params = ['min_training_data', 'p_min', 'p_max', 'q_min', 'q_max']

            for par in alg_params:
                if par in kw_args and kw_args[par] is not None:
                    if par == 'min_training_data':
                        if kw_args[par] < 1 and self._totalsamples is not None:
                            #alg_args[par] = int(kw_args[par] * self._totalsamples)  # parameters from range
                            alg_args[par] = int(round(kw_args[par] * self._totalsamples, 14))
                            if alg_args[par] <= 0:
                                if par == 'min_training_data':
                                    alg_args[par] = -1  # -1 is allowed for Arma
                                else:
                                    alg_args[par] = 2
                            # self.all_args[par] = alg_args[par]#when fit is called again&again kw_args[par]>1 would force to else block
                            # print('error history length ',self.all_args[par])
                        else:
                            alg_args[par] = kw_args[par]
                    else:
                        alg_args[par] = kw_args[par]
            # print('ARMA ARGS',alg_args)
            self.model_id = WatForeForecaster.get_model_id(algorithm,**alg_args)
            self.model_description = self.algorithm + '_' + str(alg_args)
            return tspy.forecasters.arma(**alg_args)  #

        if 'bats' == algorithm.lower():

            alg_args = {}
            # training_sample_size, box_cox_transform = False)
            if 'training_sample_size' not in kw_args.keys():
                kw_args[
                    'training_sample_size'] = 0.999999  # self._totalsamples-->not good for multiple calls to fit)  # 0.999999  # Use all of samples for training

            # optional params
            alg_params = ['training_sample_size', 'box_cox_transform']

            for par in alg_params:
                if par in kw_args and kw_args[par] is not None:
                    if par == 'training_sample_size':
                        if kw_args[par] < 1 and self._totalsamples is not None:
                            #alg_args[par] = int(kw_args[par] * self._totalsamples)
                            alg_args[par] = int(round(kw_args[par] * self._totalsamples, 14))
                            # self.all_args[par] = alg_args[par]#when fit is called again&again kw_args[par]>1 would force to else block
                            # print(alg_args)
                        else:
                            alg_args[par] = kw_args[par]
                    else:
                        alg_args[par] = kw_args[par]

            if 'training_sample_size' not in alg_args.keys():
                if self._totalsamples is not None:
                    alg_args['training_sample_size'] = self._totalsamples
                else:
                    alg_args['training_sample_size'] = 8  # minimum 8 samples are required otherwise it throws error
            self.model_id = WatForeForecaster.get_model_id(algorithm,**alg_args)
            self.model_description = self.algorithm + '_' + str(alg_args)
            #print('ALG Args',alg_args)
            return tspy.forecasters.bats(**alg_args)  #

        if 'autoforecaster' == algorithm.lower():

            alg_args = {}
            # training_sample_size, box_cox_transform = False)
            #defaults
            if 'training_sample_size' not in kw_args.keys():
                kw_args[
                    'training_sample_size'] = 0.999999  # self._totalsamples-->not good for multiple calls to fit)  # 0.999999  # Use all of samples for training
            if 'min_training_data' not in kw_args.keys():
                kw_args[
                    'min_training_data'] = 0.999999  # self._totalsamples-->not good for multiple calls to fit) # Use all of samples for training
            # optional params
            alg_params = ['min_training_data', 'error_history_length']

            for par in alg_params:
                if par in kw_args and kw_args[par] is not None:
                    if par == 'error_history_length' or par == 'min_training_data':
                        if kw_args[par] < 1 and self._totalsamples is not None:
                            #alg_args[par] = int(kw_args[par] * self._totalsamples)  # parameters from range
                            alg_args[par] = int(round(kw_args[par] * self._totalsamples, 14))
                            if alg_args[par] <= 0:
                                alg_args[par] = 2
                            # self.all_args[par] = alg_args[par] #when fit is called again&again kw_args[par]>1 would force to else block
                        else:
                            alg_args[par] = kw_args[par]
                    else:
                        alg_args[par] = kw_args[par]

            if 'min_training_data' not in alg_args:
                alg_args['min_training_data'] = 8  # minimum 8 samples are required otherwise it throws error
                self.all_args['min_training_data'] = alg_args['min_training_data']
            else:
                if alg_args['min_training_data'] < 8:
                    alg_args['min_training_data'] = 8  # minimum 8 samples are required otherwise it throws error
                    # self.all_args['min_training_data'] = alg_args['min_training_data']
            # print(alg_args)
            self.model_id = WatForeForecaster.get_model_id(algorithm,**alg_args)
            self.model_description = self.algorithm + '_' + str(alg_args)
            return tspy.forecasters.auto(**alg_args)  #

        # Algorithm name not found.
        raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0004E')) # utils needs to be moved to ts_libs


    # convert algorithm params to ints here if they are float...
 #  def fit(self, X, y):
#
#        return self

    def fit(self, X, y=None, _reset_model=False):
        """A reference implementation of a fitting function.
        Parameters
        ----------
        X : {array-like, matrix}, shape (n_samples, n_timeseries)
            If the timestamp is supplied it has to be in timstamp format i.e., int or long value of date&time.
            Example, [[0, 10.0, 34], [1, 20.0, 84], [2, 30.0, 98], [3, 40.0, 89]], for two features or if col-0 is
            timestamp then ts_icol_loc should be set to [0].
        y : array-like, shape (n_samples,) or (n_samples, n_outputs)
            The target values for the respective timestamp. The format for this is similar to X except, if
            only one time series is specified then y can be 1D array like [10.0, 20.0, 30.0, 40.0], the
            n_features should be equal to n_outputs.
        Returns
        -------
        self : object
            Returns self.
        """

        ##############################SETUP##################
        # print('Fit Called')
        # Check the context
        # if None == self.wfts_context:

        # try:
        #     self.wfts_context = TSContext(die_on_exit=False)#TSContext()
        # except:
        #     print('Error creating context.')
        #     raise
        # self.wfts_context = tspy
        #print('REST MODEL===========', _reset_model, len(self.model))

        #Fit backward compatibility with loaded models # Dec12021--SYS
        if not hasattr(self, 'is_exogenous_pipeline_'):
            self.is_exogenous_pipeline_ = False
        if not hasattr(self, 'feature_column_indices'):
            self.feature_column_indices = []

        if not hasattr(self, 'difference_all_data'):
            self.difference_all_data = False
        if not hasattr(self, 'diff_eta'):
            self.diff_eta = True
        if not hasattr(self, 'disable_difference'):
            self.disable_difference = False

        if not hasattr(self, 'n_targets_'):
            if -1 != self.target_column_indices:
                self.n_targets_ = len(self.target_column_indices)
            else:  # case where target_Col index  == -1
                self.n_targets_ = len(X[0])  #            #self.feature_column_indices
            self.n_features_ = -1
            self.exog_column_indices = [] #older models with no exogenous support
            self.last_exogenous_values = [] #older models with no exogenous support
            self.feature_column_indices = [] #older models with no exogenous support

        ###################### Dec12021--SYS

        # Should that be fiting existing models or create new one
        if self.model is None or self.model == []:
            self.model = [] 
        elif _reset_model: # will not update existing model
            if len(self.model) != 0:
                for m in self.model:
                    m.reset_model()  # just in case previous java models are holding up memory
            self.model = []  # self._getModel(algorithm=self.algorithm, kw_args=self.all_args)
        else:
            # using predict to update the existing model to avoid re-coding as it is doing same thing i.e. update model without re-initializing coefficients
            self.predict(X)
            self.model = self.model_update_predict # copy over updated models
            #print('Model Length', len(self.model), self.get_last_updated())
            return self
        #####################################################

        # print(self.ts_icol_loc)
        # print(self.all_args)
        #print (y)
        #self.debug = True
        if self.debug:
            print(str(self.__class__) + ' fit \n X==' + str(X))
            print('Y=' + str(y))

        #print("Features ====>", self.feature_column_indices,self.algorithm)
        #print("Target ====>", self.target_column_indices, self.algorithm)
        #print("Ex ====>", self.exog_column_indices, self.algorithm)
        '''
        Below check will enforce X&y be of same size, which might be problem as some transforms change size of X.
        For stats models usually that is fine but if Equal size is required you should enable the check other wise use
        X = np.vstack(X) as below
        '''
        # Removed this check, only X becaus y might contain math.nan during piplining as the transformer will only
        # update missing value for X and y stays original which is replace below but this check happens before....
        # X, y = check_X_y(X, y, accept_sparse=True)
        X = check_array(X, accept_sparse=True, force_all_finite=False)
        # This conversion is to convert list of arrays to ndarray if above check is used remove below vstack()
        # X = np.vstack(X)
        # map(list, X)
        # print ()

        # print(type(X))
        # print (y)
        # print (X[:, 1:]) #vals
        # print (X)
        '''
        In sklearn pipeline if the forecaster is used with interpolator then forecaster gets X from interpolator
        and it contains interpolated values not the y so the y should be replaced with what is in X. This is also
        because stats models train on the same time series and don't have separate target. Therefore we interpolate
        the time series and then train forecasting model on that.
        '''
        # print (X.shape)

        # print('fit',X)
        # print('fit',y)
        # print(self.ts_icol_loc)
        #check if this is redundant: might be needed in cases where fit is called directly without init
        self.n_features_ = -1 # set to -1 by default
        if -1 != self.feature_column_indices and -1 != self.target_column_indices:
            self.exog_column_indices = list(set(self.feature_column_indices) - set(self.target_column_indices))
            if len(self.exog_column_indices) > 0:
                self.n_features_ = len(self.exog_column_indices)

        self._timestamps = []
        ts_col = -1

        if -1 != self.target_column_indices:
            #self.n_features_ = len(self.target_column_indices) # With exognous this should be num of exog variables
            self.n_targets_ = len(self.target_column_indices)
        else:#case where target_Col index  == -1
            #self.n_features_ = X.shape[1]  # With exognous this should be num of exog variables
            self.n_targets_ = X.shape[1]# No ts col and all cols are features
            # self.target_column_indices == -1 overrides features, no feature is left if self.target_column_indices == -1
            # if -1 != self.n_features_:
            #     self.n_targets_ = self.n_targets_ - self.n_features_
            if -1 != self.ts_icol_loc:  # User provides TS column in data so subtract one from features
                #self.n_features_ = self.n_features_ - 1   # With exognous this should be num of exog variables
                self.n_targets_ = self.n_targets_ - 1 #TODO: Fix this to subtract number of exogenous/self.n_features_

        if self.ts_icol_loc == -1 or len(self.ts_icol_loc) == 0:
            # autogenerate ts
            len_ts = X.shape[0]
            for t in range(0, len_ts):
                self._timestamps.append(int(t))
        else:
            # print(self.ts_icol_loc[0])
            ts_col = self.ts_icol_loc[0]  # Assuming for now only one timestamp
            if ts_col < 0 or ts_col >= X.shape[1]:
                # self.stop_context()
                raise RuntimeError(Messages.get_message(str(ts_col), message_id='AUTOAITSLIBS0005E'))

            # print(X[:,ts_col])
            ts = X[:, ts_col]  # X[:, :ts_col+1].flatten()
            # print (ts)
            for t in ts:
                self._timestamps.append(int(t))
            # [X.flatten().tolist()]

        vals_df_array = []
        exogenous_matrix = [] # features/exogenous variables
        self._totalsamples = len(self._timestamps)
        # print (self.all_args)
        # print(self._totalsamples)

        #################################SET DEFAULTS################
        # moved to _getModel
        #        if 'min_training_data' not in self.all_args.keys():
        #            self.all_args['min_training_data'] = 0.999999#self._totalsamples-->not good for multiple calls to fit) # Use all of samples for training
        #        if 'training_sample_size' not in self.all_args.keys():
        #            self.all_args['training_sample_size'] = 0.999999#self._totalsamples-->not good for multiple calls to fit)  # 0.999999  # Use all of samples for training

        #############################################################
        # np.savetxt("/tmp/arima_error.csv", X, delimiter=",")
        self.last_exogenous_values = None
        if self.exog_column_indices !=-1 and len(self.exog_column_indices ) != 0:
            #exogenous_matrix = self._get_exogenous_matrix(X, self.exog_column_indices, ts_col)
            #self.last_exogenous_values = exogenous_matrix[-1]
            if len(self.feature_column_indices) > 0:  # XH: as it can be an empty list [] (see above as well)
                exogenous_matrix = self._get_exogenous_matrix(X, self.exog_column_indices, ts_col)
                self.last_exogenous_values = exogenous_matrix[-1]

        #print('Ex matrix wiht False',exogenous_matrix)
        #print('X Ex matrix wiht False',  X)
        # print('Last exognous values=',self.last_exogenous_values)
        for val_ind in range(0, X.shape[1]):
            if (val_ind != ts_col and -1 == self.target_column_indices) or (-1 != self.target_column_indices and
                                                                            #                                                                            val_ind != ts_col and # for now assume user provides different indices
                                                                            val_ind in self.target_column_indices):
                vals_df_array.append(X[:, val_ind])
                ts_l = len(self._timestamps)
                #######GET SEASONAL Length############
                # print(self.algorithm)
                if self.compute_periodicity:
                    # For multiple models compute periodicity on each ts and initialize model with that
                    # However, when printing the watfore_forecaster object self.all_args['min_training_data']
                    # will show last calculated seasonal length, array of values for ['min_training_data'] can be considered
                    # but that would require changes in multiple places and would be restricting as we don't know number
                    # of ts in advance to define param ranges and sepecify default values.

                    # print(X[:,val_ind])
                    # print(vals_df_array[-1])

                    min_train = self.all_args.get('min_training_data', None)  # if none go to non-auto mode
                    # by pass fft analysis if min_train is there meaning automode
                    # if (wf.Forecasters.hw == self.algorithm.lower() and min_train is None) or \
                    #        'autoforecaster' == self.algorithm.lower() or 'bats' == self.algorithm.lower():
                    # by pass fft for hw
                    if 'autoforecaster' == self.algorithm.lower() or 'bats' == self.algorithm.lower():
                        # use recently appended ts for seasonality
                        ul = 200  # Max on samples to init
                        ll = 8  # min samples for init, value comes from BATS as it requires minimum 8 samples

                        hw_samps, ac_per, bats_samps, per_fft = WatForeUtils.get_init_samples(
                            vals_df_array[-1].tolist(),
                            upper_limit=ul,
                            lower_limit=ll)
                        self.all_args['samples_per_season'] = ac_per  # / ts_l #0.5#
                        init_season = int(ts_l / ac_per)  # 2#
                        self.all_args['initial_training_seasons'] = init_season  # fix this to 2 and error goes away
                        # Reset history length according to periodicity in signal
                        # At some point this can be matched with look_back window of other models
                        # print('error histor == ',self.all_args['error_history_length'])
                        # print('error histor == ', self.all_args['error_horizon_length'])
                        # if per == ll / ts_l:  # means get_init_samples returned lower limit then default to 2
                        #    self.all_args['error_history_length'] = 2 / ts_l
                        #    self.all_args['error_horizon_length'] = 2 / ts_l
                        # else:

                    self.all_args['error_history_length'] = 2  # hw_samps/2
                    self.all_args['error_horizon_length'] = 2  # hw_samps/2# since we double the num samples

                    if ('autoforecaster' == self.algorithm.lower() or
                            'bats' == self.algorithm.lower()):
                        # per = WatForeUtils.get_bats_init_samples(vals_df_array[-1].tolist())
                        # print('----------BATS SAMPS',bats_samps)
                        # print('----------HW SAMPS', hw_samps)
                        # print('----------HW SAMPS', ac_per)
                        self.all_args[
                            'min_training_data'] = bats_samps  # Each model gets periodicity computed on its ts
                        self.all_args[
                            'training_sample_size'] = bats_samps  # Each model gets periodicity computed on its ts

                        # print (self.all_args['training_sample_size'])
                # print('after init bats samples========',self.all_args)
                ###########################################################
                try:
                    # self.all_args['min_training_data'] might be different for different ts depending seasonal length
                    self.model.append(self._getModel(**self.all_args))
                except  BaseException as e:
                    logger.warning("Failed to instantiate Model.", e)

                    # er = str(e)
                    # # self.stop_context()
                    # raise Exception(er)

        #yousaf print (len(exogenous_matrix[0]),feature_ind)
        #print (exogenous_matrix) #Reformat the features to matrix
        # print(vals_df_array)
        vals_df_array_log = []
        # NOTE This is going to keep original vals for all in case one ts has negative values
        # log of negative is nan so we don't log transform that

        if self.log_transformed:
            # for cnt in range(0,len(vals_df_array)):
            #     lg_val = np.log1p(1 + vals_df_array[cnt])
            # print((1 +np.array(vals_df_array)))

            lg_val = np.log1p(1 + np.array(vals_df_array))
            # print(np.isnan(lg_val))
            if np.isnan(lg_val).any():
                self.log_transformed = False
                # break
            else:
                vals_df_array = lg_val  # .insert(cnt, lg_val)
                del lg_val
                # print(cnt)
                # print('log transformed')

            #
            # if self.log_transformed:
            #     vals_df_array = vals_df_array_log
            #    #print('transformed')
            #     del vals_df_array_log

        # vals_df_array = np.log1p(1+vals_df_array)
        # print(vals_df_array)
        # pred_models = [] # store models for ts
        # val_col = X.shape[1] - 1

        # y = (X[:, val_col:]).flatten()
        # if
        # timestamps =

        # if y_x != y:
        # raise Warning("Values for X[ts,val] & y[val] in fit(X,y) are not the same, using values from X[ts,val]")
        # y = y_x
        # print(y)
        # print(X[:, :1])  # Ts

        # print(y.shape)
        # print ('shape of x in fit=====', X.shape)

        if self.debug:
            print(str(self.__class__) + ' fit \n X==' + str(X) + '\n y=' + str(y))

        # timestamps and & value convert to DF, include ts location & multiple values to create multiple models.
        #########################################Start BULK UPDATE #############################################################
        #print("================",vals_df_array)
        #self.temp_data = vals_df_array
        #for col in range(0, self.n_features_):
        for col in range(0, self.n_targets_):
            try:
                # print(vals_df_array[col].shape)

                if ('arima' == self.algorithm.lower() or
                    'arma' == self.algorithm.lower()) and ts_l > 50:
                    ###################ARIMA varying init size cases############
                    # arima_min_train_size = ts_l
                    model_initialized = False
                    ###########################################################
                    itr = 0
                    # itr > 4 so after 4 tries and arima_min_train_size = -1 exit out of loop even if model is not init
                    while (not model_initialized) and itr < 5:
                        arima_min_train_size = WatForeUtils.get_arima_init_size(itr, ts_l)
                        itr = itr + 1
                        try:
                            #                            print("ARIMA MIN TRAINING ====== ",arima_min_train_size)
                            self.all_args['min_training_data'] = arima_min_train_size
                            self.model[col] = self._getModel(**self.all_args)
                            # another optimization might be to provide latest data only for initialization
                            # This could be tricky since we cannot provide data out of order and will have
                            # difference in provided data length and last update model time(in case of missing timestamp)
                            self.model[col].update_model(self._timestamps, vals_df_array[col].tolist())
                            model_initialized = self.model[col].is_initialized()
                            # print ("MODEL TRAINIGN STATUS=========",model_initialized)
                        except  BaseException as e:
                            # er = str(e)
                            # raise (Exception(er))
                            logger.warning("Failed to train/update Model.", e)

                    ##############################################################
                # IF NOT ARIMA just Train model
                else:
                    # try:
                    if self.algorithm.lower() in EXOGENOUS_MODELS:
                        #print ('Exo algo target',exogenous_matrix,vals_df_array[col].tolist(),)
                        self.model[col].update_model(vals_df_array[col].tolist(),exogenous_matrix)
                        self.is_exogenous_pipeline_ = True
                    else:
                        #special case for HW multiplicative where HWMultiplicative gives large or very small values when trained on all data
                        if (wf.Forecasters.hw == self.algorithm.lower() and
                            'multiplicative' == self.algorithm_type):
                            self.initialize_hw_multiplicative(col,vals_df_array) #disabling for now to let other PRs go
                            #self.model[col].update_model(self._timestamps, vals_df_array[col].tolist())
                        else:
                            self.model[col].update_model(self._timestamps, vals_df_array[col].tolist())

                    # except  BaseException as e:
                    #     logger.warning("Failed to train/update Model.",e)


                # val_list = vals_df_array[col].tolist()
                # try:
                #
                #     for ind in range(0,len(val_list)):
                #         self.model[col].update_model(self._timestamps[ind],val_list[ind])
                # except Exception as e:
                #     print('Exception at updating....',self._timestamps[ind],val_list[ind])
                #     print(e)
                #     exit('FIT EXIT...')
                #
                # print('updated at fit len ',len(vals_df_array[col].tolist()))
                # print('update ts in fit=', self.model[col].last_time_updated)
            except Exception as e:
                #logger.info("Failed to Fit Model." ,e)
                # self.stop_context()  # might need to be enabled for context to stop in standalone mode.
                #logger.warning("Failed to train Model.")
                raise Exception("Failed to Fit Model." + self.model_name)  # For Joint Optimizer to continue
            #########################################END BULK UPDATE #############################################################
            vals_df_array[col] = None  # clear up as model training is done.

        #########################################START SINGLE UPDATE ###########################################################
        # #Check the one full data transfer instead of incremental data transfer.
        # prev_ts = -1 # to check new ts is not older than previous
        # for row in range(0,X.shape[0]):
        #     #print(X[i][0])
        #     #print(y[i])
        #     if prev_ts < self._timestamps[row]:
        #         for col in range(0,self.n_features_):
        #             try:
        #                 #print('Updated Model',int(self._timestamps[row]),float(vals_df_array[col][row]))
        #                 self.model[col].update_model(int(self._timestamps[row]),float(vals_df_array[col][row]))
        #                 #print('after update')
        #             except Exception as e:
        #                 print('Current Timestamp', self._timestamps[row], 'Current Value', vals_df_array[col][row])
        #                 #print (col,row)
        #                 #print(self.all_args)
        #                 #logger.error('Error ',self.all_args)
        #                 logger.exception(e)
        #                 logger.warning(self.all_args)
        #                 self.stop_context() # might need to be enabled for context to stop in standalone mode.
        #                 raise # For Joint Optimizer to continue
        #         prev_ts = self._timestamps[row]
        #     else:
        #             logger.warning('Current timestamp is older than latest previous,skipping timestamp and value')
        #             logger.warning('Current Timestamp', self._timestamps[row], 'Current Value',
        #                   'Previous Timestamp was ', prev_ts)
        #########################################END SINGLE UPDATE #############################################################
        m_fitted_ = True
        # print('After model trained',self.all_args)
        for m in self.model:
            if not m.is_initialized():
                m_fitted_ = False
            #self.model_name = m.getModelName() # not yet available
        if m_fitted_:
            self.set_model_fitted()
        else:
            if hasattr(self, 'is_fitted_'):
                del self.is_fitted_
        # print("********************************Number of features=================="+ str(self.n_features_))
        # print("********************************Number of Targets==================" + str(self.n_targets_))
        # print('Features',self.n_features_)
        # print('Vals array len',len(vals_df_array[0].tolist()))
        # print('num ts = ', len(self._timestamps))
        # print('model_id', self.model_id)

        # Set model for prediction, not needed
        # self.model_update_predict = self.get_models_copy() ---not needed here so commented out
        return self

    # Does prediction for prediction_horizon and X is considered as history all of which is used for updates
    # After updates number of predictions=prediction_horizon is returned and jvm connection is closed.
    # predict_on_history, where X is history and is used to update model
    ## prediction_type: forecast, rowwise, rowwise_2d
    def predict(self, X=None, prediction_horizon=-1, ts_col_loc=-1,prediction_type='forecast',future_exogenous=None):

        """ A reference implementation of a predicting function.
               Parameters
               ----------
               X : {array-like}, shape (n_timeseries,) shape 2-D array
                   X has history of data based on history window and will be used to update model.
                   Example: [[10], [11]], this tells model to update it with values 10,11 and
                   If X = None, the model will not be updated and future predictions are produced based on
                   prediction_history.
               future_exogenous: Future values of exogenous variables. Future values equal to required prediction_horizon
               should be provided. If not enough values are provided model will use whatever last values it had.
               Returns
                predicted values will be in 2-D and values based on prediction_horizon which defaults to 1 in model or
                prediction_horizon specified in predict after last updated timestamp.
                :param prediction_horizon:
                :param ts_col_loc:
        """
        #print('Trained data ', self.algorithm, self.temp_data)
        #print('===================Calling Predict. ts_libs..............',prediction_horizon)
        #if prediction_type is not None:
           # if prediction_type.lower() != 'forecast':
            #    logger.warning(prediction_type," is not supported. Will return result for prediction type forecast")
        # if we/WML don't support prediction_horizon, ts_col_loc in predict we can remove it from function args
        # and initialize them inside this function with -1 to keep functionality for future support

        if not hasattr(self, 'is_exogenous_pipeline_'):
            self.is_exogenous_pipeline_ = False
        if not hasattr(self, 'feature_column_indices'):
            self.feature_column_indices = []

        if not hasattr(self, 'difference_all_data'):
            self.difference_all_data = False
        if not hasattr(self, 'diff_eta'):
            self.diff_eta = True
        if not hasattr(self, 'disable_difference'):
            self.disable_difference = False

        if X is not None:
            X = check_array(X, dtype=np.float64, force_all_finite=False, ensure_2d=False, ensure_min_samples=0)
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        if prediction_type.lower() == Score.PREDICT_SLIDING_WINDOW and prediction_horizon <= 1:
            # if sliding_predict == True and  multistep_predict == False:
            return self.predict_sliding_window(X=X, prediction_horizon=prediction_horizon, ts_col_loc=ts_col_loc,
                                               future_exogenous = future_exogenous)

        elif prediction_type.lower() == Score.PREDICT_SLIDING_WINDOW and prediction_horizon > 1:
            # if sliding_predict == True and  multistep_predict == True:
            return self.predict_multi_step_sliding_window(X=X, prediction_horizon=prediction_horizon,
                                                          ts_col_loc=ts_col_loc,future_exogenous = future_exogenous)
        else:  # prediction_type.lower() == 'forecast' and prediction_horizon <= 1:
            self.model_update_predict = self.get_models_copy()
            preds = self.predict_on_history_single(X=X, prediction_horizon=prediction_horizon, ts_col_loc=ts_col_loc,
                                                   future_exogenous = future_exogenous)
        # This is to ensure each predict call starts from originally trained model
        #self.model_update_predict = self.get_models_copy()#----not needed here so commented out
        return preds

    # Does predicts 1-step ahead (default) and sliding window fashion to update model as well
    # Number of predictions based on size of X and sliding window will be returned.
    # This is for cross validation
    # validation_scoring this param is true only for x-validation as history is not given in cross validation and x_test&
    # y_test are the same size so we will need to add padding of lookback_window to x_test
    # Assumes no history is given for first, updates one value at a time
    def predict_sliding_window(self, X, prediction_horizon=1, ts_col_loc=-1,future_exogenous = None):

        if X is not None:
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        preds = []
        pr_l = []
        X = np.asarray(X)

        if ts_col_loc == -1:
            if self.ts_icol_loc != -1:
                ts_col_loc = self.ts_icol_loc[0]
        #print('Called preict sliding....None')
        # TODO: for horizon > 1 may be do sliding and change horizon for last one keeping 1 for rest of it
        self.model_update_predict = self.get_models_copy()
        #print("X predict_sliding_window()==", X)
        if not self.is_exogenous_pipeline_:
            pr_l = self.predict_on_history_single(None, prediction_horizon=prediction_horizon,
                                                  ts_col_loc=ts_col_loc)
        #print('Called preict sliding....After None', self.is_exogenous_pipeline_)
        for pr in pr_l:
            preds.append(list(pr))
        if X.all is not None and len(X) != 0:
            #print('calling predict singel')
            for count in range(0, X.shape[0]):  #
                # if count == 0:#Do not update value before predicting it
                pr_l = []
                if  count+1 == X.shape[0]:
                    if self.is_exogenous_pipeline_:
                        pr_l = self.predict_on_history_single([X[count]], prediction_horizon=prediction_horizon,
                                                      ts_col_loc=ts_col_loc,ph_offset=count)
                        #print('CountEX ', count)
                else: # Non-exogenous skip last value as they do predict(None) for first value. last value prediction won't exist in ground truth so we stop one before last
                    pr_l = self.predict_on_history_single([X[count]], prediction_horizon=prediction_horizon,
                                                          ts_col_loc=ts_col_loc,ph_offset=count)
                    #print('Count ', count)

                for pr in pr_l:
                    preds.append(list(pr))

        #self.model_update_predict = self.get_models_copy() ---not needed here so commented out

        return np.asarray(preds)

    def predict_multi_step_sliding_window(self, X, prediction_horizon=1, ts_col_loc=-1,future_exogenous = None):
        if X is not None:
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        preds = []
        pr_l = []
        X = np.asarray(X)
        if ts_col_loc == -1:
            if self.ts_icol_loc != -1:
                ts_col_loc = self.ts_icol_loc[0]
        #print('CALING MULTI STEP SLIDing 1')
        # TODO: for horizon > 1 may be do sliding and change horizon for last one keeping 1 for rest of it
        self.model_update_predict = self.get_models_copy()
        if not self.is_exogenous_pipeline_:
            pr_l = self.predict_on_history_single(None, prediction_horizon=prediction_horizon,
                                              ts_col_loc=ts_col_loc, future_exogenous = future_exogenous)
        #print('CALING MULTI STEP SLIDing AFTER NONE')
        for pr in pr_l:
            preds.append(list(pr))
        if X.all is not None and len(X) != 0:
            limit = X.shape[0] - prediction_horizon + 1
            for count in range(0,limit ):  #
                pr_l = []
                # if count == 0:#Do not update value before predicting it
                if  count+1 == limit:
                    if self.is_exogenous_pipeline_:
                        pr_l = self.predict_on_history_single([X[count]], prediction_horizon=prediction_horizon,
                                                      ts_col_loc=ts_col_loc,ph_offset=count)
                else: # Non-exogenous skip last value as they do predict(None) for first value. last value prediction won't exist in ground truth so we stop one before last
                    pr_l = self.predict_on_history_single([X[count]], prediction_horizon=prediction_horizon,
                                                          ts_col_loc=ts_col_loc,ph_offset=count)

                for pr in pr_l:
                    preds.append(list(pr))

        return np.asarray(preds)

    def _get_exogenous_matrix(self, X, feature_column_indices, ts_col, future_exog=False):

        features_matrix = []
        if 0 == len(feature_column_indices):
            return features_matrix

        if (future_exog == False):
            for feature_ind in feature_column_indices:  # allows overlap between feature and target columns
                if (feature_ind != ts_col):
                    features_matrix.append(X[:, feature_ind])
            #print("Inside exo matri x", features_matrix)
        else:
            # Iterate over all the input assuming time series are sorted and all will be used
            for feature_ind in range(0,X.shape[1]):# number of time series
                # we need to see if its possible that ts_col can be passed in future_exogenous
                if (feature_ind < self.n_features_ ):  # sanity check in case user provides more exog at predict time
                    #print('Inside false', feature_ind, self.n_features_)
                    #print(X[feature_ind, :])
                    features_matrix.append(X[:, feature_ind])
            #print('Len is ',features_matrix,X.shape[0] )

        #np.array(features_matrix).reshape(len(feature_column_indices),100)
        #print ('BEFORE---->',type(features_matrix),np.asarray(features_matrix,dtype = float))
        # we might remove convert to float in below statment once the parsing is done in the tspy wrapper
        features_matrix = list(map(list, np.transpose(np.asarray(features_matrix, dtype=float))))
        #features_matrix = list(map(list, np.transpose(features_matrix)))#map(list, zip(*features_matrix))
        #print ('===========================>>>>>',features_matrix)

        return features_matrix

    # This predict works on window data assuming X contains history values and predict_h or pre
    def predict_on_history_single(self, X, prediction_horizon=-1, ts_col_loc=-1,future_exogenous=None,
                                  ph_offset=-1):
        """ A reference implementation of a predicting function.
        Parameters
        ----------
        X : {array-like}, shape (n_predictions,) shape 2-D array
            The time stamps for which prediction is needed. Example: [[10], [11]], this tells model to predict values
            for time stamp 10 and 11  (or 10th & 11th value ) for all the time series for which model was trained.
        Returns
        -------
        y : ndarray, shape (n_predictions,n_timeseries)
            Returns an 2-D array of predicted values for timestamps for each feature/time series. For example,
            predicted values from timestamp 10 & 11 for two time series will look like,
            [[10.98, 119.72], [11.98, 129.67]] which represents
            [[predicted_value_time series-1 for timestamp 10,predicted_value_time series-2 for timestamp 10],
            [predicted_value_time series-1 for timestamp 11,predicted_value_time series-2 for timestamp 11]]
            :param prediction_horizon:
            :param ts_col_loc:
        """
        #print("X on single history==",X)
        # if this needs to be true we cannot do sliding window predict or will need to set pred horizon to predict in 1-shot all vals
        skip_update = False
        x_offset = 0  # This is for case where we have values in X so the forecast horizon needs to be offset by this value
        if X is None:
            skip_update = True
        if X is not None and 0 == len(X):
            skip_update = True

        if X is not None and 0 != len(X):
            X = check_array(X, accept_sparse=True)
            if ph_offset == -1:
                x_offset = len(X)
            else:
                x_offset = ph_offset # This is for sliding window case where one value is provided but ph has to increment for exogenous case

        ##############################EXOGENOUS CASE, parse exogenous varaible(s) yousaf############################
        ####################### Dec12021--SYS
        #backward compatibility for loading previously saved models without exogenous support
        if not hasattr(self, 'last_exogenous_values'):
            self.last_exogenous_values = None
            self.exog_column_indices = None
        if not hasattr(self, 'n_targets_'):
            self.n_targets_ = len(self.target_column_indices)
        ###################### Dec12021--SYS

        # TODO: Check&implement assumption if we have h exogenous values for h-steps ahead??????? or just 1 last exogenous!!!
        #TODO: check and implement parsing of X based on assumption where exogenous will be startig is it X[-h]???
        exogenous_features = [self.last_exogenous_values]
        ex_matrix = None


        #print(X)
        #if self.model_name in EXOGENOUS_MODELS: # ARIMAX model family in java does not support incremental updat for now
        if self.is_exogenous_pipeline_:
            skip_update = True
            ts_c = ts_col_loc if ts_col_loc != -1 else self.ts_icol_loc
            ph = prediction_horizon if prediction_horizon > 0 else self.prediction_horizon

            # if X is not None and 0 != len(X):
            #     X = check_array(X, accept_sparse=True)
            if future_exogenous is not None and 0 != len(future_exogenous):
                #print("Future Exoge",future_exogenous)
                #print("Previous Exogenous ",exogenous_features)
                #future_exogenous = check_array(future_exogenous, accept_sparse=True)

                #Enable this imputation if common one doesn't work
                # future_exogenous = imputer_helper.impute_multi_array(X=np.asarray(future_exogenous), default_values= exogenous_features[-1],
                #                                                      impute_column_indices=self.exog_column_indices)

                future_exogenous = check_array(future_exogenous, accept_sparse=True)
                #print('Future Imputed Exogenous == ',future_exogenous)
                ex_matrix = self._get_exogenous_matrix(future_exogenous, self.exog_column_indices, ts_c,
                                                       future_exog= True) #future_exogenous
                #print(ex_matrix)
                #print('preditct time---',self.exog_column_indices,future_exogenous,ts_c)

            if ex_matrix is not None and 0 < len(ex_matrix): #exogenous coming from future_exogenous
                exogenous_features = ex_matrix[0:ph]
            #print("EXOGENOUS FEATURES==BEFORE==", ex_matrix)

            # parse X and update exogenous_features accordingly if ex_matrix is None meaning X has exogenous values
            # We will treat values in X as future exogenous as future_exogenous is not provided and ARIMAX is not updatable

            if ex_matrix is None and X is not None and len(X) > 0:
                ex_matrix = self._get_exogenous_matrix(X, self.exog_column_indices, ts_c)
                #print('Here1', ex_matrix)

            if ex_matrix is not None and 0 < len(ex_matrix):
                if len(ex_matrix) >= ph:
                    #pick up last ph values in array
                    exogenous_features = ex_matrix[-ph:]#TODO : check this is it possible ph > len(ex_matrix)
                    #print('Here2',exogenous_features)
                else:
                    exogenous_features = ex_matrix[:]
                    #print('Here3')

            #print("EXOGENOUS FEATURES====", exogenous_features,ex_matrix," ph", ph, X)
            #sys.exit(0)
            # self.last_exogenous_values = exogenous_matrix[-1]

        #print("EXOGENOUS FEATURES====",exogenous_features)
        #print('Exog index=',self.exog_column_indices)
        # print('Inside Exogenous', exogenous_features)
        # sys.exit(0)
        ########################################################################
        # print(X.shape)
        # print('predict called', X)
        if self.debug:
            print(str(self.__class__) + ' predict \n X==' + str(X))
        # print(self.is_fitted_)
        try:

            check_is_fitted(self, 'is_fitted_', msg=Messages.get_message(message_id='AUTOAITSLIBS0056E'))
        except BaseException as e:
            # not Needed with new tspy Jan 2020
            # self.stop_context()
            raise (Exception(str(e)))
            #logger.warning(str(self)+':::'+str(e))
            #sys.exit()

        # print (X.shape[0])
        # print(self.n_features_)
        pred_timestamps = []
        ts_col = -1

        if skip_update:  # No updates to model will be done only predictions will be generated based on horizon
            # get forecasts
            forecasts = []

            prev_ts = self.get_last_updated()
            if prediction_horizon == -1:  # from predict signature
                h = self.prediction_horizon
            else:
                h = prediction_horizon
            try:
                #TODO: We need to maintain memory of exogenous == prediction horizon this way we have atleast as many
                #exogenous as prediction horizon else we will get almost same value for all ph>1
                for i in range(0, h):
                    per_model = []
                    f_ahead = i + 1 + x_offset
                    #print("h==",h,"i ",i,"X offset=",x_offset,' fahead',f_ahead)
                    # if prev_ts < i:

                    for m in self.model:
                        if self.model_name in EXOGENOUS_MODELS:
                            if (i < len(exogenous_features)):
                                fr_val = m.forecast_ahead(f_ahead,exogenous_features[i])
                                #print("case1: Exogenous value = ", exogenous_features[i], "fahead=", f_ahead)
                                #print(f_ahead, 'Returning forecasts==',self.model_name, fr_val)
                                #print("last updated", self.get_last_updated())
                                #print("Exogenous value = ", exogenous_features[i])
                            else:
                                # repeat last value if not enough exogenous are provided for given h
                                #print(f_ahead, 'Returning forecasts Case2==', self.model_name, fr_val)
                                fr_val = m.forecast_ahead(f_ahead, exogenous_features[-1])
                                #print("case2: Exogenous value = ",exogenous_features[-1],"fahead=",f_ahead )

                        else:
                            prev_ts = prev_ts + self.get_train_interval()
                            fr_val = m.forecast_at(prev_ts)
                        #replace nan, inf with 0
                        if fr_val == np.nan or fr_val == np.inf or fr_val == -(np.inf):
                            fr_val = 0
                        per_model.append(fr_val)
                    forecasts.append(per_model)
            except BaseException as e:
                # not Needed with new tspy Jan 2020
                # self.stop_context()
                #raise (Exception(str(e)))
                logger.warning(e)

            if self.log_transformed:
                forecasts = np.expm1(forecasts) - 1


            return np.asarray(forecasts)

        if ts_col_loc == -1 and self.ts_icol_loc == -1 or len(self.ts_icol_loc) == 0:
            # autogenerate ts
            if -1 != self.target_column_indices:
                pred_cols = len(self.target_column_indices)#X.shape[1] sys (SEP302021)
            else:
                pred_cols = X.shape[1]
            #if self.model_update_predict is None:
            #  last_update = self.get_train_size() #
            #print('Train status', self.get_train_size() )
            #print('Train status',self.get_last_updated())
            #print('Predict status', self.get_last_updated(self.model_update_predict))
            #else:#CHECK THIS
            last_update = self.get_last_updated(self.model_update_predict) + 1 # since training starts at 0

            len_ts= X.shape[0] + last_update # This won't work with real timestamps we will need to increment real ts accordingly
                                             #, if model was trained with real timestamps
            for t in range(last_update,len_ts):
                pred_timestamps.append(int(t)) # For real ts strart from previous ts and increment it
        else:
            if -1 != self.target_column_indices:
                pred_cols = len(self.target_column_indices) #X.shape[1] - 1 sys (SEP302021)
            else:
                pred_cols = X.shape[1] - 1

            if ts_col_loc == -1:
                ts_col = self.ts_icol_loc
            else:
                ts_col = ts_col_loc

            if isinstance(ts_col, list):
                ts_col = ts_col[0]  # Assuming for now only one timestamp
            else:
                ts_col = ts_col

            if ts_col < 0 or ts_col >= X.shape[1]:
                # not Needed with new tspy Jan 2020
                # self.stop_context()
                raise RuntimeError(Messages.get_message(str(ts_col), message_id='AUTOAITSLIBS0005E'))
            #if pred_cols < self.n_features_:
            if pred_cols < self.n_targets_:
                raise RuntimeError(Messages.get_message(str(pred_cols), str(self.n_targets_), message_id='AUTOAITSLIBS0006E'))
            # print(X[:,ts_col])
            pred_timestamps = X[:, ts_col]  # X[:, :ts_col+1].flatten()
        # print(pred_timestamps)
        ########################################UPDATE MODEL ON History Data#############################################
        # TODO: This needs to be updated if X contains strings/timestamp not specified by ts_col
        vals_df_array = []
        # for val_ind in range(0, X.shape[1]):
        #     if val_ind != ts_col:
        #         vals_df_array.append(X[:, val_ind])
        for val_ind in range(0, X.shape[1]):
            if (val_ind != ts_col and -1 == self.target_column_indices) or (-1 != self.target_column_indices and
                                                                            val_ind in self.target_column_indices):
                vals_df_array.append(X[:, val_ind])

        vals_df_array_log = []
        # NOTE This is going to keep original vals for all in case one ts has negative values
        # log of negative is nan so we don't log transform that
        if self.log_transformed:
            # for cnt in range(0,len(vals_df_array)):
            #     lg_val = np.log1p(1 + vals_df_array[cnt])
            lg_val = np.log1p(1 + np.array(vals_df_array))
            # print(np.isnan(lg_val))
            if np.isnan(lg_val).any():
                # print(np.isnan(lg_val))
                raise Warning(Messages.get_message(message_id='AUTOAITSLIBS0007E'))
                # self.log_transformed = False
                # break
            else:
                vals_df_array = lg_val  # .insert(cnt, lg_val)
                del lg_val

        if self.debug:
            print(str(self.__class__) + ' fit \n X==' + str(X))

        # timestamps and & value convert to DF, include ts location & multiple values to create multiple models.
        ###################################################################################################################
        # Bulk update will skip all points if one value is from previous time stamp so better not use it here
        # for col in range(0, self.n_features_):
        #     try:
        #         # print('Updated Model',int(pred_timestamps[row]),float(vals_df_array[col][row]))
        #         self.model[col].update_model(pred_timestamps, vals_df_array[col].tolist())
        #     except Exception as e:
        #         print('Skipping Update model, possible nan value or older time stamp' )
        #         #print('nan value detected in input to predict')

        ###################################################################################################################
        prev_ts = self.get_last_updated(self.model_update_predict)  # self.get_train_size()-1  #
        #print('Trained model last ts ',self.get_last_updated(self.model_update_predict))
        #print('Predict model last ts ', self.get_last_updated())
        for row in range(0, X.shape[0]):
            if prev_ts < pred_timestamps[row]:
                #for col in range(0, self.n_features_):
                for col in range(0, self.n_targets_):
                    try:
                        #print('Updated Model',int(pred_timestamps[row]),float(vals_df_array[col][row]))
                        #Ensures concurrently running WML instances don't get inconsistent state by updating acutal model
                        self.model_update_predict[col].update_model(int(pred_timestamps[row]), float(vals_df_array[col][row]))
                        #self.model[col].update_model(int(pred_timestamps[row]), float(vals_df_array[col][row]))
                    except BaseException as e:
                        print('Skipping Update model, current Timestamp', str(pred_timestamps[row]), 'Current Value ', str(vals_df_array[col][row]))
                        #np.savetxt('/Users/syshah/Documents/Research_Projects/TimeSeriesAutomation-Challenge/WatForeDebugging/error_data_slice/'
                        #        'hw_mul_update.csv', vals_df_array[col], delimiter=',')
                        #print(X.shape[0])
                        #print('Tried to update with latest ts, old ts', int(pred_timestamps[row]),self.get_last_updated())
                        #print(e)
                        #print(self.all_args)
                        #exit(0)
                prev_ts = pred_timestamps[row]#sanity check
            else:#IN this case it is fine may be user gave older window and wants just next value
                print('Skipping Update model, current timestamp is older than previous one.')
                print('Current Timestamp', str(pred_timestamps[row]),
                               'Previous Timestamp was ', str(prev_ts))

        ####################################################################################################################
        # NOW Forecast values based ont prediction_horizon
        forecasts = []

        # assume value forecasted for same time stamp for all the models
        # print (self.model.is_initialized)
        prev_ts = self.get_last_updated(self.model_update_predict)  # self.get_train_size() -1 # once the get_train_size is replaced with lasttime updated remove -1
        if prediction_horizon == -1:  # from predict signature
            h = self.prediction_horizon
        else:
            h = prediction_horizon
        try:

            # print('Prediciton Horizon',h)
            # for i in range(prev_ts+1, prev_ts + h+1):
            for i in range(0, h):
                per_model = []
                # if prev_ts < i:
                prev_ts = prev_ts + self.get_train_interval()
                #for m in self.model:
                for m in self.model_update_predict:
                    fr_val = m.forecast_at(prev_ts)
                    per_model.append(fr_val)
                # else:
                #    print('Current timestamp is older than latest previous,skipping timestamp and value')
                #    print('Current Timestamp', i, 'Previous Timestamp was ', prev_ts)

                forecasts.append(per_model)
            #  model persistance i.e.export should be done & loading load should be added as we lose model after stop
            # Moved to pred_On_window
            # try:
            #     self.stop_context()
            #
            # except:
            #     print('Context already closed')
        except:
            # not Needed with new tspy Jan 2020
            # self.stop_context()
            raise
        ####Inverse log transform
        # print(forecasts)
        if self.log_transformed:
            forecasts = np.expm1(forecasts) - 1
            # for cnt in range(0, len(forecasts)):
            #    forecasts[cnt] = np.expm1(forecasts[cnt]) - 1

        #####
        #model_update_predict should not be reset here to support cases like sliding window,
        # rest to trained model should be done in functions calling this function
        return np.asarray(forecasts)
    @classmethod
    def get_exogenous_modelnames(cls):
        return EXOGENOUS_MODELS
    @classmethod
    def get_model_id(cls, algorithm_name, **params):

        id = 'st_'
        algorithm_type = params.get('algorithm_type', None)
        comput_seasonalty = params.get('compute_seasonality', None)
        box_cox_transform = params.get('box_cox_transform', None)
        use_full_error_history = params.get('use_full_error_history', None)
        force_model = params.get('force_model', None)
        min_training_data = params.get('min_training_data', None)

        number_of_samples = params.get('number_of_samples', None)
        is_season_length = params.get('is_season_length', None)

        if algorithm_name.lower() == 'hw':
            if algorithm_type.lower() == 'additive' and comput_seasonalty == False and \
                    use_full_error_history == False:
                id = id + '1'
            if algorithm_type.lower() == 'multiplicative' and comput_seasonalty == False and \
                    use_full_error_history == None:
                id = id + '2'
            if algorithm_type.lower() == 'additive' and is_season_length == False and number_of_samples is not None:
                id = id + '6'
            if algorithm_type.lower() == 'multiplicative' and is_season_length == False and number_of_samples is not None:
                id = id + '7'

        if algorithm_name.lower() == 'bats' and box_cox_transform == False:
            id = id + '3'
        if algorithm_name.lower() == 'arima' and use_full_error_history == True and \
                force_model == True and min_training_data == -1:
            id = id + '4'
        if algorithm_name.lower() == 'autoforecaster':
            id = id + '5'

        return id
    # This one is more sklearn style having values in X whic it will ignore and make index
    ############################Moved from autoai_ts to tslibs###############################################
    def __getstate__(self):
        self.model_dumps = []
        state = self.__dict__.copy()
        for m in self.model:
            state['model_dumps'].append(pickle.dumps(m))
        state['wfts_context'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
         #Backward compatibility
        if not hasattr(self, 'is_exogenous_pipeline_'):
            self.is_exogenous_pipeline_ = False
        if not hasattr(self, 'feature_column_indices'):
            self.feature_column_indices = []
        if not hasattr(self, 'difference_all_data'):
            self.difference_all_data = True
        if not hasattr(self, 'diff_eta'):
            self.diff_eta = True
        if not hasattr(self, 'disable_difference'):
            self.disable_difference = False

        self.model = []
        for m in self.model_dumps:
            self.model.append(pickle.loads(m))

    ############################Moving to tslibs###############################################
    def set_model_fitted(self):
        self.is_fitted_ = True

    @classmethod
    def get_estimators(cls, log_transform=False,target_column_indices=-1, time_column_index =-1
                       ,prediction_horizon =-1,lookback_win=1):
        log_transform = False # For now disable all log transform
        selected_estimators = [
        #commented out pipelines not used for now and only enabled shorted listed pipelines.
                               #WatForeForecaster(algorithm=wf.Forecasters.autoforecaster,
                               #                  log_transform=log_transform,
                               #                  prediction_horizon=prediction_horizon,lookback_win=lookback_win,
                               #                  target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index),

            # selected pipeline MVP1
                               WatForeForecaster(algorithm=wf.Forecasters.hw,algorithm_type='additive',
                                                 min_training_data=0.99,
                                                 log_transform=log_transform,prediction_horizon=prediction_horizon,
                                                 lookback_win=lookback_win,target_column_indices=target_column_indices,
                                                             ts_icol_loc = time_column_index),
                                # selected pipeline MVP1
                               WatForeForecaster(algorithm=wf.Forecasters.hw,algorithm_type='multiplicative',
                                                 min_training_data=0.99,prediction_horizon=prediction_horizon,
                                                 log_transform=log_transform, lookback_win=lookback_win,
                                                 target_column_indices=target_column_indices,
                                                             ts_icol_loc = time_column_index),

                               #WatForeForecaster(algorithm=wf.Forecasters.bats, training_sample_size=0.25,
                               #                   box_cox_transform=False,log_transform=log_transform,
                               #                  prediction_horizon=prediction_horizon,lookback_win=lookback_win,
            #                                                  ts_icol_loc = target_column_index),
                               #WatForeForecaster(algorithm=wf.Forecasters.hw, compute_seasonality=True,
                               #                  use_full_error_history=True, log_transform=log_transform,
                               #                  prediction_horizon=prediction_horizon, lookback_win=lookback_win,
                               #                  target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index),
                               #WatForeForecaster(algorithm=wf.Forecasters.hw,
            #                  compute_seasonality=True, samples_per_season=0.05,
            #                                     prediction_horizon=prediction_horizon,log_transform=log_transform,
            #                                    lookback_win=lookback_win,target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index),


                              # WatForeForecaster(algorithm=wf.Forecasters.hw, algorithm_type='additive',
                              #                   compute_seasonality=True, samples_per_season=0.1,
                              #                   prediction_horizon=prediction_horizon, log_transform=log_transform,
                              #                   lookback_win=lookback_win,target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index),
                               #selected pipeline MVP1
                               WatForeForecaster(algorithm=wf.Forecasters.arima, use_full_error_history=True,
                                                 force_model=False,min_training_data=-1, log_transform=log_transform,
                                                 prediction_horizon=prediction_horizon, lookback_win=lookback_win,
                                                 target_column_indices=target_column_indices,
                                                 ts_icol_loc = time_column_index),
                               WatForeForecaster(algorithm=wf.Forecasters.bats, training_sample_size=0.25,
                                                  box_cox_transform=False, log_transform=log_transform,
                                                  prediction_horizon=prediction_horizon, lookback_win=lookback_win,
                                                  target_column_indices=target_column_indices,
                                                 ts_icol_loc = time_column_index),
                               #WatForeForecaster(algorithm=wf.Forecasters.arima,use_full_error_history=True,
                               #                   force_model=True,log_transform=log_transform,
                               #                  prediction_horizon=prediction_horizon,lookback_win=lookback_win,
                                #                 target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index),
                               #WatForeForecaster(algorithm=wf.Forecasters.arma,
                               #                  prediction_horizon=prediction_horizon,
                               #                  lookback_win=lookback_win,target_column_indices=target_column_indices,
            #                                                  ts_icol_loc = target_column_index)

                               ]

        return selected_estimators

    #ONLY  MAKES COPY OF MODESL IN JVM pickle to string based
    def get_models_copy(self, verbose=False):

        models_copy = []
        strings = []
        if self.model is None or self.model == []:
            print('No model defined')
        else:
            try:
                for m in self.model:
                    strings.append(pickle.dumps(m))
                    #mdl = pickle.loads(pickle.dumps(m))
                    #models_copy.append(mdl)
                #it is import to keep the two loops separate for dummps and loads otherwise context might mix up
                for ms in strings:
                    models_copy.append(pickle.loads(ms))
                return models_copy
            except:
                print('Model Copy failed')
                return None
import numpy as np
import pandas as pd

import autoai_ts_libs.deps.tspy
from autoai_ts_libs.deps.tspy.multi_time_series import multi_time_series
from autoai_ts_libs.deps.tspy.time_series import time_series
from autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.datamodel import tes
from autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.estimators import CausalityEstimator

import autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.l0hawkeslib as l0hawkeslib
import autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.l0hawkesutils as l0hawkesutils



class L0HawkesInputDatatypeAdapter:
    """
    This is a class that provides a namespace for a collection of static methods which given 
    
    1. a representation of timeseries of some type including dataframe, array, 
    tuple of arrays, timestamped event sequence or autoai_ts_libs.deps.tspy timeseries and
    
    2. a specification of the location in the representation containing timestamps and event types
    
    return
    a list of two arrays respectively containg the timestamps and the event types.

    These two arrays are the data arguments expected by LOHawkes routines in the library.
    """
    @staticmethod
    def from_dataframe(data, ts_column, value_column):
        timestamp_list  = data[ts_column]
        event_type_list = data[value_column]
        
        timestamp_list_array  = np.array(timestamp_list).astype(np.dtype(float))
        event_type_list_array = np.array(event_type_list)
        
        return timestamp_list_array, event_type_list_array
    
    
    @staticmethod
    def from_timeseries(data, ts_column, value_column):
        data = data.to_df()
        timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_dataframe(data,
                                                                                                  ts_column='timestamp', 
                                                                                                  value_column='value')
        return timestamp_list_array, event_type_list_array
    
    @staticmethod
    def from_tes(data, ts_column, value_column):
        timestamp_list_array  = np.array(data.get_ts()).astype(np.dtype(float)).squeeze()
        event_type_list_array = np.array(data.get_eid()).squeeze()

        return timestamp_list_array, event_type_list_array
          
    
    @staticmethod
    def from_multitimeseries(data, ts_column, value_column):
        pass
    
    
    @staticmethod
    def from_array(data, ts_column, value_column):
        ts_column_idx    = int(ts_column)
        value_column_idx = int(value_column)
        
        timestamp_list_array  = data[:, ts_column_idx].astype(np.dtype(float))
        event_type_list_array = data[:, value_column_idx]
        return timestamp_list_array, event_type_list_array
    
    
    @staticmethod
    def from_tuple(data, ts_column, value_column):
        ts_column_idx    = int(ts_column)
        value_column_idx = int(value_column)
        
        timestamp_list_array  = np.array(data[ts_column_idx]).astype(np.dtype(float))
        event_type_list_array = np.array(data[value_column_idx])
        return timestamp_list_array, event_type_list_array        

    
    @staticmethod
    def from_data(data, ts_column, value_column):
        
        if isinstance(data, pd.DataFrame):
            timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_dataframe(data, ts_column, value_column)
        
        elif isinstance(data, np.ndarray):
            timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_array(data, ts_column, value_column)
        
        elif isinstance(data, tuple):
            timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_tuple(data, ts_column, value_column)
        
        elif isinstance(data, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries):
            timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_timeseries(data, ts_column, value_column)
            
        elif isinstance(data, autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.datamodel.tes):
            timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_tes(data, ts_column, value_column)
        
        return timestamp_list_array, event_type_list_array

    def show_multivariate_points(data, ts_column, value_column, **kwargs):
        timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_data(data, ts_column, value_column)
        
        return l0hawkesutils.show_multivariate_points(timestamp_list_array,
                                                      event_type_list_array,
                                                      **kwargs)
    


class L0HawkesNh(CausalityEstimator):
    def __init__(self,
                 Nh=None,
                 sparse_level=0.75,
                 decayfunc='power',
                 prior = 'gg', 
                 itr_max=50,
                 err_threshold=1e-4,
                 reporting_interval=10,
                 nu_mu=0.1,
                 nu_beta=0.1,
                 nu_A=0.1,
                 epsilon=0.01,
                 a_mu=1.001,
                 b_mu=0.01 ,
                 a_beta=1.01,
                 b_beta=0.01,
                 eta=2):

        """
        Parameters
        ----------
        timestamps : 1D numpy array
            Array of timestamps. Assumed to have N+1 events, where the 0-th event is the 
            genesis event and treated differently from the others. 
        event_types : 1D numpy array
            Array of event types in the original names of the N+1 events. 
        Nh : int
            The number of event instances kept in the history. Nh <= N must hold. 
            For the first Nh instances, the history is shorter than Nh.
        sparse_level : double
            Level of sparsity for the impact matrix. Must be in [0.5,1).
            Corresponds to the probability of getting zero in Bernoulli distribution.
            The default is 0.75.
        decayfunc : string
            Specifies the name of the decay function. Either power or exponential. 
            Only the first three letters (pow, exp) matters. Case insensitive.
        prior : string
            Specifies the prior distribution (or regularization). Currently, gauss
            (Gaussian or L2 regularization), gamma (Gamma distribution), 
            or gg (L2+gamma) is allowed. 
        itr_max : double, optional
            The maximum number of MM iterations. The default is 50.
        err_threshold : double, optional
            Threshold for the residual from the previous round. Used to check 
            convergence. The default is 1e-4.
        reporting_interval : int, optional
            How often you want to get residual feedback. The default is every 10 
            iterations. 
        nu_mu : double, optional
            L2 regularization strength for mu. Will be ignored when prior=gamma. 
            The default is 0.1.
        nu_beta : double, optional
            L2 regularization strength for beta. Will be ignored when prior=gamma. 
            The default is 0.1.
        nu_A : double, optional
            L2 regularization strength for A. Will not be affected by "prior". The 
            default is 0.1.
        epsilon : double, optional
            Threshold parameter for the epsilon-sparsity theory. The default is 0.01.
        a_mu : double, optional
            The shape parameter of the Gamma prior for mu. Must be greater than 1.
            The default is 1.001.
        b_mu : double, optional
            The rate parameter of the Gamma prior for mu. Must be positive. The 
            default is 0.01.
        a_beta : double, optional
            The shape parameter of the Gamma prior for beta. Must be greater than 1.
            The default is 1.01.
        b_beta : double, optional
            The rate parameter of the Gamma prior for beta. Must be positive. The 
            default is 0.01.
        eta : double, optional
            Exponent of the power decay. Ignored if decayfunc is not power. 
            The default is 2.
       
        Attributes
        ----------
        result : dictionary{'event_list','learned_params','regularizer_params','training_data'}      
            event_list : 1D numpy array
                Mapping from event type index to the original event type name
            learned_params : dictionary
                mu : 1D numpy array
                    Baseline intensities
                beta : 1D numpy array
                    Decay parameters
                A : 2D numpy array
                    Impact matrix as the final solution. Use this (not A_epsilon)
                    for practical purposes. This is computed by post-processing 
                    A_epsilon.
                A_epsilon : 2D numpy array
                    Raw impact matrix before postprocess. This is only for 
                    mathematical investigations. Use A instead for applications.
                l0norm : double
                    L0 norm of A
                qself : 1D numpy array
                    Self-triggering probabilities
                qhist : 1D numpy array
                    Triggering probabilities. n-th row is for n-th event instance
                l0l2sol : dictionary
                    Object returned from L0L2sqlog_plus_linear
                loglik : list
                    log likelihood values
            regularizer_params : dictionary
                decayfunc : string
                    decayfunc
                prior : string
                    prior
                nu_A : double 
                    nu_A
                sparse_level : double 
                    sparse_level
                tau : double 
                    tau = ln(sparse_level/(1-sparse_level))
                epsilon : double 
                    epsilon
                nu_mu : double
                    nu_mu
                nu_beta : double
                    nu_beta
                a_mu : double
                    a_mu
                b_mu : double
                    b_mu
                a_beta : double
                    a_beta
                b_beta : double
                    b_beta
            training_data : dictionary
                timestamps : 1D numpy array
                    timestamps
                event_types : 1D numpy array
                    event types as original names
                event_types_idx : 1D numpy array
                    event types as indices
        """


        super(L0HawkesNh, self).__init__()
        self.Nh                 = Nh   
        self.sparse_level       = sparse_level                        
        self.decayfunc          = decayfunc          
        self.prior              = prior              
        self.itr_max            = itr_max            
        self.err_threshold      = err_threshold      
        self.reporting_interval = reporting_interval 
        self.nu_mu              = nu_mu              
        self.nu_beta            = nu_beta            
        self.nu_A               = nu_A                     
        self.epsilon            = epsilon            
        self.a_mu               = a_mu               
        self.b_mu               = b_mu               
        self.a_beta             = a_beta             
        self.b_beta             = b_beta             
        self.eta                = eta                
        
        
        self.valid_keys = ['Nh',
                           'sparse_level',                        
                           'decayfunc',          
                           'prior',              
                           'itr_max',            
                           'err_threshold',      
                           'reporting_interval', 
                           'nu_mu',              
                           'nu_beta',            
                           'nu_A',               
                           'epsilon',            
                           'a_mu',               
                           'b_mu',               
                           'a_beta',             
                           'b_beta',             
                           'eta']                

        
        self.variable_names        = None
        self.weighted_causal_array = None
        self.result                = None 
    
    
    def fit(self, 
            data, 
            ts_column='timestamp', 
            value_column='value',
            scaling_factor=1.0):
        """
        Computes causal relations between timeseries using data in either

        1. Pandas dataframe
        2. Numpy array
        3. Tuple of numpy arrays
        4. Timestamped Event Sequence (`autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.datamodel.tes`)
        5. Time Series (`autoai_ts_libs.deps.tspy.time_series.time_series`)

        Parameters
        ----------
        data:
            type `pandas.DataFrame` or `numpy.ndarray` or `tuple` of` numpy.ndarray` or `tes` or `time_series` 

            * :class:`~pandas.DataFrame`
            * :class:`~numpy.ndarray`
            * `tuple` of two `numpy.ndarray`
            * :class:`~autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.datamodel.tes`
            * :class:`~`autoai_ts_libs.deps.tspy.time_series.time_series`

        ts_column : string
            name of the column  containing timestamps;
            it can be "0" or "1" for `numpy.ndarray` or `tuple` of` numpy.ndarray`
        value_column: string
            name of the column containing event types;
            it can be "0" or "1" for `numpy.ndarray` or `tuple` of` numpy.ndarray`
        scaling_factor: float
            the factor to divide the timestamps;
            it might be the case that integer timestamps in a `time_series` data might have
            resulted from multiplying floating point time values in the original timeseries, by a scaling_factor.
            In that case we need to convert to these original floating point time values by division by that factor.
            The default is 1.0, i.e. no conversion.
            
        Returns
        -------
        self : object
            Fitted L0Hawkes estimator.
        """        

        algorithm = l0hawkeslib.L0HawkesNh
        
        timestamp_list_array, event_type_list_array = L0HawkesInputDatatypeAdapter.from_data(data, ts_column, value_column)
        timestamp_list_array = timestamp_list_array / scaling_factor

        if self.Nh is None:
            effective_Nh = len(timestamp_list_array) - 1 
        else:
            effective_Nh = self.Nh
        self.effective_Nh = effective_Nh    
        
        
        result = algorithm(timestamp_list_array,
                           event_type_list_array,
                           effective_Nh,
                           sparse_level       = self.sparse_level,
                           decayfunc          = self.decayfunc,
                           prior              = self.prior,
                           itr_max            = self.itr_max,
                           err_threshold      = self.err_threshold,
                           reporting_interval = self.reporting_interval,
                           nu_mu              = self.nu_mu,
                           nu_beta            = self.nu_beta,
                           nu_A               = self.nu_A,
                           epsilon            = self.epsilon,
                           a_mu               = self.a_mu,
                           b_mu               = self.b_mu,
                           a_beta             = self.a_beta,
                           b_beta             = self.b_beta,
                           eta                = self.eta)

        
        self.result = result
        
        self.variable_names               = [str(item) for item in set(result['training_data']['event_types'])]
        self.weighted_causal_array        = result['learned_params']['A']
        self.raw_weighted_causal_array    = result['learned_params']['A_epsilon']
        return self
        
        
    def _get_single_variable_weighted_causes(self, variable_name, sparse=True):      
        causal_dict = {}
        effect_idx = self.variable_names.index(variable_name)
        if sparse:
            row = self.weighted_causal_array[effect_idx, :]
        else:
            row = self.raw_weighted_causal_array[effect_idx, :]
        for cause_idx, weight in enumerate(row):
            cause = self.variable_names[cause_idx]
            causal_dict[cause] = row[cause_idx]
            
        return {variable_name : causal_dict}
                    
    
    def get_weighted_causes(self, variable_name=None, sparse=True):
        if variable_name is not None:
            causal_dict = self._get_single_variable_weighted_causes(variable_name, sparse)
        else:
            causal_dict = {}
            for effect in self.variable_names:
                causal_dict.update(self._get_single_variable_weighted_causes(effect, sparse))
        return causal_dict


    def get_decay_parameters(self):
        decay_dict = {}
        for variable_name in self.variable_names:
            variable_idx = self.variable_names.index(variable_name)
            decay_dict[variable_name] = self.result['learned_params']['beta'][variable_idx]
        return decay_dict

    
    def get_base_intensities(self):
        base_intensity_dict = {}
        for variable_name in self.variable_names:
            variable_idx = self.variable_names.index(variable_name)
            base_intensity_dict[variable_name] = self.result['learned_params']['mu'][variable_idx]
        return base_intensity_dict


    def get_instance_triggering_probabilities(self, n):
        return self.result['learned_params']['qhist'][n]


    def get_instance_self_triggering_probability(self, n):
        return self.result['learned_params']['qself'][n]
        
    
    def show_causal_triggers_of(self, n, **kwargs):
        qself       = self.result['learned_params']['qself']
        qhist       = self.result['learned_params']['qhist']
        timestamps  = self.result['training_data']['timestamps']
        event_types = self.result['training_data']['event_types']
        
        return l0hawkesutils.show_causal_triggers_of(n,
                                                     qself, qhist, timestamps, event_types,
                                                     **kwargs)

    def show_model(self, **kwargs):
        return l0hawkesutils.show_model(self.result, **kwargs)

    


L0Hawkes = L0HawkesNh


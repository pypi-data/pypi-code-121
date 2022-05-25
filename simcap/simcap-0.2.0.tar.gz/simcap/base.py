# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import t, chi2, sem
from scipy.stats.mstats import meppf, mquantiles
from statsmodels.tsa.stattools import adfuller, kpss
from tqdm import tqdm
from .markov import markov_model_search
from .exceptions import StationaryWarning, CorrelatedExogWarning, NegativeValuesError
from joblib import Parallel, delayed
import warnings


class BaseSimulation:
    """
    Base class used to generate simulations of generic correlated, nonnegative, 
    nonstationary, multivariate time series.
    
    Parameters
    ----------
    endogenous : ndarray of shape (n_periods, n_variables)
        An endogenous variable is a variable in a model that is changed or determined 
        by its relationship with other variables within the model. Variables should be 
        in columns with periods in rows. It is assumed the passed array is already  
        sorted chronologically with the most recent observation in the last row. The  
        endogenous variables in this array will be modeled by the simulation.
    prototypes : list of ndarrays of shape (n_periods, ), optional
        A list of univariate time series of shape (n_periods, ). It is assumed each of 
        the prototypes are already sorted chronologically with the most recent  
        observation in the last element of the array. Prototypical time series can be 
        used to model distributions of endogenous variables. For example, if attempting 
        to model the price of a mutual fund with only two years of bull market price 
        history, one might decide to use a stock index like the S&P 500 as a prototype 
        for the mutual fund since the stock index has a longer history with examples 
        across all market regimes.
    endog_proto_rel : dict, optional
        Required if prototypes are used. A dictionary mapping endogenous variables to 
        prototype series. For example, if the first endogenous variable maps to the 
        first prototype, the second endogenous variable does not have a prototype, and 
        the third endogenous variable maps to the second prototype, pass the dictionary: 
        {0: 0, 1: None, 2: 1}
    exogenous : ndarray of shape (n_periods, n_variables), optional
        An exogenous variable is a variable in a model whose value is determined outside 
        the model but is imposed on the model. The exogenous variables that are passed 
        will influence the simulation but will not be modeled by the simulation. The 
        array should have the same number of rows as the endogenous array. Exogenous 
        observations for a particular period should be in the same row as the endogenous 
        observations for the same period.
    suppress_warnings : bool, default=False
        If True, StationaryWarning and CorrelatedExogWarning warnings are suppressed.
        
    """

    def __init__(
        self,
        endogenous,
        prototypes=None,
        endog_proto_rel=None,
        exogenous=None,
        suppress_warnings=False,
    ):
        self.endogenous = endogenous
        self.prototypes = prototypes
        self.endog_proto_rel = endog_proto_rel
        self.exogenous = exogenous
        self.suppress_warnings = suppress_warnings
        self.dataset_labels = ("Endogenous", "Exogenous")
        self._test_stationarity()
        self._validate_positive()
        self._remove_correlated_exog()

    @staticmethod
    def _stationary(mv_series):
        """
        Using the Augmented Dickey-Fuller test along with KPSS test to check 
        stationarity of each variable in a multivariate time series.

        Parameters
        ----------
        mv_series : ndarray of shape (n_periods, n_variables)
            A multivariate time series.

        Returns
        -------
        stationary : list
            A list that contains the column index of each variable that appears to be
            stationary. If no variables appear to be stationary, an empty list is
            returned.

        """
        stationary = list()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            for i, col in enumerate(mv_series.T):
                df_pvalue = adfuller(col)[1]
                kpss_pvalue = kpss(col)[1]
                if df_pvalue < 0.05 or kpss_pvalue > 0.05:
                    stationary.append(i)
        return stationary

    @staticmethod
    def _all_pos_values(mv_series):
        """
        This function checks to see that all values in a multivariate time series are
        positive.

        Parameters
        ----------
        mv_series : ndarray of shape (n_periods, n_variables)
            A multivariate time series.

        Returns
        -------
        bool
            Returns True if all values in the series are positive. If any values are
            negative, returns False.

        """
        return np.all(mv_series > 0)

    @staticmethod
    def _merge_endog_and_exog(endog, exog):
        """
        Simple wrapper to numpy hstack function that adds an array containing exogenous
        variables to an array containing endogenous variables. The number of rows in
        each array must be the same.

        Parameters
        ----------
        endog : ndarray of shape (n_periods, n_endog_variables)
            A multivariate time series containing endogenous variables.
        exog : ndarray of shape (n_periods, n_exog_variables)
            A univariate or multivariate time series containing exogenous variables.

        Returns
        -------
        ndarray of shape (n_periods, n_endog_variables + n_exog_variables)
            An array with the endogenous variables in the leftmost columns and the 
            exogenous variables in the rightmost columns.

        """
        return np.hstack((endog, exog))

    @staticmethod
    def _remove_exog_from_merged(merged, exog):
        """
        Removes exogenous variables from an array containing endogenous variables
        in the leftmost columns and exogenous variables in the rightmost columns.

        Parameters
        ----------
        merged : ndarray of shape (-1, n_endog_variables + n_exog_variables)
            An array with the endogenous variables in the leftmost columns and the 
            exogenous variables in the rightmost columns.
        exog : ndarray of shape (-1, n_exog_variables)
            An array containing exogenous variables.

        Returns
        -------
        ndarray of shape (-1, n_endog_variables)
            Returns the columns from merged that are attributable to endogenous 
            variables.

        """
        exog_idx_start = -exog.shape[1]
        return merged[:, :exog_idx_start]

    @staticmethod
    def _log_change(mv_series):
        """
        Computes the one-period log percantage change for each variable in a 
        multivariate time series.

        Parameters
        ----------
        mv_series : ndarray of shape (n_periods, n_variables)
            A multivariate time series.

        Returns
        -------
        pct_change : ndarray of shape (n_periods - 1, n_variables)
            The one-period log percentage change for each column in mv_series.

        """
        diff = np.diff(mv_series, axis=0)
        pct_change = np.log1p(diff / mv_series[:-1, :])
        return pct_change

    def _remove_correlated_exog(self):
        """
        Checks correlation of exogenous variables to endogenous variables. If any 
        exogenous variable has correlation coefficient of 0.98 or more or -0.98 or less
        to an endogenous variable, the exogenous variable is removed.

        """
        if self.exogenous is not None:
            endog = self.endogenous
            exog = self.exogenous
            merged = self._merge_endog_and_exog(endog, exog)
            endog_label, exog_label = self.dataset_labels

            exog_idx_start = -exog.shape[1]
            corr = np.corrcoef(merged, rowvar=False)
            endog_to_exog = corr[:exog_idx_start, exog_idx_start:]

            delete = list()
            for i, col in enumerate(endog_to_exog.T):
                if np.any(np.abs(col) >= 0.98):
                    delete.append(i)
            if len(delete) == exog.shape[1]:
                self.exogenous = None
                if not self.suppress_warnings:
                    w = (
                        f"{exog_label} data has been removed from consideration due to "
                        "all columns being highly correlated with one or more "
                        f"{endog_label} columns.\n"
                    )
                    warnings.warn(w, CorrelatedExogWarning)
            elif len(delete) > 0:
                self.exogenous = np.delete(exog, delete, axis=1)
                if not self.suppress_warnings:
                    w = (
                        f"{exog_label} columns {delete} have been removed from "
                        "consideration due to high correlation with one or more "
                        f"{endog_label} columns.\n"
                    )
                    warnings.warn(w, CorrelatedExogWarning)

    @staticmethod
    def _mean_rvs(log_change):
        """
        Given observation, estimate distribution space that contains the true population 
        mean. Return a random mean from this space using t-distrubtion. Random means are
        only sampled from within the bounds of the 70% confidence interval.
        
        Parameters
        ----------
        log_change : ndarray of shape (n_periods, )
            The one-period log percentage change for a column in a multivariate series.

        Returns
        -------
        random_mean : float
            Random value from t-distribution estimated to contain the true population 
            mean.
        
        """
        m = np.mean(log_change)
        n = log_change.shape[0]
        se = sem(log_change)
        t_dist = t(df=n - 1, loc=m, scale=se)
        lower_bound, upper_bound = t_dist.interval(alpha=0.7)
        random_mean = t_dist.rvs()
        while not lower_bound <= random_mean <= upper_bound:
            random_mean = t_dist.rvs()
        return random_mean

    @staticmethod
    def _std_rvs(log_change):
        """
        Given observation, estimate distribution space that contains the true population 
        standard deviation. Return a random standard deviation from this space using 
        chi squared distrubtion.
        
        Parameters
        ----------
        log_change : ndarray of shape (n_periods, )
            The one-period log percentage change for a column in a multivariate series.

        Returns
        -------
        random_mean : float
            Random value from chi squared distribution estimated to contain the true 
            population standard deviation.
            
        """
        s = np.std(log_change, ddof=1)
        n = log_change.shape[0]
        num = (n - 1) * (s ** 2)
        random_std = np.sqrt(num / chi2.rvs(df=n - 1))
        return random_std

    def _fit_hmm_sim_to_empirical(self, hmm_sim, log_change):
        """
        Fits each variable in a hidden markov model simulation to an emprical (or 
        prototypical) distribution so that the resulting simulation has log percentage 
        change distributions resembling the observed time series.

        Parameters
        ----------
        hmm_sim : ndarray of shape (n_periods, n_variables)
            A hidden markov model simulation of one-period log percentage changes.
        log_change : ndarray of shape (n_periods, n_variables)
            The one-period log percentage change for each column in a multivariate time
            series.

        Returns
        -------
        simulation : ndarray of shape (n_periods, n_variables)
            A random multivariate correlated simulation of log percentage changes where 
            the distribution each variable resembles the distribution found in the 
            empricial (or prototypical) time series.

        """
        protos = self.prototypes
        rel = self.endog_proto_rel
        exog = self.exogenous

        if exog is not None:
            hmm_sim = self._remove_exog_from_merged(hmm_sim, exog)
            log_change = self._remove_exog_from_merged(log_change, exog)
        simulation = np.empty_like(hmm_sim)

        for i, x_sim in enumerate(hmm_sim.T):

            # linear interpolation of cdf
            q = meppf(x_sim, alpha=0, beta=1)

            # apply quantiles of simulated data to kde of observed or
            # prototypical data
            x_endog = log_change[:, i]

            if rel is not None:
                proto_idx = rel[i]
                if proto_idx is not None:
                    proto = protos[rel[i]]
                    proto = self._log_change(proto.reshape(-1, 1))
                    sx = mquantiles(proto, q)
                else:
                    sx = mquantiles(x_endog, q)
            else:
                sx = mquantiles(x_endog, q)
            # get z scores of simulated data that was fit to kde
            mu = np.mean(sx)
            sig = np.std(sx, ddof=1)
            z = (sx - mu) / sig

            # get simulated mean and std based on observation
            new_mu = self._mean_rvs(x_endog)
            new_sig = self._std_rvs(x_endog)

            # adjust prototype to new mean and std
            new_x = z * new_sig + new_mu

            simulation[:, i] = new_x
        return simulation

    @staticmethod
    def _simulate_series(log_change, begin_values):
        """
        Use the one-period log percentage change for each column in a multivariate time
        series and beginning values for each of the columns to create a simulated time
        series.

        Parameters
        ----------
        log_change : ndarray of shape (n_periods, n_variables)
            The one-period log percentage change for each column in a multivariate time
            series.
        begin_values : ndarray of shape (1, n_variables)
            The beginning values for each column of a multivariate time series 
            simulation.

        Returns
        -------
        sim : ndarray of shape (n_periods, n_variables)
            Simulated multivariate time series.

        """
        sim = np.exp(np.cumsum(log_change, axis=0))
        sim = sim * begin_values
        sim = np.vstack((begin_values, sim[:-1, :]))

        return sim

    def _test_stationarity(self):
        """
        Checks each variable in endogenous time series for stationarity. Simulation is
        not intended for stationary variables.
        
        Raises
        ------
        StationaryWarning

        """
        if not self.suppress_warnings:
            w = (
                "{} columns {} appear to be stationary. This may negatively affect the "
                "simulation.\n"
            )

            endog = self._stationary(self.endogenous)
            endog_label, _ = self.dataset_labels
            if len(endog) > 0:
                warnings.warn(w.format(endog_label, str(endog)), StationaryWarning)

    def _validate_positive(self):
        """
        Checks all time series for negative values. Time series with negative values are 
        not supported.

        Raises
        ------
        NegativeValuesError

        """
        endog_label, exog_label = self.dataset_labels

        e = "{} data has negative values.\n"

        if not self._all_pos_values(self.endogenous):
            raise NegativeValuesError(e.format(endog_label))
        if self.prototypes is not None:
            for proto in self.prototypes:
                if proto is not None:
                    if not self._all_pos_values(proto):
                        raise NegativeValuesError(e.format("Prototype"))
        if self.exogenous is not None:
            if not self._all_pos_values(self.exogenous):
                raise NegativeValuesError(e.format(exog_label))

    def _begin_values(self, bv_arg):
        """
        Creates beginning values array to use in the simulation given the begin_values
        parameter passed at initiation.
        
        Parameters
        ----------
        bv_arg : {"start", "end", "norm"}
        
        Returns
        -------
        begin_values : ndarray of shape (1, n_variables)
            The beginning values for each column of a multivariate time series 
            simulation.

        """
        endog = self.endogenous

        if bv_arg == "start":
            begin_values = endog[0, :]
        elif bv_arg == "end":
            begin_values = endog[-1, :]
        elif bv_arg == "norm":
            begin_values = np.ones((1, endog.shape[1]))
        else:
            raise ValueError(
                'begin_values parameter must be in ("start", "end", "norm").'
            )
        return begin_values

    def _periods_per_sim(self, periods):
        """
        Sets periods_per_sim parameter if not passed at initiation.
        
        Parameters
        ----------
        periods : None or int
            
        Returns
        -------
        int
            Periods per simulation.

        """
        endog = self.endogenous

        if periods is not None and not isinstance(periods, int):
            raise TypeError("periods_per_sim parameter must be an integer")
        elif periods is None:
            return endog.shape[0]
        else:
            return periods

    def generate_simulations(
        self,
        n_sims=100,
        periods_per_sim=None,
        begin_values="start",
        hmm_search_n_iter=60,
        hmm_search_n_fits_per_iter=10,
        hmm_search_params=None,
        output_as_float32=False,
        n_jobs=None,
        verbose=True,
    ):
        """
        Generate simulations using the data set at object initiation.
        
        Parameters
        ----------
        n_sims : int, default=100
            The number of simulations to generate.
        periods_per_sim : int, optional
            The number of periods, or rows, to generate in each simulation. If None 
            (default), the periods per simulation will match the number of rows in the 
            endogenous array.
        begin_values : {"start", "end", "norm"}, default="start"
            The values to set for the first row of each simulation. "start" will set the 
            first row of each simulation to match the first row of the endogenous 
            series. "end" will set the first row of each simulation to match the last 
            row of the endogenous series. "norm" will set the first row of each 
            simulation to 1 in all columns.
        hmm_search_n_iter : int, default=60
            For Hidden Markov Model search, the number of parameter settings that are 
            sampled. ``n_iter`` trades off runtime vs quality of the solution. If 
            exhausitive search of the parameter grid would result in fewer iterations, 
            search stops when all parameter combinations have been searched.
        hmm_search_n_fits_per_iter : int, default=10
            The number of Hidden Markov Models to be randomly initialized and evaluated 
            for each combination of parameter settings.
        hmm_search_params : dict, default=None
            For Hidden Markov Model search, dictionary with parameter names (str) as 
            keys and lists of parameters to try as dictionary values. Parameter lists 
            are sampled uniformly. All of the parameters are required:
            
            * n_states: list of ints
            * cov_window_size: list of ints
            * pca_n_components: list of floats, ints, or None
            * scale_before_pca: list of bool
            * scale_after_pca: list of bool
            
            If ``fit_pipeline_params`` is ``None``, default is::

                dict = (
                    n_states = [3, 4, 5, 6, 7, 8, 9],
                    cov_window_size = [13, 21, 34, 55, 89, 144],
                    pca_n_components = [0.8, 0.85, 0.9, 0.95, None],
                    scale_before_pca = [True, False],
                    scale_after_pca = [True, False],
                )
        output_as_float32 : bool, default=False
            If True, convert simulation array to float32. If False, simulation will be 
            output as float64.
        n_jobs : int, default=None
            Number of jobs to run in parallel when performing Hidden Markov Model search 
            as well as when generating simulations. None means 1. -1 means using all 
            processors. 
        verbose : bool, default=True
            If True, progress bar written to stdout as simulations are generated.

        Returns
        -------
        simulations : ndarray of shape (n_simulations, n_periods, n_variables)
            An array of multiple simulated multivariate time series.

        """
        size = self._periods_per_sim(periods_per_sim)
        endog = self.endogenous
        exog = self.exogenous
        bv = self._begin_values(begin_values)

        if n_jobs is None:
            n_jobs = 1
        # merge endogenous and exogenous series
        if exog is not None:
            series = self._merge_endog_and_exog(endog, exog)
        else:
            series = endog
        # calculate log percentage change
        series_log_change = self._log_change(series)

        # fit hidden_markov_model
        results, _ = markov_model_search(
            series_log_change,
            hmm_search_n_iter,
            hmm_search_n_fits_per_iter,
            hmm_search_params,
            n_jobs=n_jobs,
            verbose=verbose,
        )
        model = results["model"]

        # generate simulations
        def single_simulation(i):
            markov_sim, _ = model.sample(size)
            sim_log_change = self._fit_hmm_sim_to_empirical(
                markov_sim, series_log_change
            )
            simulation = self._simulate_series(sim_log_change, bv)

            if output_as_float32:
                simulation = simulation.astype("float32")
            return simulation

        parallel = Parallel(n_jobs=n_jobs)

        tqdm_args = {
            "iterable": range(n_sims),
            "desc": f"generating sims (n_jobs={n_jobs})",
            "total": n_sims,
            "disable": not verbose,
            "position": 0,
            "leave": True,
        }

        simulations = parallel(delayed(single_simulation)(i) for i in tqdm(**tqdm_args))

        simulations = np.array(simulations)

        return simulations

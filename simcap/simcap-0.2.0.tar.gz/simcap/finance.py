# -*- coding: utf-8 -*-

import pandas as pd
from .base import BaseSimulation


class SimCAP(BaseSimulation):
    """
    Simulation of Correlated Asset Prices
    
    Parameters
    ----------
    asset_price_history : pandas DataFrame of shape (n_periods, n_assets)
        DataFrame of asset price history. Assets should be in columns with periods in 
        rows. Ticker symbol or some other unique label for the asset should be in the 
        first row. It is assumed the passed DataFrame is already sorted chronologically 
        with the most recent price observation in the last row. Each of the assets in  
        this DataFrame will be modeled by the simulation.
    prototypes : list of ndarrays or pandas Series of shape (n_periods, ), optional
        A list of univariate time series of shape (n_periods, ). It is assumed each of 
        the prototypes are already sorted chronologically with the most recent  
        observation in the last element of the array/Series. Prototypical time series 
        can be used to model distributions of assets. For example, if attempting to 
        model the price of a mutual fund with only two years of bull market price 
        history, one might decide to use a stock index like the S&P 500 as a prototype 
        for the mutual fund since the stock index has a longer history with examples 
        across all market regimes.
    asset_proto_rel : dict, optional
        Required if prototypes are used. A dictionary mapping assets to prototypes. For 
        example, if the asset with ticker of "SPD" maps to the first prototype, "GSUS" 
        does not have a prototype, and "XVV" maps to the second prototype, pass the 
        dictionary: {"SPD": 0, "GSUS": None, "XVV": 1}
    external_factors : pandas DataFrame of shape (n_periods, n_assets), optional
        DataFrame of factors that are used to influence the simulation of asset prices 
        but are not simulated themselves. The DataFrame should have the same number of 
        rows as the asset_price_history DataFrame. external_factor observations for a 
        particular period should be in the same row as the asset_price_history 
        observations for the same period. For example, if row 4 of the 
        asset_price_history DataFrame are prices recorded on 2021-11-15, row 4 of the 
        external_factors DataFrame should also be values that were recorded on 
        2021-11-15.
    suppress_warnings : bool, default=False
        If True, StationaryWarning and CorrelatedExogWarning warnings are suppressed.
    
    
    Examples
    --------
    >>> from simcap.datasets import load_example_asset_price_history
    >>> from simcap import SimCAP
    >>> asset_prices = load_example_asset_price_history()
    >>> print(asset_prices.shape)
    (2517, 8)
    >>> model = SimCAP(asset_prices)
    >>> sims = model.generate_simulations(
    >>>     n_sims=10, 
    >>>     periods_per_sim=500,
    >>>     output_as_dfs=False,
    >>> )
    >>> print(sims.shape)
    (10, 500, 8)
        
    """

    def __init__(
        self,
        asset_price_history,
        prototypes=None,
        asset_proto_rel=None,
        external_factors=None,
        suppress_warnings=False,
    ):
        self.asset_price_history = asset_price_history
        self.prototypes = self._convert_proto_series_to_array(prototypes)
        self.asset_proto_rel = asset_proto_rel
        self.external_factors = external_factors
        self.suppress_warnings = suppress_warnings
        self.dataset_labels = ("Asset Price History", "External Factors")
        self.tickers_ = asset_price_history.columns.tolist()
        self._history_to_endog()
        self._external_to_exog()
        self._prepare_rel()
        self._test_stationarity()
        self._validate_positive()
        self._remove_correlated_exog()

    def _history_to_endog(self):
        """
        Sets asset_price_history values as the endogenous parameter of the base 
        simulator.

        """
        self.endogenous = self.asset_price_history.values

    @staticmethod
    def _convert_proto_series_to_array(prototypes):
        """
        If prototypes are pandas Series instances, convert to numpy arrays.

        """
        if prototypes is not None:
            new_protos = list()
            for proto in prototypes:
                if isinstance(proto, pd.Series):
                    new_protos.append(proto.values)
                else:
                    new_protos.append(proto)
            return new_protos
        else:
            return None

    def _external_to_exog(self):
        """
        Sets external_factors values as the exogenous parameter of the base simulator.

        """
        if self.external_factors is not None:
            self.exogenous = self.external_factors.values
        else:
            self.exogenous = None

    def _prepare_rel(self):
        """
        Converts ticker-to-prototype relationship to column-index-to-prototype 
        relationship setup used in the base simulator.

        """
        if self.asset_proto_rel is not None:
            endog_proto_rel = dict()
            for k, v in self.asset_proto_rel.items():
                endog_proto_rel[self.tickers_.index(k)] = v
            self.endog_proto_rel = endog_proto_rel
        else:
            self.endog_proto_rel = None

    def generate_simulations(
        self,
        n_sims=100,
        periods_per_sim=None,
        begin_values="norm",
        hmm_search_n_iter=60,
        hmm_search_n_fits_per_iter=10,
        hmm_search_params=None,
        output_as_dfs=True,
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
            asset_price_history DataFrame.
        begin_values : {"start", "end", "norm"}, default="norm"
            The values to set for the first row of each simulation. "start" will set the 
            first row of each simulation to match the first row of asset prices in the 
            asset_price_history DataFrame. "end" will set the first row of each 
            simulation to match the last row of the asset_price_history DataFrame. 
            "norm" will set the first row of each simulation to 1 for all assets.
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
        output_as_dfs : bool, default=True
            If True, simulations are output as an n_sims element list of DataFrames of 
            shape (periods_per_sim, n_assets). If False, simulations are ouput as an 
            ndarray of shape (n_sims, periods_per_sim, n_assets).
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
        simulations : list (of length n_sims) of pandas DataFrames of shape 
        (n_periods, n_variables) or ndarray of shape (n_simulations, n_periods, 
        n_variables)
            If ``output_as_dfs`` is True, simulations are output as an n_sims 
            element list of DataFrames of shape (periods_per_sim, n_assets).
            If False, simulations are ouput as an ndarray of shape (n_sims, 
            periods_per_sim, n_assets).

        """
        simulations = super().generate_simulations(
            n_sims=n_sims,
            periods_per_sim=periods_per_sim,
            begin_values=begin_values,
            hmm_search_n_iter=hmm_search_n_iter,
            hmm_search_n_fits_per_iter=hmm_search_n_fits_per_iter,
            hmm_search_params=hmm_search_params,
            output_as_float32=output_as_float32,
            n_jobs=n_jobs,
            verbose=verbose,
        )

        if output_as_dfs:
            simulations = [pd.DataFrame(a, columns=self.tickers_) for a in simulations]
        return simulations

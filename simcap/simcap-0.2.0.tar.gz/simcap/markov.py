# -*- coding: utf-8 -*-

import numpy as np
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.model_selection import ParameterGrid
from random import shuffle
from hmmlearn import hmm
from joblib import Parallel, delayed
from tqdm import tqdm


class MarkovModelSearch:
    @staticmethod
    def _split_series_into_windows(mv_series, window_size):
        """
        Split 2d matrix of shape (n_periods, n_variables) into 3d matrix of shape
        (n_windows, window_size, n_variables).

        Parameters
        ----------
        mv_series : ndarray of shape (n_periods, n_variables)
            A multivariate time series.
        window_size : int
            The number of periods to be included in each window.

        Returns
        -------
        windows : ndarray of shape (n_windows, window_size, n_variables)
            A multivariate time series split into n windows of ``window_size``.

        """
        clip_size = mv_series.shape[0] % window_size
        if clip_size > 0:
            mv_series = mv_series[:-clip_size, :]
        windows = mv_series.reshape(-1, window_size, mv_series.shape[1])
        return windows

    @staticmethod
    def _cluster_for_init(
        windows, pca_n_components, n_clusters, scale_before_pca, scale_after_pca
    ):
        """
        Clustering of windowed time series by correlation coefficients. For each window
        in windows, correlation coefficients, covariance, and variable means are 
        computed. Windows are clustered into ``n_clusters`` and assigned a cluster 
        label. Each window's covariance matrix, variable means, and cluster label is 
        returned.
        
        Pipeline for clustering:
        
        1. Upper triangle of correlation matrix for each window is flattened and added 
           as a row of a 2d matrix; one row of coefficients per window.
        2. If scale_before_pca parameter is ``True``, the 2d matrix of coefficients is 
           scaled using scikit-learn ``StandardScaler``.
        3. Dimensions are reduced using PCA. The ``pca_n_components`` parameter controls 
           the level of dimentionality reduction.
        4. If ``scale_after_pca`` parameter is ``True``, the matrix resulting from the 
           PCA transformation is scaled using scikit-learn ``StandardScaler``.
        5. Processed data is fit to scikit-learn ``AgglomerativeClustering`` algorithm. 
           The ``n_clusters`` parameter controls how many clusters will be returned.
        6. Cluster labels are assigned to each window.

        Parameters
        ----------
        windows : ndarray of shape (n_windows, window_size, n_variables)
            A multivariate time series split into n windows of ``window_size``.
        pca_n_components : int or float
            scikit-learn PCA ``n_components`` parameter.
        n_clusters : int
            scikit-learn ``AgglomerativeClustering n_clusters`` parameter.
        scale_before_pca : bool
            If ``True``, correlation coefficients are scaled prior to PCA 
            transformation.
        scale_after_pca : bool
            If ``True``, correlation coefficients are scaled after PCA transformation.

        Returns
        -------
        cov_matrices : ndarray of shape (n_windows, n_variables, n_variables)
            Computed covariance matrices for each of the input windows.
        means : ndarray of shape (n_windows, n_variables)
            Computed means for each variable of each of the input windows.
        cluster_labels : ndarray of shape (n_windows, )
            Cluster label assigned to each of the input windows.

        """
        cols = windows.shape[2]
        cov_matrices = list()
        means = list()
        corr_coefs = list()

        for window in windows:
            cov_matrix = np.cov(window, rowvar=False)
            cov_matrices.append(cov_matrix)

            mean = window.mean(axis=0)
            means.append(mean)

            corr_matrix = np.corrcoef(window, rowvar=False)
            corr_coef = corr_matrix[np.triu_indices(cols, k=1)]
            corr_coefs.append(corr_coef)
        cov_matrices = np.array(cov_matrices)
        means = np.array(means)
        corr_coefs = np.array(corr_coefs)

        pca = PCA(n_components=pca_n_components)

        if scale_before_pca:
            features = pca.fit_transform(corr_coefs)
        else:
            features = pca.fit_transform(scale(corr_coefs))
        if scale_after_pca:
            features = scale(features)
        model = AgglomerativeClustering(n_clusters)
        cluster_labels = model.fit_predict(features)

        return cov_matrices, means, cluster_labels

    @staticmethod
    def _random_covariance_init(cov_matrices, cluster_labels):
        """
        Given covariance matrices for each window and the cluster labels for each 
        window, return a random covariance matrix for each cluster.

        Parameters
        ----------
        cov_matrices : ndarray of shape (n_windows, n_variables, n_variables)
            Covariance matrices for n windows.
        cluster_labels : ndarray of shape (n_windows, )
            Cluster label assigned to each of n windows.

        Returns
        -------
        covar_init : ndarray of shape (n_clusters, n_variables, n_variables)
            Random covariance matrix for each of n clusters.

        """
        covar_init = list()

        for i in np.unique(cluster_labels):
            cluster_cov_matrices = cov_matrices[cluster_labels == i]
            n = cluster_cov_matrices.shape[0]
            choice = int(np.random.uniform(0, n))
            covar_init.append(cluster_cov_matrices[choice])
        covar_init = np.array(covar_init)

        return covar_init

    @staticmethod
    def _random_mean_init(means, cluster_labels):
        """
        Given variable means for each window and the cluster labels for each window, 
        return random variable means for each cluster.

        Parameters
        ----------
        means : ndarray of shape (n_windows, n_variables)
            Variable means for n windows.
        cluster_labels : ndarray of shape (n_windows, )
            Cluster label assigned to each of n windows.

        Returns
        -------
        mean_init : ndarray of shape (n_clusters, n_variables)
            Random variables means for each of n clusters.

        """
        mean_init = list()

        for i in np.unique(cluster_labels):
            cluster_means = means[cluster_labels == i]
            n = cluster_means.shape[0]
            choice = int(np.random.uniform(0, n))
            mean_init.append(cluster_means[choice])
        mean_init = np.array(mean_init)

        return mean_init

    @staticmethod
    def fit_hmm_model(log_change, n_states, covar_init, mean_init):
        """
        Fit a Hidden Markov Model with Gaussian emissions.

        Parameters
        ----------
        log_change : ndarray of shape (n_periods, n_variables)
            The one-period log percentage change for each column in a multivariate time
            series.
        n_states : int
            The number of hidden states to model.
        covar_init : ndarray of shape (n_states, n_variables, n_variables)
            Covariance matrix used to initiate the model.
        mean_init : ndarray of shape (n_states, n_variables)
            Variable means used to initiate the model.

        Returns
        -------
        model : hmmlearn.hmm.GaussianHMM
            The fit Hidden Markov Model with Gaussian emissions.
        score : float
            The log-likelihood of input ``log_change`` under the fit model.

        """
        model = hmm.GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            covars_prior=covar_init,
            means_prior=mean_init,
        )
        model.fit(log_change)
        score = model.score(log_change)
        return model, score

    def run_fit_pipeline(
        self,
        log_change,
        n_states,
        cov_window_size,
        pca_n_components,
        scale_before_pca,
        scale_after_pca,
        n_fits,
    ):
        """
        Hidden Markov Models are prone to converging on local optima based on where the
        optimization is initiated. In an attempt to find a model closer to the global 
        optimum, several models are initiated with different random covariance matrices
        and variable means. The best performing model is returned.

        Parameters
        ----------
        log_change : ndarray of shape (n_periods, n_variables)
            The one-period log percentage change for each column in a multivariate time
            series.
        n_states : int
            The number of hidden states to model.
        cov_window_size : int
            The number of periods to be included in each window of the time series.
        pca_n_components : int or float
            scikit-learn PCA ``n_components`` parameter.
        scale_before_pca : bool
            If ``True``, correlation coefficients are scaled prior to PCA 
            transformation.
        scale_after_pca : bool
            If ``True``, correlation coefficients are scaled after PCA transformation.
        n_fits : int
            The number of Hidden Markov Models to be randomly initialized and evaluated.

        Returns
        -------
        best_score : float
            The log-likelihood of input ``log_change`` under the fit model with the 
            highest log-likelihood score.
        best_params : dict
            The parameters used to fit the model with the highest log-likelihood score.
        best_model : model : hmmlearn.hmm.GaussianHMM
            The fit Hidden Markov Model with the highest log-likelihood score.

        """
        windows = self._split_series_into_windows(log_change, cov_window_size)
        cov_matrices, means, cluster_labels = self._cluster_for_init(
            windows, pca_n_components, n_states, scale_before_pca, scale_after_pca,
        )

        best_score = 0
        best_model = None
        best_params = None

        for i in range(n_fits):
            covar_init = self._random_covariance_init(cov_matrices, cluster_labels)
            mean_init = self._random_mean_init(means, cluster_labels)
            model, score = self.fit_hmm_model(
                log_change, n_states, covar_init, mean_init
            )

            if score > best_score:
                best_score = score
                best_model = model
                best_params = dict(
                    n_states=n_states,
                    cov_window_size=cov_window_size,
                    pca_n_components=pca_n_components,
                    scale_before_pca=scale_before_pca,
                    scale_after_pca=scale_after_pca,
                    covar_init=covar_init,
                    mean_init=mean_init,
                )
        return best_score, best_params, best_model

    def model_search(
        self,
        log_change,
        n_iter,
        n_fits_per_iter,
        fit_pipeline_params=None,
        n_jobs=None,
        verbose=False,
    ):
        """
        Randomized grid search of hyperparameter space to find a well-performing Hidden
        Markov Model. 

        Parameters
        ----------
        log_change : ndarray of shape (n_periods, n_variables)
            The one-period log percentage change for each column in a multivariate time
            series.
        n_iter : int
            Number of parameter settings that are sampled. ``n_iter`` trades off runtime 
            vs quality of the solution. If exhausitive search of the grid would result
            in fewer iterations, search stops when all parameter combinations have been
            searched.
        n_fits_per_iter : int
            The number of Hidden Markov Models to be randomly initialized and evaluated.
        fit_pipeline_params : dict
            Dictionary with parameter names (str) as keys and lists of parameters to 
            try as dictionary values. Parameter lists are sampled uniformly. All 
            of the parameters are required:
            
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
            
        n_jobs : int, default=None
            Number of jobs to run in parallel when performing Hidden Markov Model 
            search. None means 1. -1 means using all processors. 
        verbose : bool, default=False
            If ``True``, progress bar written to stdout during model search.

        Returns
        -------
        best_results : dict
            Dictionary with the following keys and values:
                
            +--------+-------------------------------------------------------------+
            | key    | value                                                       |
            +========+=============================================================+
            | model  | The fit Hidden Markov Model with the highest log-likelihood | 
            |        | score.                                                      |
            +--------+-------------------------------------------------------------+
            | params | The parameters used to fit the model with the highest       |
            |        | log-likelihood score.                                       |
            +--------+-------------------------------------------------------------+
            | score  | The log-likelihood of input ``log_change`` under the fit    |
            |        | model with the highest log-likelihood score.                |
            +--------+-------------------------------------------------------------+
                
        models : list of dicts
            List of each model fit in ``n_iter``. The dictonary in each element contains
            the same keys and values expained in for ``best_results``.

        """
        if fit_pipeline_params is None:
            fit_pipeline_params = dict(
                n_states=[3, 4, 5, 6, 7, 8, 9],
                cov_window_size=[13, 21, 34, 55, 89, 144],
                pca_n_components=[0.8, 0.85, 0.9, 0.95, None],
                scale_before_pca=[True, False],
                scale_after_pca=[True, False],
            )
        param_grid = list(ParameterGrid(fit_pipeline_params))
        shuffle(param_grid)

        if n_iter < len(param_grid):
            param_grid = param_grid[:n_iter]

        def single_fit(params):
            model_score, model_params, model = self.run_fit_pipeline(
                log_change,
                n_states=params["n_states"],
                cov_window_size=params["cov_window_size"],
                pca_n_components=params["pca_n_components"],
                scale_before_pca=params["scale_before_pca"],
                scale_after_pca=params["scale_after_pca"],
                n_fits=n_fits_per_iter,
            )

            result = {"score": model_score, "params": model_params, "model": model}

            return result

        parallel = Parallel(n_jobs=n_jobs)

        tqdm_args = {
            "iterable": param_grid,
            "desc": f"markov model search (n_jobs={n_jobs})",
            "total": len(param_grid),
            "disable": not verbose,
            "position": 0,
            "leave": True,
        }

        models = parallel(delayed(single_fit)(params) for params in tqdm(**tqdm_args))

        best_score = 0
        best_results = None

        for results in models:
            if results["score"] > best_score:
                best_score = results["score"]
                best_results = results
        return best_results, models


def markov_model_search(
    log_change,
    n_iter,
    n_fits_per_iter,
    fit_pipeline_params=None,
    n_jobs=None,
    verbose=False,
):
    """
    Randomized grid search of hyperparameter space to find a well-performing Hidden
    Markov Model. 

    Parameters
    ----------
    log_change : ndarray of shape (n_periods, n_variables)
        The one-period log percentage change for each column in a multivariate time
        series.
    n_iter : int
        Number of parameter settings that are sampled. ``n_iter`` trades off runtime 
        vs quality of the solution. If exhausitive search of the parameter grid would 
        result in fewer iterations, search stops when all parameter combinations have 
        been searched.
    n_fits_per_iter : int
        The number of Hidden Markov Models to be randomly initialized and evaluated.
    fit_pipeline_params : dict
        Dictionary with parameter names (str) as keys and lists of parameters to 
        try as dictionary values. Parameter lists are sampled uniformly. All 
        of the parameters are required:
        
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
        
    n_jobs : int, default=None
        Number of jobs to run in parallel when performing Hidden Markov Model 
        search. None means 1. -1 means using all processors.
    verbose : bool, default=False
        If ``True``, progress bar written to stdout during model search.

    Returns
    -------
    best_results : dict
        Dictionary with the following keys and values:
            
        +--------+-------------------------------------------------------------+
        | key    | value                                                       |
        +========+=============================================================+
        | model  | The fit Hidden Markov Model with the highest log-likelihood | 
        |        | score.                                                      |
        +--------+-------------------------------------------------------------+
        | params | The parameters used to fit the model with the highest       |
        |        | log-likelihood score.                                       |
        +--------+-------------------------------------------------------------+
        | score  | The log-likelihood of input ``log_change`` under the fit    |
        |        | model with the highest log-likelihood score.                |
        +--------+-------------------------------------------------------------+
            
    models : list of dicts
        List of each model fit in ``n_iter``. The dictonary in each element contains
        the same keys and values expained in for ``best_results``.

    """
    mms = MarkovModelSearch()
    best_results, models = mms.model_search(
        log_change, n_iter, n_fits_per_iter, fit_pipeline_params, n_jobs, verbose
    )
    return best_results, models

import numpy as np
from tqdm import tqdm
from msepm.compute import get_state_gradient, get_site_values
from msepm.compute import predict_epm_states, solve_regression_system
from msepm.scaler import Scaler
from msepm.helpers import pearson_correlation


class EPMBase:

    def __init__(self, iter_limit=100, n_jobs=1,
                 error_tolerance=0.001, learning_rate=0.01,
                 scale_X=False, verbose=False):
        self._coefs = None
        self._intercepts = None
        self._error = None
        self.iter_limit = iter_limit
        self.n_jobs = n_jobs
        self.error_tolerance = error_tolerance
        self.learning_rate = learning_rate
        self.scale_X = scale_X
        self.verbose = verbose

    def predict(self, Y: np.ndarray, return_site_predictions=False):
        if self._coefs is None:
            print("EPM model not trained\nRun .fit method to train model")
            return 1
        _coef = predict_epm_states(self._coefs, self._intercepts, Y)
        if return_site_predictions:
            return _coef, get_site_values(self._coefs, self._intercepts, _coef)
        return _coef

    def fit_epm(self, X, Y, sample_weights=None, verbose=False):
        fit_X, fit_Y = np.copy(X, order='k'), np.copy(Y, order='k')
        if len(fit_X.shape) == 1:
            fit_X = fit_X.reshape(-1, 1)
        error = None
        scaler = Scaler()
        scaler.fit(fit_X)
        verbose_t = tqdm(disable=True if not verbose else False, desc=f'Fitting MSEPM ')
        for iteration in range(self.iter_limit):
            _iter_sys = solve_regression_system(fit_X, fit_Y, n_jobs=self.n_jobs)
            _iter_error = sum(_iter_sys[2])
            gradient = get_state_gradient(_iter_sys[0], _iter_sys[1], fit_X, fit_Y)
            if iteration == 0:
                error = _iter_error
            else:
                if error - _iter_error < self.error_tolerance:
                    fit_X += gradient * self.learning_rate * fit_X
                    break
                else:
                    error = _iter_error
            fit_X -= gradient * self.learning_rate
            if self.scale_X:
                fit_X = scaler.transform(fit_X)
            verbose_t.update(1)
        self._coefs = _iter_sys[0]
        self._intercepts = _iter_sys[1]
        self._error = error

    def score(self, X, Y):
        predictions = self.predict(Y)
        scores = pearson_correlation(predictions, X.T)
        return np.array([scores[i][i] for i in range(scores.shape[0])])


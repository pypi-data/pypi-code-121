import random
from typing import Dict, Tuple
import joblib
import numpy as np
from tqdm import tqdm
from msepm.base import EPMBase
from msepm import MultistateEpigeneticPacemaker
from msepm.helpers import get_fold_step_size, tqdm_joblib


class MultistateEpigeneticPacemakerCV(EPMBase):
    """
        """

    def __init__(self,
                 cv_folds: int = 3, randomize_sample_order: bool = False,
                 iter_limit=100, n_jobs=1,
                 error_tolerance=0.001, learning_rate=0.01,
                 scale_X=False, verbose=False):
        EPMBase.__init__(self)
        self.cv_folds = cv_folds
        self.randomize = randomize_sample_order
        self.iter_limit = iter_limit
        self.n_jobs = n_jobs
        self.error_tolerance = error_tolerance
        self.learning_rate = learning_rate
        self.scale_X = scale_X
        self.verbose = verbose

    def fit(self, X, Y, sample_weights=None, return_out_of_fold_predictions=False):
        cv_groups = self.get_cv_folds(X.shape[0])
        fold_count = 0
        # reshape X if one dimensional
        X_fit = X if len(X.shape) > 1 else X.reshape(-1, 1)
        coefs, intercepts, errors = np.zeros((Y.shape[0], X_fit.shape[1])), np.zeros(Y.shape[0]), 0.0
        training_sample_count = 0
        predictions = {}
        with tqdm_joblib(tqdm(desc="Fitting CV Folds", total=self.cv_folds,
                              disable=True if not self.verbose else False)) as progress_bar:
            models = joblib.Parallel(n_jobs=self.n_jobs)(
                joblib.delayed(self.fit_fold)(*[X_fit, Y,
                                                test_indices,
                                                return_out_of_fold_predictions,
                                                sample_weights]) for
                test_indices in cv_groups)
        for model, train_len, model_predictions in models:
            training_sample_count += train_len
            predictions.update(model_predictions)
            coefs += model._coefs * train_len
            intercepts += model._intercepts * train_len
            errors += model._error * train_len
            fold_count += 1
        self._coefs = coefs / training_sample_count
        self._intercepts = intercepts / training_sample_count
        self._error = errors / training_sample_count
        if return_out_of_fold_predictions:
            return self.unpack_out_of_fold_predictions(predictions)

    def fit_fold(self, X, Y, test_indices, return_out_of_fold_predictions=False, sample_weights=None):
        fold_epm = MultistateEpigeneticPacemaker(iter_limit=self.iter_limit, error_tolerance=self.error_tolerance,
                                                 learning_rate=self.learning_rate, scale_X=self.scale_X, n_jobs=1)
        train_indices = [index for index in range(X.shape[0]) if index not in test_indices]
        train_Y = Y[:, train_indices]
        train_X = X[train_indices, :]

        test_Y = Y[:, test_indices]

        fold_epm.fit(train_X, train_Y, sample_weights=sample_weights)
        predictions = {}
        if return_out_of_fold_predictions:
            test_states = fold_epm.predict(test_Y)
            for index, state in zip(test_indices, test_states):
                predictions[index] = state
        return fold_epm, len(train_indices), predictions

    def get_cv_folds(self, sample_number):
        if self.cv_folds < 0:
            self.cv_folds = sample_number
        sample_indices = [count for count in range(sample_number)]
        if self.randomize:
            random.shuffle(sample_indices)
        step_size = get_fold_step_size(sample_number, self.cv_folds)
        test_indices = []
        for fold in range(self.cv_folds):
            if fold + 1 == self.cv_folds:
                test_indices.append(sample_indices[fold * step_size:])
            else:
                test_indices.append(sample_indices[fold * step_size: fold * step_size + step_size])
        return test_indices

    @staticmethod
    def unpack_out_of_fold_predictions(predictions):
        return np.array([predictions[index] for index in range(len(predictions))])

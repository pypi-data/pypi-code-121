import pandas as pd
from cryptotoolbox.utility import metrics
from cryptotoolbox.signal import signal_utility
from datetime import datetime
from pathlib import Path
from cryptotoolbox.parallel_run import signal_result_analyzer
from cryptotoolbox.file_saver import dropbox_file_saver


class DeterministicSharpeOptimModel():
    def __init__(self):
        self.w_optim = None
        return

    def calibrate(self, X, y):
        return

    def fit(self, X_train, y_train, X_val, y_val):
        w_optim = signal_utility.deterministic_optim_sharpe(signal_data=X_train.copy(),returns = y_train.copy())
        self.w_optim = w_optim

    def predict(self, X_test):
        data = pd.DataFrame(X_test.values * self.w_optim, columns=X_test.columns, index=X_test.index)
        X_test['signal'] = data.sum(axis=1)
        return X_test['signal'].values

    def get_features_importance(self, features_names):
        run_importances = {}
        for (name, imp) in zip(features_names, self.w_optim):
            run_importances[name] = imp
        return run_importances

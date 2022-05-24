from cryptotoolbox.rebalancing import allocation
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.utility import metrics
import pandas as pd
import numpy as np


class ERC_Allocation_Model():
    def __init__(self):
        self.w_optim = None
        self.cutting_rate_threshold = 0.7
        self.share_for_flat_signals = 0.1
        return

    def calibrate(self, X, y, number_per_year=252):
        X = X[[col for col in X.columns if 'signal' in col]]
        param_grid = {
            'cutting_rate_threshold': [0.62,0.7,0.85,0.91],
            'share_for_flat_signals': [0.05,0.1,0.22,0.3]
        }
        best_params = {}
        for cutting_rate_threshold in param_grid['cutting_rate_threshold']:
            for share_for_flat_signals in param_grid['share_for_flat_signals']:
                self.fit(X,y,X,y)
                y_pred_discrete = self.predict(X)
                perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                                      transaction_cost=False,
                                                                      print_turnover=False)
                sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
                best_params[(cutting_rate_threshold,share_for_flat_signals)] = sharpe_strat
        self.cutting_rate_threshold, self.share_for_flat_signals = max(best_params)

    def fit(self, X_train, y_train, X_val, y_val):
        X_t = X_train.copy()
        X_t = X_t.fillna(0)
        n_step, n_asset = X_t.shape
        def filtering_process(series):
            # True if less than 50% of obs. are constant
            return series.value_counts(dropna=False).max() < self.cutting_rate_threshold * n_step
        assets = X_t.apply(filtering_process).values
        w_optim = np.zeros(n_asset)
        signals_returns_df = signal_utility.recompute_perf_returns(X_t.loc[:,assets],y_train)
        signals_returns_df = signals_returns_df.fillna(0)
        w_optim_assets = allocation.ERC(signals_returns_df)
        w_optim_assets = w_optim_assets.reshape(w_optim_assets.size)
        nb_asset_optimized = np.sum(assets)
        nb_asset_not_optimized = n_asset - nb_asset_optimized
        w_optim[assets] = w_optim_assets*(1-self.share_for_flat_signals)
        w_optim[list(map(bool, 1-assets))] = self.share_for_flat_signals * (1 / nb_asset_not_optimized)
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

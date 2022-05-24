from cryptotoolbox.mixing import mixing_utility

import lightgbm as lgb

import numpy as np

from sklearn.model_selection import cross_val_score, GridSearchCV, KFold, RandomizedSearchCV, train_test_split



class LGBMModel():

    def __init__(self, preprocessing = False, threshold = 0.6, number_per_year=252):
        self.model = lgb.LGBMRegressor()

    def calibrate(self, X, y):#, method = 'standard'):
        param_grid = {
            'boosting_type': ['gbdt'],
            'num_leaves': [int(x) for x in np.linspace(start=10, stop=30, num=10)],
            'max_depth': [int(x) for x in np.linspace(start=-1, stop=7, num=3)],
            'learning_rate': [0.001,0.01,0.2],
            'n_estimators': [int(x) for x in np.linspace(start=40, stop=120, num=40)]
        }
        gbm_grid = GridSearchCV(self.model, param_grid, cv=2)
        gbm_grid.fit(X.fillna(0), y.fillna(0))
        print('Best parameters found by grid search are:', gbm_grid.best_params_)
        best_params = gbm_grid.best_params_
        self.model.set_params(**best_params)
        return best_params

    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        self.model.fit(X_train, y_train, eval_set=[(X_val, y_val)], eval_metric=['l1', 'l2'], early_stopping_rounds=5,verbose=0)

    def predict(self, X_test):#, method = 'standard'):
        y_pred = self.model.predict(X_test)
        return y_pred

    def get_features_importance(self, features_names):#, method = 'standard'):
        run_importances = {}
        for (name, imp) in zip(features_names, self.model.feature_importances_):
            run_importances[name] = imp
        return run_importances

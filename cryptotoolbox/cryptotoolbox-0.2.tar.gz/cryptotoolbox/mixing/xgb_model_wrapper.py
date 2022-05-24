from cryptotoolbox.mixing import mixing_utility
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV

class XGBModel():
    def __init__(self):
       self.model = xgb.XGBRegressor()


    def calibrate(self, X, y):#, method = 'standard'):
        X = X.fillna(0)
        y = y.fillna(0)
        params = {
            "colsample_bytree": [0.7, 0.3],
            "gamma": [0, 0.5],
            "learning_rate": [0.03, 0.3],  # default 0.1
            "max_depth": [4],  # default 3
            "n_estimators": [120],  # default 100
            "subsample": [0.6, 0.4]
        }
        cv = 2
        n_iter = 50
        # cv=3
        # n_iter = 200
        search = RandomizedSearchCV(self.model, param_distributions=params, random_state=42, n_iter=n_iter, cv=cv,
                                    verbose=1, n_jobs=1, return_train_score=True)
        search.fit(X, y)
        best_params = search.best_params_
        self.model = xgb.XGBRegressor(colsample_bytree = best_params['colsample_bytree'], gamma = best_params['gamma'], learning_rate = best_params['learning_rate'],
                                      max_depth = best_params['max_depth'], n_estimators = best_params['n_estimators'], subsample = best_params['subsample'])

    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        X_train = X_train.fillna(0)
        y_val = y_val.fillna(0)
        self.model.fit(X_train, y_train, eval_set=[(X_val, y_val)], eval_metric=['rmse', 'logloss'],
                           early_stopping_rounds=5, verbose=0)


    def predict(self, X_test):#, method = 'standard'):
        X_test = X_test.fillna(0)
        y_pred = self.model.predict(X_test)
        return y_pred


    def get_features_importance(self, features_names):#, method = 'standard'):
        pass
        # run_importances = {}
        # if method == 'lgbm':
        #     for (name, imp) in zip(features_names, self.model.feature_importances_):
        #         run_importances[name] = imp
        # if method == 'standard':
        #     for (name, imp) in zip(features_names, self.model.coef_):
        #         run_importances[name] = imp
        # return run_importances

from cryptotoolbox.mixing import mixing_utility
from sklearn.linear_model import Lasso
from sklearn.model_selection import cross_val_score, GridSearchCV, KFold, RandomizedSearchCV, train_test_split


class LassoModel():

    def __init__(self):#, method = 'standard'):
        alpha = 0.0001
        self.model = Lasso(alpha=alpha, fit_intercept=False, max_iter=5000)        # """ Initialize shape of target. """

    def calibrate(self, X, y):#, method = 'standard'):

        param_grid = {
            'alpha': [0, 0.01, 0.1,0.5,1],
        }
        X = X.fillna(0)
        y = y.fillna(0)
        lasso_grid = GridSearchCV(self.model, param_grid, cv=2)
        lasso_grid.fit(X, y)
        # print('Best parameters found by grid search are:', lasso_grid.best_params_)
        best_params = lasso_grid.best_params_
        self.model = Lasso(alpha=best_params['alpha'], fit_intercept=False, max_iter=5000)


    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        X_train = X_train.fillna(0)
        y_train = y_train.fillna(0)
        # print(X_train, y_train)
        self.model.fit(X_train, y_train)

    def predict(self, X_test):#, method = 'standard'):
        X_test = X_test.fillna(0)
        y_pred = self.model.predict(X_test)
        # print(y_pred)
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

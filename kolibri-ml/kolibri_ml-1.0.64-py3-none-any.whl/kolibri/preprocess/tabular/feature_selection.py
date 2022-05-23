from kolibri.core.component import Component
from kolibri.config import TaskType
from sklearn.ensemble import RandomForestClassifier as rfc
from sklearn.ensemble import RandomForestRegressor as rfr
try:
    from lightgbm import LGBMClassifier as lgbmc
    from lightgbm import LGBMRegressor as lgbmr
except:
    pass


import numpy as np
import pandas as pd

# ______________________________________________________________________________________________________________________________________________________
# Feature Selection
class Advanced_Feature_Selection_Classic(Component):
    """
    - Selects important features and reduces the feature space. Feature selection is based on Random Forest , Light GBM and Correlation
    - to run on multiclass classification , set the subclass argument to 'multi'
  """

    defaults = {
        "fixed": {
            "task-type": TaskType.CLASSIFICATION,
            "top-features-to-pick": 0.10,
            "subclass": "ignore",
            "n_jobs": 1,
        }
    }

    def __init__(self, configs):
        super().__init__(configs)

        self.target = self.get_parameter("target")
        self.ml_usecase = self.get_parameter("task-type")
        self.top_features_to_pick = 1 - self.get_parameter("top-features-to-pick")
        self.random_state = self.get_parameter("random-state")
        self.subclass = self.get_parameter("subclass")
        self.n_jobs = self.get_parameter("n_jobs")

    def fit(self, dataset, y=None):
        self.fit_transform(dataset, y=y)
        return self

    def transform(self, dataset, y=None):
        # return the data with onlys specific columns
        data = dataset
        # self.selected_columns.remove(self.target)
        data = data[self.selected_columns_test]
        if self.target in dataset.columns:
            data[self.target] = dataset[self.target]
        return data

    def fit_transform(self, dataset, y=None):

        dummy_all = dataset.copy()
        dummy_all[self.target] = dummy_all[self.target].astype("float32")

        # Random Forest
        max_fe = min(70, int(np.sqrt(len(dummy_all.columns))))
        max_sa = min(1000, int(np.sqrt(len(dummy_all))))

        if self.ml_usecase == "classification":
            m = rfc(
                100,
                max_depth=5,
                max_features=max_fe,
                n_jobs=self.n_jobs,
                max_samples=max_sa,
                random_state=self.random_state,
            )
        else:
            m = rfr(
                100,
                max_depth=5,
                max_features=max_fe,
                n_jobs=self.n_jobs,
                max_samples=max_sa,
                random_state=self.random_state,
            )

        m.fit(dummy_all.drop(self.target, axis=1), dummy_all[self.target])
        # self.fe_imp_table= dsk.DataFrame(m.feature_importances_,columns=['Importance'],index=dummy_all.drop(self.target,axis=1).columns).sort_values(by='Importance',ascending= False)
        self.fe_imp_table = pd.DataFrame(
            m.feature_importances_,
            columns=["Importance"],
            index=dummy_all.drop(self.target, axis=1).columns,
        )
        self.fe_imp_table = self.fe_imp_table[
            self.fe_imp_table["Importance"]
            >= self.fe_imp_table.quantile(self.top_features_to_pick)[0]
            ]
        top = self.fe_imp_table.index
        dummy_all_columns_RF = dummy_all[top].columns

        # LightGBM
        max_fe = min(70, int(np.sqrt(len(dummy_all.columns))))
        max_sa = min(
            float(1000 / len(dummy_all)),
            float(np.sqrt(len(dummy_all) / len(dummy_all))),
        )

        if self.ml_usecase == "classification":
            m = lgbmc(
                n_estimators=100,
                max_depth=5,
                n_jobs=self.n_jobs,
                subsample=max_sa,
                random_state=self.random_state,
            )
        else:
            m = lgbmr(
                n_estimators=100,
                max_depth=5,
                n_jobs=self.n_jobs,
                subsample=max_sa,
                random_state=self.random_state,
            )
        m.fit(dummy_all.drop(self.target, axis=1), dummy_all[self.target])
        # self.fe_imp_table= dsk.DataFrame(m.feature_importances_,columns=['Importance'],index=dummy_all.drop(self.target,axis=1).columns).sort_values(by='Importance',ascending= False)
        self.fe_imp_table = pd.DataFrame(
            m.feature_importances_,
            columns=["Importance"],
            index=dummy_all.drop(self.target, axis=1).columns,
        )
        self.fe_imp_table = self.fe_imp_table[
            self.fe_imp_table["Importance"]
            >= self.fe_imp_table.quantile(self.top_features_to_pick)[0]
            ]
        top = self.fe_imp_table.index
        dummy_all_columns_LGBM = dummy_all[top].columns

        # we can now select top correlated feature
        if self.subclass != "multi":
            corr = pd.DataFrame(np.corrcoef(dummy_all.T))
            corr.columns = dummy_all.columns
            corr.index = dummy_all.columns
            # corr = corr[self.target].abs().sort_values(ascending=False)[0:self.top_features_to_pick+1]
            corr = corr[self.target].abs()
            corr = corr[corr.index != self.target]  # drop the target column
            corr = corr[corr >= corr.quantile(self.top_features_to_pick)]
            corr = pd.DataFrame(dict(features=corr.index, value=corr)).reset_index(
                drop=True
            )
            corr = corr.drop_duplicates(subset="value")
            corr = corr["features"]
            # corr = dsk.DataFrame(dict(features=corr.index,value=corr)).reset_index(drop=True)
            # corr = corr.drop_duplicates(subset='value')[0:self.top_features_to_pick+1]
            # corr = corr['features']
        else:
            corr = list()

        self.dummy_all_columns_RF = dummy_all_columns_RF
        self.dummy_all_columns_LGBM = dummy_all_columns_LGBM
        self.corr = corr

        self.selected_columns = list(
            set(
                [self.target]
                + list(dummy_all_columns_RF)
                + list(corr)
                + list(dummy_all_columns_LGBM)
            )
        )

        self.selected_columns_test = (
            dataset[self.selected_columns].drop(self.target, axis=1).columns
        )
        return dataset[self.selected_columns]


# _

# ______________________________________________________________________________________________________________________________________________________
# Boruta Feature Selection algorithm
# Base on: https://github.com/scikit-learn-contrib/boruta_py/blob/master/boruta/boruta_py.py
class Boruta_Feature_Selection(Component):
    """
          Boruta selection algorithm based on borutaPy sklearn-contrib and
          Miron B Kursa, https://m2.icm.edu.pl/boruta/
          Selects the most important features.
            Args:
              target (str): target column name
              ml_task (str): case: classification or regression
              top_features_to_pick: to make...
              max_iteration {int): overall iterations of shuffle and train forests
              alpha {float): p-value on which
              the option to favour one measur to another. e.g. if value is .6 , during feature selection tug of war, correlation target measure will have a higher say.
              A value of .5 means both measure have equal say
  """
    defaults = {
        "fixed":{

            "task-type": TaskType.CLASSIFICATION,
            "top-features-to-pick": 1.0,
            "max-iteration" : 200,
            "n-iter-no-change" : 25,
            "alpha" : 0.05,
            "subclass" : "ignore",
            "n_jobs" : 1,
        }
    }

    def __init__(self, configs):
        super().__init__(configs)
        self.target = self.get_parameter("target")
        self.ml_usecase = self.get_parameter("task-type")
        self.top_features_to_pick = self.get_parameter("top-features-to-pick")
        self.random_state = self.get_parameter("random-state")
        self.subclass = self.get_parameter("subclass")
        self.max_iteration = self.get_parameter("max-iteration")
        self.n_iter_no_change = self.get_parameter("n-iter-no-change")
        self.alpha = self.get_parameter("alpha")
        self.selected_columns_test = []
        self.n_jobs = self.get_parameter("n_jobs")

    @property
    def selected_columns(self):
        return self.selected_columns_test + [self.target]

    def fit(self, dataset, y=None):
        from .boruta_py import BorutaPyPatched

        dummy_data = dataset
        X, y = dummy_data.drop(self.target, axis=1), dummy_data[self.target].values
        y = y.astype("float32")
        X_cols = X.columns
        X = X.values

        if self.ml_usecase == "classification":
            m = rfc(
                100,
                max_depth=5,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                class_weight="balanced",
            )
        else:
            m = rfr(
                100, max_depth=5, n_jobs=self.n_jobs, random_state=self.random_state,
            )

        feat_selector = BorutaPyPatched(
            m,
            n_estimators="auto",
            perc=int(self.top_features_to_pick * 100),
            max_iter=self.max_iteration,
            random_state=self.random_state,
            early_stopping=(self.n_iter_no_change > 0),
            n_iter_no_change=self.n_iter_no_change,
        )

        try:
            feat_selector.fit(X, y)
            self.selected_columns_test = list(X_cols[feat_selector.support_])
        except:
            # boruta may errors out if all features are selected
            self.selected_columns_test = list(X_cols)

        return self

    def transform(self, dataset, y=None):
        if self.target in dataset.columns:
            return dataset[self.selected_columns]
        else:
            return dataset[self.selected_columns_test]

    def fit_transform(self, dataset, y=None):
        self.fit(dataset, y=y)
        return self.transform(dataset, y=y)

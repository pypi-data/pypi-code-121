from kolibri.core.component import Component
from kolibri.config import TaskType
import numpy as np
import pandas as pd
from kolibri.preprocess.tabular.feature_selection import Advanced_Feature_Selection_Classic

# _______________________________________________________________________________________________________________________________________________________________________________________________
# custome DFS
class DFS_Classic(Component):
    """
    - Automated feature interactions using multiplication, division , addition & substraction
    - Only accepts numeric / One Hot Encoded features
    - Takes DF, return same DF
    - for Multiclass classification problem , set subclass arg as 'multi'
  """

    defaults = {
        "fixed":{
            "task-type": TaskType.CLASSIFICATION,
            "interactions": ["multiply", "divide", "add", "subtract"],
            "top-features-to-pick-percentage" : 0.05,
             "subclass": "ignore",
             "n_jobs" : 1,
        }
    }

    def __init__(self, configs):
        super().__init__(configs)
        self.target = self.get_parameter("target")
        self.interactions = self.get_parameter("interactions")
        self.top_n_correlated = self.get_parameter("top-features-to-pick-percentage")  # (this will be 1- top_features , but handled in the Advance_feature_selection )
        self.ml_usecase = self.get_parameter("task-type")
        self.random_state =self.get_parameter ("random-state")
        self.subclass = self.get_parameter("subclass")
        self.n_jobs = self.get_parameter("n_jobs")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):

        data = dataset

        data_without_target = data.drop(self.target, axis=1, errors="ignore")
        # for multiplication:
        # we need bot catagorical and numerical columns

        if "multiply" in self.interactions:

            data_multiply = pd.concat(
                [
                    data_without_target.mul(col[1], axis="index")
                    for col in data_without_target.iteritems()
                ],
                axis=1,
            )
            data_multiply.columns = [
                "_multiply_".join([i, j])
                for j in data_without_target.columns
                for i in data_without_target.columns
            ]
            # we dont need to apply rest of conditions
            data_multiply.index = data.index
        else:
            data_multiply = pd.DataFrame()

        # for division, we only want it to apply to numerical columns
        if "divide" in self.interactions:

            data_divide = pd.concat(
                [
                    data_without_target[self.numeric_columns].div(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_divide.columns = [
                "_divide_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            data_divide.replace([np.inf, -np.inf], 0, inplace=True)
            data_divide.fillna(0, inplace=True)
            data_divide.index = data.index
        else:
            data_divide = pd.DataFrame()

        # for addition, we only want it to apply to numerical columns
        if "add" in self.interactions:

            data_add = pd.concat(
                [
                    data_without_target[self.numeric_columns].add(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_add.columns = [
                "_add_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            data_add.index = data.index
        else:
            data_add = pd.DataFrame()

        # for substraction, we only want it to apply to numerical columns
        if "subtract" in self.interactions:

            data_substract = pd.concat(
                [
                    data_without_target[self.numeric_columns].sub(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_substract.columns = [
                "_subtract_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            data_substract.index = data.index
        else:
            data_substract = pd.DataFrame()

        # get all the dummy data combined
        dummy_all = pd.concat(
            (data, data_multiply, data_divide, data_add, data_substract), axis=1
        )
        del data_multiply
        del data_divide
        del data_add
        del data_substract
        # now only return the columns we want:
        dummy_all = dummy_all[self.columns_to_keep]
        if self.target in dataset.columns:
            dummy_all[self.target] = dataset[self.target]
        return dummy_all

    def fit_transform(self, dataset, y=None):

        data = dataset

        data_without_target = data.drop(self.target, axis=1, errors="ignore")

        # we need to seperate numerical and ont hot encoded columns
        # self.ohe_columns = [i if ((len(data[i].unique())==2) & (data[i].unique()[0] in [0,1]) & (data[i].unique()[1] in [0,1]) ) else None for i in data.drop(self.target,axis=1).columns]
        self.ohe_columns = [
            i
            for i in data.columns
            if data[i].nunique() == 2
            and data[i].unique()[0] in [0, 1]
            and data[i].unique()[1] in [0, 1]
        ]
        # self.ohe_columns = [i for i in self.ohe_columns if i is not None]
        self.numeric_columns = [
            i for i in data_without_target.columns if i not in self.ohe_columns
        ]
        target_variable = data[[self.target]]

        # for multiplication:
        # we need bot catagorical and numerical columns

        if "multiply" in self.interactions:
            data_multiply = pd.concat(
                [
                    data_without_target.mul(col[1], axis="index")
                    for col in data_without_target.iteritems()
                ],
                axis=1,
            )
            data_multiply.columns = [
                "_multiply_".join([i, j])
                for j in data_without_target.columns
                for i in data_without_target.columns
            ]
            # we dont need columns that are self interacted
            col = [
                "_multiply_".join([i, j])
                for j in data_without_target.columns
                for i in data_without_target.columns
                if i != j
            ]
            data_multiply = data_multiply[col]
            # we dont need columns where the sum of the total column is null (to catagorical variables never happening togather)
            col1 = [
                i for i in data_multiply.columns if np.nansum(data_multiply[i]) != 0
            ]
            data_multiply = data_multiply[col1]
            data_multiply.index = data.index
        else:
            data_multiply = pd.DataFrame()

        # for division, we only want it to apply to numerical columns
        if "divide" in self.interactions:
            data_divide = pd.concat(
                [
                    data_without_target[self.numeric_columns].div(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_divide.columns = [
                "_divide_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            # we dont need columns that are self interacted
            col = [
                "_divide_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
                if i != j
            ]
            data_divide = data_divide[col]
            # we dont need columns where the sum of the total column is null (to catagorical variables never happening togather)
            col1 = [i for i in data_divide.columns if np.nansum(data_divide[i]) != 0]
            data_divide = data_divide[col1]
            # additionally we need to fill anll the possible NaNs
            data_divide.replace([np.inf, -np.inf], 0, inplace=True)
            data_divide.fillna(0, inplace=True)
            data_divide.index = data.index
        else:
            data_divide = pd.DataFrame()

        # for addition, we only want it to apply to numerical columns
        if "add" in self.interactions:
            data_add = pd.concat(
                [
                    data_without_target[self.numeric_columns].add(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_add.columns = [
                "_add_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            # we dont need columns that are self interacted
            col = [
                "_add_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
                if i != j
            ]
            data_add = data_add[col]
            # we dont need columns where the sum of the total column is null (to catagorical variables never happening togather)
            col1 = [i for i in data_add.columns if np.nansum(data_add[i]) != 0]
            data_add = data_add[col1]
            data_add.index = data.index
        else:
            data_add = pd.DataFrame()

        # for substraction, we only want it to apply to numerical columns
        if "subtract" in self.interactions:
            data_substract = pd.concat(
                [
                    data_without_target[self.numeric_columns].sub(col[1], axis="index")
                    for col in data_without_target[self.numeric_columns].iteritems()
                ],
                axis=1,
            )
            data_substract.columns = [
                "_subtract_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
            ]
            # we dont need columns that are self interacted
            col = [
                "_subtract_".join([i, j])
                for j in data_without_target[self.numeric_columns].columns
                for i in data_without_target[self.numeric_columns].columns
                if i != j
            ]
            data_substract = data_substract[col]
            # we dont need columns where the sum of the total column is null (to catagorical variables never happening togather)
            col1 = [
                i for i in data_substract.columns if np.nansum(data_substract[i]) != 0
            ]
            data_substract = data_substract[col1]
            data_substract.index = data.index
        else:
            data_substract = pd.DataFrame()

        # get all the dummy data combined
        dummy_all = pd.concat(
            (data_multiply, data_divide, data_add, data_substract), axis=1
        )
        del data_multiply
        del data_divide
        del data_add
        del data_substract

        dummy_all[self.target] = target_variable
        self.dummy_all = dummy_all

        # apply advanced feature selectio
        afs = Advanced_Feature_Selection_Classic(
            target=self.target,
            ml_usecase=self.ml_usecase,
            top_features_to_pick=self.top_n_correlated,
            random_state=self.random_state,
            subclass=self.subclass,
            n_jobs=self.n_jobs,
        )
        dummy_all_t = afs.fit_transform(dummy_all)

        data_fe_final = pd.concat(
            (data, dummy_all_t), axis=1
        )  # self.data_fe[self.corr]
        # # making sure no duplicated columns are there
        data_fe_final = data_fe_final.loc[
            :, ~data_fe_final.columns.duplicated()
        ]  # new added
        # # remove thetarget column
        # # this is the final data we want that includes original , fe data plus impact of top n correlated
        self.columns_to_keep = data_fe_final.drop(self.target, axis=1).columns
        del dummy_all
        del dummy_all_t

        return data_fe_final

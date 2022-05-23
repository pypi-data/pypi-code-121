from kolibri.core.component import Component
import numpy as np
import pandas as pd


from sklearn.preprocessing import OneHotEncoder

# make dummy variables
class DummyConverter(Component):

    def __init__(self, config={}):
        super().__init__(config)
        self.target = self.get_parameter("target")

        # create one_hot object
        self.one_hot = OneHotEncoder(handle_unknown="ignore", dtype=np.float32)

    def fit(self, dataset, y=None):
        data = dataset
        # if there are categorical variables
        if len(data.select_dtypes(include=("object")).columns) > 0:
            if self.target is not None:
                self.non_categorical_data = data.drop(self.target, axis=1, errors="ignore").select_dtypes(exclude=("object"))
                if self.target in data.columns.values:
                    self.target_column = data[self.target]
                #categorical columns
                categorical_data = data.drop(self.target, axis=1, errors="ignore").select_dtypes(include=("object"))
            else:
                self.non_categorical_data = data.select_dtypes(exclude=("object"))
                self.target_column = None
                #categorical columns
                categorical_data = data.select_dtypes(include=("object"))

            self.one_hot.fit(categorical_data)
            self.data_columns = self.one_hot.get_feature_names(categorical_data.columns)

        return self

    def transform(self, data, y=None):

        if len(data.select_dtypes(include=("object")).columns) > 0:
            if self.target is not None:
                self.non_categorical_data = data.drop(self.target, axis=1, errors="ignore").select_dtypes(exclude=("object"))
                # fit without target and only categorical columns
                array = self.one_hot.transform(
                    data.drop(self.target, axis=1, errors="ignore").select_dtypes(
                        include=("object")
                    )
                ).toarray()
            else:
                self.non_categorical_data = data.select_dtypes(exclude=("object"))
                # fit without target and only categorical columns
                array = self.one_hot.transform(data.select_dtypes(include=("object"))).toarray()

            data_dummies = pd.DataFrame(array, columns=self.data_columns)
            data_dummies.index = self.non_categorical_data.index
            if self.target in data.columns:
                target_column = data[[self.target]]
            else:
                target_column = None
            data = pd.concat((target_column, self.non_categorical_data, data_dummies), axis=1)
            del self.non_categorical_data
            return data
        else:
            return data

    def fit_transform(self, data, y=None):
        return self.fit(data, y).transform(data, y)


from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(DummyConverter.name, DummyConverter)
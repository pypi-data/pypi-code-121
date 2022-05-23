from kolibri.core.component import Component
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import numpy as np


class Ordinal(Component):
    """
    - converts categorical features into ordinal values
    - takes a dataframe , and information about column names and ordered categories as dict
    - returns float panda data frame
  """


    def __init__(self, params):

        super().__init__(params)


    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        new_data_test = pd.DataFrame(
            self.enc.transform(data[self.info_as_dict.keys()]),
            columns=self.info_as_dict.keys(),
            index=data.index,
        )
        for i in self.info_as_dict.keys():
            data[i] = new_data_test[i]
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        # creat categories from given keys in the data set
        cat_list = []
        for i in self.info_as_dict.values():
            i = [np.array(i)]
            cat_list = cat_list + i

        # now do fit transform
        self.enc = OrdinalEncoder(categories=cat_list)
        new_data_train = pd.DataFrame(
            self.enc.fit_transform(data.loc[:, self.info_as_dict.keys()]),
            columns=self.info_as_dict,
            index=data.index,
        )
        # new_data = dsk.DataFrame(self.enc.fit_transform(data.loc[:,self.info_as_dict.keys()]))
        for i in self.info_as_dict.keys():
            data[i] = new_data_train[i]

        return data

from kolibri.core.component import Component
import pandas as pd
import numpy as np
from sklearn.preprocessing import KBinsDiscretizer





# Binning for Continious
class Binning(Component):
    """
    - Converts numerical variables to catagorical variable through binning
    - Number of binns are automitically determined through Sturges method
    - Once discretize, original feature will be dropped
        Args:
            features_to_discretize: list of featur names to be binned

  """

    defaults = {
        "fixed":{
            "features-to-discretize":None
        }
    }

    def __init__(self, configs):
        super().__init__(configs)
        self.features_to_discretize =  self.get_parameter("features-to-discretize")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        # only do if features are provided
        if len(self.features_to_discretize) > 0:
            data_t = self.disc.transform(
                np.array(data[self.features_to_discretize]).reshape(
                    -1, self.len_columns
                )
            )
            # make pandas data frame
            data_t = pd.DataFrame(
                data_t, columns=self.features_to_discretize, index=data.index
            )
            # all these columns are catagorical
            data_t = data_t.astype(str)
            # drop original columns
            data.drop(self.features_to_discretize, axis=1, inplace=True)
            # add newly created columns
            data = pd.concat((data, data_t), axis=1)
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        # only do if features are given

        if len(self.features_to_discretize) > 0:

            # place holder for all the features for their binns
            self.binns = []
            for i in self.features_to_discretize:
                # get numbr of binns
                hist, _ = np.histogram(data[i], bins="sturges")
                self.binns.append(len(hist))

            # how many colums to deal with
            self.len_columns = len(self.features_to_discretize)
            # now do fit transform
            self.disc = KBinsDiscretizer(
                n_bins=self.binns, encode="ordinal", strategy="kmeans"
            )
            data_t = self.disc.fit_transform(
                np.array(data[self.features_to_discretize]).reshape(
                    -1, self.len_columns
                )
            )
            # make pandas data frame
            data_t = pd.DataFrame(
                data_t, columns=self.features_to_discretize, index=data.index
            )
            # all these columns are catagorical
            data_t = data_t.astype(str)
            # drop original columns
            data.drop(self.features_to_discretize, axis=1, inplace=True)
            # add newly created columns
            data = pd.concat((data, data_t), axis=1)

        return data
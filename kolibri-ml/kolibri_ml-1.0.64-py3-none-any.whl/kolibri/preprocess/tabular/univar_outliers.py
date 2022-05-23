import numpy as np

from kolibri.core.component import Component
from kdmt.outliers import z_score_method, mad_method, tukeys_method
from kolibri.utils.common import intersect
class UnivarOutlier(Component):
    """
    - Removes outlier using ABOD,KNN,IFO,PCA & HOBS using hard voting
    - Only takes numerical / One Hot Encoded features
  """

    defaults = {
        "fixed":{
            "methods":["z-score", "mad", "tukeys"],
            "ignore-columns": [],
            "include-columns": [],
            "impute-value":np.nan,
            "threshold":6
        }
    }
    def __init__(self, params):
        super().__init__(params)
        self.target = self.get_parameter("target")
        self.random_state = self.get_parameter("random-state")
        self.methods = self.get_parameter("methods")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, data, y=None):
        return data

    def fit_transform(self, dataset, y=None):
        columns=[c for c, col in enumerate(dataset.columns) if col in self.get_parameter("include-columns") and col not in self.get_parameter("ignore-columns")]
        for col in columns:
            outliers=[]
            if "z-score" in self.methods:
                outliers.append(z_score_method(dataset, dataset.columns[col],self.get_parameter("threshold")))

            if "mad" in self.methods:
                outliers.append(mad_method(dataset, dataset.columns[col], self.get_parameter("threshold")))

            if "tukeys" in self.methods:
                outliers.append(tukeys_method(dataset, dataset.columns[col])[0])
            outliers_index=intersect(outliers)

            dataset.iloc[list(outliers_index), col ]=self.get_parameter("impute-value")

        return dataset


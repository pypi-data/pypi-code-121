from kolibri.core.component import Component
import pandas as pd

class NearZeroVariance(Component):
    """
    - Algorithm for detecting near zero variance:
      -1) the Count of unique values divided by the size of the feature has to be lower than a pre sepcified threshold
      -2) Most common point(count) divided by the second most common point(count) in the feature is greater than a pre specified threshold
      Once both conditions are met , the feature is dropped
    -Ignores target variable

      Args:
        threshold_1: float (between 0.0 to 1.0) , default is .10
        threshold_2: int (between 1 to 100), default is 20
        tatget variable : string, name of the target variable

  """
    defaults={
        "fixed": {
            "threshold-1": 0.1,
            "threshold-2" : 20,
            "None-ratio-cutoff":0.85,
            "ignore-columns": []
        },
        "tunable":
            {
                "features-todrop": {
                    "value":[]
                }
            }
    }

    def __init__(self, configs={}):
        super().__init__(configs)
        self.threshold_1 = self.get_parameter("threshold-1")
        self.threshold_2 = self.get_parameter("threshold-2")
        self.target=self.get_parameter("target")
        self.none_ratio=self.get_parameter("None-ratio-cutoff")
        self.columns_to_ignore=self.get_parameter("ignore-columns")

    def fit(
            self, data, y=None
    ):  # from training data set we are going to learn what columns to drop
        self.to_drop = []
        sampl_len = len(data)
        self.to_drop=[i for i in data.columns if data[i].isnull().sum() > 0.85 * len(data)]
        self.to_drop.extend(self.get_parameter("features-todrop"))
        self.to_drop=list(set(self.to_drop))

        columns=[c for c in data.columns if c !=self.target or c not in self.to_drop]

        for i in columns:
            # get the number of unique counts
            u = pd.DataFrame(data[i].value_counts()).sort_values(
                by=i, ascending=False, inplace=False
            )
            # take len of u and divided it by the total sample numbers, so this will check the 1st rule , has to be low say 10%
            # import pdb; pdb.set_trace()
            if len(u)==0:
                self.to_drop.append(i)
                continue
            first = len(u) / sampl_len
            # then check if most common divided by 2nd most common ratio is 20 or more
            if (
                    len(u[i]) == 1
            ):  # this means that if column is non variance , automatically make the number big to drop it
                second = 100
            else:
                second = u.iloc[0, 0] / u.iloc[1, 0]
            # if both conditions are true then drop the column, however, we dont want to alter column that indicate NA's
            if (first <= 0.10) and (second >= 20) and (i[-10:] != "_surrogate"):
                self.to_drop.append(i)
            # now drop if the column has zero variance
            if (second == 100) and (i[-10:] != "_surrogate"):
                self.to_drop.append(i)
        self.to_drop=list(set([c for c in self.to_drop if c not in self.columns_to_ignore]))

    def transform(
            self, dataset, y=None
    ):  # since it is only for training data set , nothing here
        data = dataset.drop(self.to_drop, axis=1)
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        self.fit(data)
        return self.transform(data)

from kolibri.core.component import Component
import pandas as pd
import numpy as np




# rare catagorical variables
class Catagorical_variables_With_Rare_levels(Component):
    """
    -Merges levels in catagorical features with more frequent level  if they appear less than a threshold count
      e.g. Col=[a,a,a,a,b,b,c,c]
      if threshold is set to 2 , then c will be mrged with b because both are below threshold
      There has to be atleast two levels belwo threshold for this to work
      the process will keep going until all the levels have atleast 2(threshold) counts
    -Only handles catagorical features
    -It is recommended to run the Zroe_NearZero_Variance and Define_dataTypes first
    -Ignores target variable
      Args:
        threshold: int , default 10
        target: string , name of the target variable
        new_level_name: string , name given to the new level generated, default 'others'

  """

    defaults ={
        "fixed":{
            "new-level-name": "_OTHER_",
            "rare-level-threshold": 0.05
        }
    }
    def __init__(self, params):

        super().__init__(params)
        self.threshold = self.get_parameter("rare-level-threshold")
        self.target = self.get_parameter("target")
        self.new_level_name = self.get_parameter("new-level-name")

    def fit(
        self, dataset, y=None
    ):  # we will learn for what columnns what are the level to merge as others
        # every level of the catagorical feature has to be more than threshols, if not they will be clubed togather as "others"
        # in order to apply, there should be atleast two levels belwo the threshold !
        # creat a place holder
        data = dataset
        self.ph = pd.DataFrame(
            columns=data.drop(self.target, axis=1)
            .select_dtypes(include="object")
            .columns
        )
        # ph.columns = df.columns# catagorical only
        for i in data[self.ph.columns].columns:
            # determine the infrequebt count
            v_c = data[i].value_counts()
            count_th = round(v_c.quantile(self.threshold))
            a = np.sum(
                pd.DataFrame(data[i].value_counts().sort_values())[i] <= count_th
            )
            if a >= 2:  # rare levels has to be atleast two
                count = pd.DataFrame(data[i].value_counts().sort_values())
                count.columns = ["fre"]
                count = count[count["fre"] <= count_th]
                to_club = list(count.index)
                self.ph.loc[0, i] = to_club
            else:
                self.ph.loc[0, i] = []
        # # also need to make a place holder that keep records of all the levels , and in case a new level appears in test we will change it to others
        # self.ph_level = dsk.DataFrame(columns=data.drop(self.target,axis=1).select_dtypes(include="object").columns)
        # for i in self.ph_level.columns:
        #   self.ph_level.loc[0,i] = list(data[i].value_counts().sort_values().index)

    def transform(self, dataset, y=None):  #
        # transorm
        data = dataset
        for i in data[self.ph.columns].columns:
            t_replace = self.ph.loc[0, i]
            data[i].replace(
                to_replace=t_replace, value=self.new_level_name, inplace=True
            )
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        self.fit(data)
        return self.transform(data)
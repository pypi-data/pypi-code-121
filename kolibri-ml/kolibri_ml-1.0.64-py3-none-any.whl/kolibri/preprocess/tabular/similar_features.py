from kolibri.core.component import Component
from scipy import stats
import numpy as np



class Group_Similar_Features(Component):
    """
    - Given a list of features , it creates aggregate features
    - features created are Min, Max, Mean, Median, Mode & Std
    - Only works on numerical features
      Args:
        list_of_similar_features: list of list, string , e.g. [['col',col2],['col3','col4']]
        group_name: list, group name/names to be added as prefix to aggregate features, e.g ['gorup1','group2']
  """

    defaults = {
        "fixed":{
            "group-name": [],
            "list-of-grouped-features": [[]]
        }
    }
    def __init__(self, params):
        super().__init__(params)
        self.list_of_similar_features = self.get_parameter("list-of-grouped-features")
        self.group_name = self.get_parameter("group-name")
        # if list of list not given
        try:
            np.array(self.list_of_similar_features).shape[0]
        except:
            raise (
                "Group_Similar_Features: list_of_grouped_features is not provided as list of list"
            )

    def fit(self, data, y=None):
        # nothing to learn
        return self

    def transform(self, dataset, y=None):
        data = dataset
        # # only going to process if there is an actual missing value in training data set
        if len(self.list_of_similar_features) > 0:
            for f, g in zip(self.list_of_similar_features, self.group_name):
                data[g + "_Min"] = data[f].apply(np.min, 1)
                data[g + "_Max"] = data[f].apply(np.max, 1)
                data[g + "_Mean"] = data[f].apply(np.mean, 1)
                data[g + "_Median"] = data[f].apply(np.median, 1)
                data[g + "_Mode"] = stats.mode(data[f], 1)[0]
                data[g + "_Std"] = data[f].apply(np.std, 1)

            return data
        else:
            return data

    def fit_transform(self, data, y=None):
        return self.transform(data)

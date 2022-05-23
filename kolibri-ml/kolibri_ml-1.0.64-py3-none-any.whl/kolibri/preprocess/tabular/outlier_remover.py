from kolibri.core.component import Component
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
try:
    from pyod.models.knn import KNN
    from pyod.models.iforest import IForest
    from pyod.models.pca import PCA
except:
    pass

class Outlier(Component):
    """
    - Removes outlier using ABOD,KNN,IFO,PCA & HOBS using hard voting
    - Only takes numerical / One Hot Encoded features
  """

    defaults = {
        "fixed":{
            "contamination": 0.20,
            "methods":["knn", "iso", "pca"]
        }
    }
    def __init__(self, params):
        super().__init__(params)
        self.target = self.get_parameter("target")
        self.contamination = self.get_parameter("contamination")
        self.random_state = self.get_parameter("random-state")
        self.methods = self.get_parameter("methods")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, data, y=None):
        return data

    def fit_transform(self, dataset, y=None):

        # dummify if there are any obects
        if len(dataset.select_dtypes(include="object").columns) > 0:
            self.dummy = DummyConverter()
            data = self.dummy.fit_transform(dataset)
        else:
            data = dataset

        data_without_target = data.drop(self.target, axis=1)

        if "knn" in self.methods:
            self.knn = KNN(contamination=self.contamination)
            self.knn.fit(data_without_target)
            knn_predict = self.knn.predict(data_without_target)
            data_without_target["knn"] = knn_predict

        if "iso" in self.methods:
            self.iso = IForest(
                contamination=self.contamination,
                random_state=self.random_state,
                behaviour="new",
            )
            self.iso.fit(data_without_target)
            iso_predict = self.iso.predict(data_without_target)
            data_without_target["iso"] = iso_predict

        if "pca" in self.methods:
            self.pca = PCA(
                contamination=self.contamination, random_state=self.random_state
            )
            self.pca.fit(data_without_target)
            pca_predict = self.pca.predict(data_without_target)
            data_without_target["pca"] = pca_predict

        data_without_target["vote_outlier"] = data_without_target[self.methods].sum(
            axis=1
        )
        self.outliers = data_without_target[
            data_without_target["vote_outlier"] == len(self.methods)
        ].index

        return dataset[~dataset.index.isin(self.outliers)]


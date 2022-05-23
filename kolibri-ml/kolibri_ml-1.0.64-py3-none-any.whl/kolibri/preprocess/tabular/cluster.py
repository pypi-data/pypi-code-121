
from kolibri.core.component import Component
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
import pandas as pd
import numpy as np
from sklearn import cluster
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler


# __________________________________________________________________________________________________________________________________________________________________________
# Clustering entire data
class ClusterDataset(Component):
    """
    - Applies kmeans clustering to the entire data set and produce clusters
    - Highly recommended to run the DataTypes_Auto_infer class first
      Args:
          target_variable: target variable (integer or numerical only)
          check_clusters_upto: to determine optimum number of kmeans clusters, set the uppler limit of clusters
  """

    defaults = {
        "fixed":{
            "check_clusters_upto": 20
        }
    }
    def __init__(self, configs):
        super().__init__(configs)
        self.target = self.get_parameter("target")
        self.check_clusters = self.get_parameter("check_clusters_upto") + 1
        self.random_state = self.get_parameter("random-state")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        data = data.drop(self.target, axis=1, errors="ignore")
        # first convert to dummy
        if len(data.select_dtypes(include="object").columns) > 0:
            data_t1 = self.dummy.transform(data)
        else:
            data_t1 = data

        # # # now make PLS
        # # data_t1 = self.pls.transform(data_t1)
        # # data_t1 = self.pca.transform(data_t1)
        # # now predict with the clustes
        predict = pd.DataFrame(self.k_object.predict(data_t1), index=data.index)
        data["data_cluster"] = predict
        data["data_cluster"] = data["data_cluster"].astype("object")
        if self.target in dataset.columns:
            data[self.target] = dataset[self.target]
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset.copy()
        # first convert to dummy (if there are objects in data set)
        if len(data.select_dtypes(include="object").columns) > 0:
            self.dummy = DummyConverter()
            data_t1 = self.dummy.fit_transform(data)
            data_t1 = data_t1.drop(self.target, axis=1)
        else:
            data_t1 = data.drop(self.target, axis=1)

        # now make PLS
        # self.pls = PLSRegression(n_components=len(data_t1.columns)-1)
        # data_t1 = self.pls.fit_transform(data_t1.drop(self.target,axis=1),data_t1[self.target])[0]
        # self.pca = PCA(n_components=len(data_t1.columns)-1)
        # data_t1 = self.pca.fit_transform(data_t1.drop(self.target,axis=1))

        # we are goign to make a place holder , for 2 to 20 clusters
        self.ph = pd.DataFrame(
            np.arange(2, self.check_clusters, 1), columns=["clusters"]
        )
        self.ph["Silhouette"] = float(0)
        self.ph["calinski"] = float(0)

        # Now start making clusters
        for k in self.ph.index:
            c = self.ph["clusters"][k]
            self.k_object = cluster.KMeans(
                n_clusters=c,
                init="k-means++",
                precompute_distances="auto",
                n_init=10,
                random_state=self.random_state,
            )
            self.k_object.fit(data_t1)
            self.ph.iloc[k, 1] = metrics.silhouette_score(
                data_t1, self.k_object.labels_
            )
            self.ph.iloc[k, 2] = metrics.calinski_harabasz_score(
                data_t1, self.k_object.labels_
            )

        # now standardize the scores and make a total column
        m = MinMaxScaler((-1, 1))
        self.ph["calinski"] = m.fit_transform(
            np.array(self.ph["calinski"]).reshape(-1, 1)
        )
        self.ph["Silhouette"] = m.fit_transform(
            np.array(self.ph["Silhouette"]).reshape(-1, 1)
        )
        self.ph["total"] = self.ph["Silhouette"] + self.ph["calinski"]
        # sort it by total column and take the first row column 0 , that would represent the optimal clusters
        try:
            self.clusters = int(
                self.ph[self.ph["total"] == max(self.ph["total"])]["clusters"]
            )
        except:  # in case there isnt a decisive measure , take calinski as yeard stick
            self.clusters = int(
                self.ph[self.ph["calinski"] == max(self.ph["calinski"])]["clusters"]
            )
        # Now make the final cluster object
        self.k_object = cluster.KMeans(
            n_clusters=self.clusters,
            init="k-means++",
            precompute_distances="auto",
            n_init=10,
            random_state=self.random_state,
        )
        # now do fit predict
        predict = pd.DataFrame(self.k_object.fit_predict(data_t1), index=data.index)
        data["data_cluster"] = predict
        data["data_cluster"] = data["data_cluster"].astype("object")

        if self.target in dataset.columns:
            data[self.target] = dataset[self.target]

        return data


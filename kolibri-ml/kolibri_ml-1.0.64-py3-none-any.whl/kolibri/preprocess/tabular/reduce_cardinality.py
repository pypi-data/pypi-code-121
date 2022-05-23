from kolibri.core.component import Component
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
from sklearn.cross_decomposition import PLSRegression
import pandas as pd
import numpy as np
from sklearn import cluster
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler

# __________________________________________________________________________________________________________________________________________
# Clustering catagorical data
class Reduce_Cardinality_with_Clustering(Component):
    """
    - Reduces the level of catagorical column / cardinality through clustering
    - Highly recommended to run the DataTypes_Auto_infer class first
      Args:
          target_variable: target variable (integer or numerical only)
          catagorical_feature: list of features on which clustering  is to be applied / cardinality to be reduced
          check_clusters_upto: to determine optimum number of kmeans clusters, set the uppler limit of clusters
  """

    defaults = {
        "fixed":{
            "catagorical-feature" : [],
            "check_clusters_upto" : 30,
        }
    }

    def __init__(self, configs):

        super().__init__(configs)
        self.target = self.get_parameter("target")
        self.feature = self.get_parameter("catagorical-feature")
        self.check_clusters =self.get_parameter ("check_clusters_upto") + 1
        self.random = self.get_parameter("random-state")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        # we already know which leval belongs to whihc cluster , so all w need is to replace levels with clusters we already have from training data set
        for i, z in zip(self.feature, self.ph_data):
            data[i] = data[i].replace(list(z["levels"]), z["cluster"])
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset.copy()
        # first convert to dummy
        if len(data.select_dtypes(include="object").columns) > 0:
            self.dummy = DummyConverter()
            data_t = self.dummy.fit_transform(data.drop(self.feature, axis=1))
            # data_t1 = data_t1.drop(self.target,axis=1)
        else:
            data_t = data.drop(self.feature, axis=1)

        # now make PLS
        self.pls = PLSRegression(
            n_components=2
        )  # since we are only using two componenets to group #PLSRegression(n_components=len(data_t1.columns)-1)
        data_pls = self.pls.fit_transform(
            data_t.drop(self.target, axis=1), data_t[self.target]
        )[0]

        # # now we will take one component and then we calculate mean, median, min, max and sd of that one component grouped by the catagorical levels
        self.ph_data = []
        self.ph_clusters = []
        for i in self.feature:
            data_t1 = pd.DataFrame(
                dict(levels=data[i], comp1=data_pls[:, 0], comp2=data_pls[:, 1]),
                index=data.index,
            )
            # now group by feature
            data_t1 = data_t1.groupby("levels")
            data_t1 = data_t1[["comp1", "comp2"]].agg(
                ["mean", "median", "min", "max", "std"]
            )  # this gives us a df with only numeric columns (min , max ) and level as index
            # some time if a level has only one record  its std will come up as NaN, so convert NaN to 1
            data_t1.fillna(1, inplace=True)

            # now number of clusters cant be more than the number of samples in aggregated data , so
            self.check_clusters = min(self.check_clusters, len(data_t1))

            # # we are goign to make a place holder , for 2 to 20 clusters
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
                    random_state=self.random,
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
            self.ph_clusters.append(self.ph)
            # Now make the final cluster object
            self.k_object = cluster.KMeans(
                n_clusters=self.clusters,
                init="k-means++",
                precompute_distances="auto",
                n_init=10,
                random_state=self.random,
            )
            # now do fit predict
            predict = self.k_object.fit_predict(data_t1)
            # put it back with the group by aggregate columns
            data_t1["cluster"] = predict
            data_t1["cluster"] = data_t1["cluster"].apply(str)
            # now we dont need all the columns, only the cluster column is required along with the index (index also has a name , we  groupy as "levels")
            data_t1 = data_t1[["cluster"]]
            # now convert index ot the column
            data_t1.reset_index(
                level=0, inplace=True
            )  # this table now only contains every level and its cluster
            # self.data_t1= data_t1
            # we can now replace cluster with the original level in the original data frame
            data[i] = data[i].replace(list(data_t1["levels"]), data_t1["cluster"])
            self.ph_data.append(data_t1)

        if self.target in dataset.columns:
            data[self.target] = dataset[self.target]
        return data


# ____________________________________________________________________________________________________________________________________________
# Clustering catagorical data
class Reduce_Cardinality_with_Counts(Component):
    """
    - Reduces the level of catagorical column by replacing levels with their count & converting objects into float
      Args:
          catagorical_feature: list of features on which clustering is to be applied
  """

    def __init__(self, catagorical_feature=[]):
        super().__init__()
        self.feature = catagorical_feature

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        # we already know level counts
        for i, z, k in zip(self.feature, self.ph_data, self.ph_u):
            data[i] = data[i].replace(k, z["counts"])
            data[i] = data[i].astype("float32")

        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        #
        self.ph_data = []
        self.ph_u = []
        for i in self.feature:
            data_t1 = pd.DataFrame(
                dict(
                    levels=data[i].groupby(data[i], sort=False).count().index,
                    counts=data[i].groupby(data[i], sort=False).count().values,
                )
            )
            u = data[i].unique()
            # replace levels with counts
            data[i].replace(u, data_t1["counts"], inplace=True)
            data[i] = data[i].astype("float32")
            self.ph_data.append(data_t1)
            self.ph_u.append(u)

        return data


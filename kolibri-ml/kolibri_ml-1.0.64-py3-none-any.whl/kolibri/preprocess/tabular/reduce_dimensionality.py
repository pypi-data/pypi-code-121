from kolibri.core.component import Component
import numpy as np
import pandas as pd
from sklearn.decomposition import KernelPCA

class DimensionalityReduction(Component):
    """
    - Takes DF, return same DF with different types of dimensionality reduction modles (pca_liner , pca_kernal, tsne , pls, incremental)
    - except pca_liner, every other method takes integer as number of components
    - only takes numeric variables (float & One Hot Encoded)
    - it is intended to solve supervised ML usecases , such as classification / regression
  """
    defaults = {
        "fixed":{

               "pca-method" : "pca_linear",
                "pca-components" : 0.99
        }
    }
    def __init__(self, configs):
        super().__init__(configs)
        self.target = self.get_parameter("target")
        self.variance_retained = self.get_parameter("pca-components")
        self.random_state = self.get_parameter("random-state")
        self.method = self.get_parameter("pca-method")

    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):
        data = dataset
        if self.method in [
            "pca_liner",
            "pca_kernal",
            "tsne",
            "incremental",
        ]:  # if self.method in ['pca_liner' , 'pca_kernal', 'tsne' , 'incremental','psa']
            data = data.drop(self.target, axis=1, errors="ignore")
            data_pca = self.pca.transform(data)
            data_pca = pd.DataFrame(data_pca)
            data_pca.columns = [
                "Component_" + str(i) for i in np.arange(1, len(data_pca.columns) + 1)
            ]
            data_pca.index = data.index
            if self.target in dataset.columns:
                data_pca[self.target] = dataset[self.target]
            return data_pca
        else:
            return dataset

    def fit_transform(self, dataset, y=None):
        data = dataset
        if self.method == "pca_liner":
            self.pca = PCA(self.variance_retained, random_state=self.random_state)
            # fit transform
            data_pca = self.pca.fit_transform(data.drop(self.target, axis=1))
            data_pca = pd.DataFrame(data_pca)
            data_pca.columns = [
                "Component_" + str(i) for i in np.arange(1, len(data_pca.columns) + 1)
            ]
            data_pca.index = data.index
            data_pca[self.target] = data[self.target]
            return data_pca
        elif self.method == "pca_kernal":  # take number of components only
            self.pca = KernelPCA(
                self.variance_retained,
                kernel="rbf",
                random_state=self.random_state,
                n_jobs=-1,
            )
            # fit transform
            data_pca = self.pca.fit_transform(data.drop(self.target, axis=1))
            data_pca = pd.DataFrame(data_pca)
            data_pca.columns = [
                "Component_" + str(i) for i in np.arange(1, len(data_pca.columns) + 1)
            ]
            data_pca.index = data.index
            data_pca[self.target] = data[self.target]
            return data_pca
        # elif self.method == 'pls': # take number of components only
        #   self.pca = PLSRegression(self.variance_retained,scale=False)
        #   # fit transform
        #   data_pca = self.pca.fit_transform(data.drop(self.target,axis=1),data[self.target])[0]
        #   data_pca = dsk.DataFrame(data_pca)
        #   data_pca.columns = ["Component_"+str(i) for i in np.arange(1,len(data_pca.columns)+1)]
        #   data_pca.index = data.index
        #   data_pca[self.target] = data[self.target]
        #   return(data_pca)
        elif self.method == "tsne":  # take number of components only
            self.pca = TSNE(self.variance_retained, random_state=self.random_state)
            # fit transform
            data_pca = self.pca.fit_transform(data.drop(self.target, axis=1))
            data_pca = pd.DataFrame(data_pca)
            data_pca.columns = [
                "Component_" + str(i) for i in np.arange(1, len(data_pca.columns) + 1)
            ]
            data_pca.index = data.index
            data_pca[self.target] = data[self.target]
            return data_pca
        elif self.method == "incremental":  # take number of components only
            self.pca = IncrementalPCA(self.variance_retained)
            # fit transform
            data_pca = self.pca.fit_transform(data.drop(self.target, axis=1))
            data_pca = pd.DataFrame(data_pca)
            data_pca.columns = [
                "Component_" + str(i) for i in np.arange(1, len(data_pca.columns) + 1)
            ]
            data_pca.index = data.index
            data_pca[self.target] = data[self.target]
            return data_pca
        else:
            return dataset
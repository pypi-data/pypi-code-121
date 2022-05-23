from kolibri.core.component import Component
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import RobustScaler
from kolibri.utils.log_normalizer import LogNormaliser
import pandas as pd
import numpy as np




class Normalizer(Component):
    defaults = {
        "fixed":{
            "normalization-method": "zscore",
            "random-state-quantile":42,
            "ignore-columns":[],
            "include-columns":[],
            "table-index": [],
            "columns":[]
        }
    }

    def __init__(self, configs={}):

        super().__init__(configs)
        self.normalizer_funct = self.get_parameter("normalization-method")
        self.random_state_quantile = self.get_parameter("random-state-quantile")
        self._log_offset=100


    def fit(self, data, y=None):

        # we only want to apply if there are numeric columns
        self.numeric_features = (
            data.select_dtypes(include=["float32", "int64", "float64", "int32"]).columns
        )
        self.numeric_features=[col for col in self.numeric_features if (col not in self.get_parameter("ignore-columns") and col in self.get_parameter("include-columns"))]

        if len(self.numeric_features) > 0:
            if self.normalizer_funct == "zscore":
                self.scaler = StandardScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "minmax":
                self.scaler = MinMaxScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "quantile":
                self.scaler = QuantileTransformer(
                    random_state=self.random_state_quantile,
                    output_distribution="normal"
                )
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "maxabs":
                self.scaler = MaxAbsScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "robust":
                self.scaler = RobustScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "log10":
                self.scaler = LogNormaliser()
                self.scaler.fit(data[self.numeric_features])


        return self




    def transform(self, data, y=None):

        if len(self.numeric_features) > 0:
            self.data_t = pd.DataFrame(
                self.scaler.transform(data[self.numeric_features])
            )
            # we need to set the same index as original data
            self.data_t.index = data.index
            self.data_t.columns = self.numeric_features
            for i in self.numeric_features:
                data[i] = self.data_t[i]
            return data

        else:
            return data

    def fit_transform(self, data, y=None):
        self.fit(data)

        return self.transform(data)

    def inverse_transform(self, data):
        if len(self.numeric_features) > 0:
            self.data_t = pd.DataFrame(
                self.scaler.inverse_transform(data[self.numeric_features])
            )
            # we need to set the same index as original data
            self.data_t.index = data.index
            self.data_t.columns = self.numeric_features
            for i in self.numeric_features:
                data[i] = self.data_t[i]
            return data

        else:
            return data


    def inverse_transform_col(self, data, colName):
        dummy = pd.DataFrame(np.zeros((len(data), len(self.numeric_features))), columns=self.numeric_features)
        dummy[colName] = data
        dummy = pd.DataFrame(self.inverse_transform(dummy), columns=self.numeric_features)
        return dummy[colName].values
from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(Normalizer.name, Normalizer)
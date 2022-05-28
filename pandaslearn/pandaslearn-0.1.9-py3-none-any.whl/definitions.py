from sklearn.impute import MissingIndicator  # IterativeImputer
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    OneHotEncoder,
    OrdinalEncoder,
    RobustScaler,
    StandardScaler,
)

all_imputers = {
    "SimpleImputer": SimpleImputer,
    # "IterativeImputer": IterativeImputer,
    "MissingIndicator": MissingIndicator,
    "KNNImputer": KNNImputer,
}

all_normalizers = {
    "StandardScaler": StandardScaler,
    "MaxAbsScaler": MaxAbsScaler,
    "MinMaxScaler": MinMaxScaler,
    "RobustScaler": RobustScaler,
}

all_encoders = {
    "OneHotEncoder": OneHotEncoder,
    "OrdinalEncoder": OrdinalEncoder,
}
